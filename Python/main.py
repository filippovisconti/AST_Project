import argparse
import signal
from time import sleep

import docker.models.containers

from doc_page_parser import generate_json
from docker_utilities import *

signal_file = f'specs/inverse_lock'


def generate_playbooks(module_name: str, containers: list[docker.models.containers.Container], num_tests: int) -> None:
    if len(containers) > 0 and containers:
        logging.info("Generating random tasks")
        specs_file_path = f'/root/specs/{module_name}_specification.json'
        command = f'python3 /root/specs/main_generator.py -s {specs_file_path}' \
                  f' -m {module_name} -n {num_tests} --hosts all'

        exec_run_wrapper(containers[0], command)


def try_lock():
    tries = 5
    while not os.path.exists(signal_file) and tries > 0:
        logging.info("Waiting for signal file")
        sleep(1)
        tries -= 1

    if tries <= 0:
        logging.info("Signal file not found. Aborting...")
        exit(1)

    logging.info(f"Signal file found ({os.path.exists(signal_file)}). Running playbook...")


def free_lock():
    try:
        os.remove(signal_file)
    except FileNotFoundError:
        pass


def run_on_module(module_name: str, cnc_machine: docker.models.containers.Container = None,
                  containers: list[docker.models.containers.Container] = None, num_tests: int = 15,
                  create_spec: bool = False, integration_file=None):
    if create_spec or not os.path.exists(f'specs/{module_name}_specification.json'):
        logging.info(f'Generating json specification for {module_name}')
        generate_json(builtin_module_name=module_name, dest_dir='specs')
    else:
        logging.info(f'Using existing json specification for {module_name}')

    generate_playbooks(module_name=module_name, containers=containers, num_tests=num_tests)

    try_lock()

    results = {}
    for playbook_name in os.listdir('ansible/fuzzed_playbooks'):
        playbook_path = f'fuzzed_playbooks/{playbook_name}'
        logging.info(f'Running playbook {playbook_path}')

        # run setup playbook
        if integration_file:
            # run setup playbook
            pass

        exit_code = run_ansible_playbook(playbook_path=playbook_path, cnc=cnc_machine)

        if exit_code in results:
            results[exit_code] += 1
        else:
            results[exit_code] = 1

        logging.info(f"Playbook {playbook_path} finished with exit code {exit_code}")

        containers = reset_containers(containers)

    free_lock()

    return results


def print_results(results: dict):
    for key, value in results.items():
        if key == 0:
            print(f"PASS           - Count: {value}")
        elif key == -1:
            print(f"MODULE FAILURE - Count: {value}")
        elif key == -2:
            print(f"SET ATTR ERROR - Count: {value}")
        else:
            print(f"EXIT CODE: {key},   Count: {value}")


def main():
    # Call create_containers function
    signal.signal(signal.SIGINT, delete_containers_and_network)

    parser = argparse.ArgumentParser(description='Fuzzer for Ansible modules')
    parser.add_argument('-m', '--module_name', type=str, help='Name of the Ansible module', default='lineinfile')
    parser.add_argument('-n', '--num_tests', type=int, help='Number of fuzzed playbooks to generate', default='15')
    parser.add_argument('-s', '--create_spec', action="store_true", help='If set, creates specification file')
    parser.add_argument('-i', '--integration_file', type=str, help='If set, uses the given integration file',
                        default=None)
    args = parser.parse_args()

    logging.info(f"Running fuzzer with parameters {args}")
    try:
        containers, cnc_machine = setup_infrastructure()
        module_name = args.module_name

        results = run_on_module(module_name=module_name, cnc_machine=cnc_machine, containers=containers,
                                num_tests=args.num_tests, create_spec=args.create_spec,
                                integration_file=args.integration_file)

        print_results(results)

    except Exception as e:
        logging.info(e)
        logging.exception("Exception occurred.")

    logging.info("Cleaning up...")
    delete_containers_and_network()


if __name__ == '__main__':
    main()

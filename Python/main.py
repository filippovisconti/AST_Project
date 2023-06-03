import argparse
import signal
import logging
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

        if integration_file:
            setup_file = f'ansible/setup_playbooks/{integration_file}'
        else:
            setup_file = f'ansible/setup_playbooks/{module_name}_setup.yml'

        if os.path.exists(setup_file):
            logging.info(f'Running setup playbook {setup_file}')
            run_ansible_playbook(playbook_path=setup_file, cnc=cnc_machine)

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


results: dict = {}


def kill_wrapper(signal=None, frame=None):
    print_results()
    try:
        delete_containers_and_network()
    except Exception as e:
        logging.exception(e)


def check_before_run():
    if not os.path.exists('specs'):
        raise Exception("No specs folder found.")

    if not os.path.exists('ansible/fuzzed_playbooks'):
        # create folder
        os.mkdir('ansible/fuzzed_playbooks')

    if not os.path.exists('ansible/setup_playbooks'):
        # create folder
        os.mkdir('ansible/setup_playbooks')

    if not os.path.exists('ansible/keys'):
        os.mkdir('ansible/keys')
        raise Exception("No keys folder found. Please create one and place your public key in it.")

    if not os.path.exists('ansible/keys/authorized_keys'):
        raise Exception("No key found. Please place your public key in ansible/keys/authorized_keys.")

    if not os.path.exists('ansible/ansible.cfg'):
        raise Exception("No ansible.cfg file found. Please place one in the ansible folder. " +
                        "NOTE: include host_key_checking = False            in the file.")

    if not os.path.exists('ansible/inventory.ini'):
        raise Exception("No inventory.ini file found. Please place one in the ansible folder.")

    if not os.path.exists('ansible/sshd_config.d/ansible.conf'):
        raise Exception("No ansible.conf file found. Please place one in the ansible/sshd_config.d folder.")


def main():

    signal.signal(signal.SIGINT, kill_wrapper)

    parser = argparse.ArgumentParser(description='Fuzzer for Ansible modules')
    parser.add_argument('-m', '--module_name', type=str, help='Name of the Ansible module', default='lineinfile',
                        required=True)
    parser.add_argument('-n', '--num_tests', type=int, help='Number of fuzzed playbooks to generate', default='15',
                        required=True)
    parser.add_argument('-s', '--create_spec', action="store_true", help='If set, creates specification file',
                        required=False)
    parser.add_argument('-i', '--integration_file', type=str,
                        help='If set, uses the given integration file - which HAS to be placed' +
                             'inside the ansible/setup_playbooks folder',
                        default=None, required=False)
    parser.add_argument('-v', '--verbose', action="store_true", help='If set, sets log level to DEBUG',
                        required=False)
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
        logging.debug("Verbose logging activated.")
    else:
        logging.basicConfig(level=logging.INFO)
    # Call create_containers function
    try:
        check_before_run()
    except Exception as e:
        logging.exception(e)
        exit(1)

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

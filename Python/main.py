import signal
from time import sleep

import docker.models.containers

from doc_page_parser import generate_json
from docker_utilities import *


def run_on_module(module_name: str, cnc_machine: docker.models.containers.Container = None,
                  containers: list[docker.models.containers.Container] = None):
    logging.info(f'Generating json specification for {module_name}')
    generate_json(builtin_module_name=module_name, dest_dir='specs')

    if len(containers) > 0:
        logging.info("Generating random tasks")
        specs_file_path = f'/root/specs/{module_name}_specification.json'
        exec_run_wrapper(containers[0],
                         f'python3 /root/specs/main_generator.py -s {specs_file_path} -m{module_name} --hosts all')

    signal_file = f'specs/inverse_lock'
    while not os.path.exists(signal_file):
        logging.info("Waiting for signal file")
        sleep(1)

    for playbook_name in os.listdir('ansible/fuzzed_playbooks'):
        playbook_path = f'fuzzed_playbooks/{playbook_name}'
        logging.info(f'Running playbook {playbook_path}')
        # run_ansible_playbook(playbook_path=playbook_path)

    # reset_containers(containers)
    os.remove(signal_file)


def main():
    # Call create_containers function
    signal.signal(signal.SIGINT, delete_containers_and_network)

    try:
        containers, cnc_machine = setup_infrastructure()

        module_name = 'lineinfile'
        run_on_module(module_name=module_name, cnc_machine=cnc_machine, containers=containers)

        # module_name = 'git'
        # run_on_module(module_name)


    except Exception as e:
        logging.info(e)
        logging.exception("Exception occurred. Cleaning up...")
        # TODO: Remove containers and network

        delete_containers_and_network()


if __name__ == '__main__':
    main()

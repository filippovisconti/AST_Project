from doc_page_parser import generate_json
from docker_utilities import *
from models import create_task_from_spec_default, AnsibleModuleSpecification, Ansible_Playbook


def main():
    # Call create_containers function
    try:
        containers, cnc_machine = setup_infrastructure()
        """
        playbook_path = 'test_playbook.yaml'
        run_ansible_playbook(playbook_path=playbook_path)

        reset_containers(containers)
        run_ansible_playbook(playbook_path=playbook_path)
        """
        module_name = 'lineinfile'
        logging.info(f'Generating json specification for {module_name}')

        generate_json(module_name)
        module_spec = AnsibleModuleSpecification.from_json(f'json/{module_name}_specification.json')

        logging.info(f'Creating default task for {module_name}')
        default_task = create_task_from_spec_default(module_spec)

        hosts = 'all'
        logging.info(f'Creating playbook for {module_name}\n\ton hosts: {hosts}')

        playbook = Ansible_Playbook(f'Testing {module_name}', hosts, [default_task])
        playbook_path = f'fuzzed_playbooks/{module_name}_default.yaml'

        logging.info(f'Writing playbook to {playbook_path}')
        playbook.to_yaml(file_path=f'ansible/{playbook_path}')

        logging.info(f'Running playbook {playbook_path}')
        run_ansible_playbook(playbook_path=playbook_path)


    except Exception as e:
        logging.info(e)
        logging.exception("Exception occurred. Cleaning up...")
        # TODO: Remove containers and network

    delete_containers_and_network()


if __name__ == '__main__':
    main()

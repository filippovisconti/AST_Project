from docker_utilities import *


def main():
    # Call create_containers function
    try:
        containers, cnc_machine = setup_infrastructure()

        playbook_path = 'test_playbook.yaml'
        run_ansible_playbook(playbook_path=playbook_path)

        reset_containers(containers)
        run_ansible_playbook(playbook_path=playbook_path)

    except Exception:
        logging.exception("Exception occurred. Cleaning up...")
        # TODO: Remove containers and network

    delete_containers_and_network()


if __name__ == '__main__':
    main()

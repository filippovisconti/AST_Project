from docker_utilities import *


def main():
    # Call create_containers function
    try:
        create_network()
        build_ansible_image()
        build_debian_image()
        containers = create_containers()
        create_cnc_machine()

        playbook_path = 'test_playbook.yaml'
        run_ansible_playbook(playbook_path=playbook_path)

        reset_containers(containers)
        run_ansible_playbook(playbook_path=playbook_path)

    except Exception:
        logging.exception("Exception occurred. Cleaning up...")
        # TODO: Remove containers and network
    delete_containers()


if __name__ == '__main__':
    main()

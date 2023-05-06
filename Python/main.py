from time import sleep

from docker_utilities import *


def main():
    # Call create_containers function
    try:
        create_network()
        build_ansible_image()
        build_debian_image()
        containers = create_containers()
        create_cnc_machine()

        # Wait for user input
        logging.info("Running Ansible playbook...")
        res = client.containers.get('cnc_machine').exec_run(
            'ansible-playbook -i /root/ansible/inventory.ini /root/ansible/test_playbook.yaml'
        )
        # > /root/ansible/output.txt'

        #sleep(10)
        if res.exit_code == 0:
            logging.info("Ansible playbook executed successfully")
            logging.info(res.output.decode('utf-8'))
        else:
            logging.error(f"Ansible playbook failed - code {res.exit_code}")
            logging.error(res.output.decode('utf-8'))

    except Exception:
        logging.exception("Exception occurred. Cleaning up...")
        # TODO: Remove containers and network
    delete_containers()


if __name__ == '__main__':
    main()

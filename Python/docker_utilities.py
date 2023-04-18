import os
import pprint
from click import pause
import docker, logging

logging.basicConfig(level=logging.INFO)

logging.info("Create Docker client")
client = docker.from_env()
logging.info("Created Docker client")

# Define network settings
subnet = '10.10.10.0/24'
gateway_ip = '10.10.10.1'
network_name = 'ansible_network'

# Define container settings
image_name = 'debian'
container_count = 3
platform = 'linux/arm64'
start_command = 'tail -f /dev/null'
cwd = os.getcwd()


def create_network():
    # Create network
    networks = client.networks.list(names=[network_name])
    if not networks:

        ipam_pool = docker.types.IPAMPool(subnet=subnet,
                                          iprange=subnet,
                                          gateway=gateway_ip)

        ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])
        client.networks.create(network_name, driver='bridge', ipam=ipam_config)
        logging.info("Created network")
    else:
        logging.info("Network already exists")


def build_ansible_image():
    # Build image
    client.images.build(path='.',
                        dockerfile='Dockerfile',
                        tag='my-ansible-runner')


def create_cnc_macine():
    # Create containers

    container_name = f'cnc_machine'
    container = client.containers.create('my-ansible-runner',
                                         name=container_name,
                                         network=network_name,
                                         platform=platform,
                                         command=start_command,
                                         volumes={
                                             f'{cwd}/ansible': {
                                                 'bind': '/root/ansible',
                                                 'mode': 'rw'
                                             },
                                             f'{cwd}/ansible/ansible.cfg': {
                                                 'bind': '/root/.ansible.cfg',
                                                 'mode': 'rw'
                                             }
                                         },
                                         detach=True,
                                         dns=['8.8.8.8', '8.8.4.4'])

    logging.info(f'Created container {container_name}')

    container.start()
    container.reload()

    command = 'chmod 600 /root/ansible/ansible_ed25519'
    container.exec_run(command)

    logging.info(
        f'Started container {container_name} with IP address {container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]}'
    )

    # res = container.exec_run(
    #     'ansible-playbook -i /root/ansible/inventory.ini /root/ansible/test_playbook.yaml'  # > /root/ansible/output.txt'
    # )
    # print(res)


# apt update && apt install net-tools && ifconfig
# ansible-playbook -i inventory.ini test_playbook.yaml
# chmod 600 ansible_ed25519
# Create function to create containers
def create_containers():
    # Create containers
    for i in range(container_count):
        container_name = f'container_{i+2}'
        container = client.containers.create(
            image_name,
            name=container_name,
            network=network_name,
            platform=platform,
            command=start_command,
            volumes={
                f'{cwd}/ansible/keys': {
                    'bind': '/root/.ssh/',
                    'mode': 'rw'
                },
                f'{cwd}/ansible/sshd_config.d': {
                    'bind': '/etc/ssh/sshd_config.d/',
                    'mode': 'rw'
                }
            },
            detach=True,
            dns=['8.8.8.8', '8.8.4.4'])

        logging.info(f'Created container {container_name}')

        container.start()
        container.reload()
        logging.info(
            f'Started container {container_name} with IP address {container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]}'
        )
        command = 'apt update'
        res = container.exec_run(command)
        command = 'apt install net-tools openssh-server python3 sudo -y'
        res = container.exec_run(command)
        command = 'service ssh start'
        res = container.exec_run(command)
        command = 'passwd -d root'
        res = container.exec_run(command)

        logging.info(f'Executed command on container {container_name}')


def delete_containers():
    # Remove containers
    for container in client.containers.list():
        # container.stop()
        container.remove(force=True)
        logging.info(f"Removed container {container.name}")

    # Remove network
    client.networks.get(network_name).remove()
    logging.info("Removed network")


def main():
    # Call create_containers function
    try:
        create_network()
        build_ansible_image()
        create_containers()
        create_cnc_macine()

        # Wait for user input
        # pause()
        res = client.containers.get('cnc_machine').exec_run(
            'ansible-playbook -i /root/ansible/inventory.ini /root/ansible/test_playbook.yaml'  # > /root/ansible/output.txt'
        )
        if res.exit_code == 0:
            logging.info("Ansible playbook executed successfully")
        else:
            logging.error(f"Ansible playbook failed - code {res.exit_code}")
            logging.error(res.output.decode('utf-8'))

    except:
        logging.exception("Exception occurred. Cleaning up...")
        # TODO: Remove containers and network
    delete_containers()


if __name__ == '__main__':
    main()
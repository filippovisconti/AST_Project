import logging
import os
import platform

import docker

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
image_name_cnc = 'alpine'
container_count = 3
if platform.machine() == 'arm64':
    platform = 'linux/arm64'
else:
    platform = 'linux/amd64'

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
    if not client.images.list(name=image_name_cnc):
        logging.info(f"Pulling {image_name_cnc} image...")
        client.images.pull(image_name_cnc, platform=platform)
        logging.info(f"Pulled {image_name_cnc}image")
    else:
        logging.info(f"{image_name_cnc} image already exists")

    client.images.build(path='.',
                        dockerfile='Dockerfile-ansible-runner',
                        tag='my-ansible-runner')
    logging.info("Built ansible-runner image")


def build_debian_image():
    # Build image
    if not client.images.list(name=image_name):
        logging.info(f"Pulling {image_name} image...")
        client.images.pull(image_name, platform=platform)
        logging.info(f"Pulled {image_name} image")
    else:
        logging.info(f"{image_name} image already exists")
    client.images.build(path='.',
                        dockerfile='Dockerfile-debian',
                        tag='my-debian')
    logging.info(f"Built {image_name} image")


def create_cnc_machine() -> docker.models.containers.Container:
    # Create containers

    container_name = f'cnc_machine'
    container = client.containers.create(image='my-ansible-runner',
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
        f'Started container {container_name} ' +
        f'with IP address {container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]}'
    )
    return container


def create_containers() -> list[docker.models.containers.Container]:
    # Create containers
    containers = []
    for i in range(container_count):
        container_name = f'container_{i + 2}'
        container = client.containers.create(
            image=f'my-debian',
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
            f'Started container {container_name} ' +
            f'with IP address {container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]}'
        )
        # command: str = 'apt update'
        # container.exec_run(command)

        # command = 'apt install net-tools openssh-server python3 sudo -y'
        # container.exec_run(command)

        command = 'service ssh start'
        container.exec_run(command)

        logging.info(f'Executed commands on container {container_name}')
        containers.append(container)

    return containers


def reset_containers(containers: list[docker.models.containers.Container]):
    logging.info(f'Restarting containers...')
    for cont in containers:
        cont.restart()
        cont.exec_run('service ssh start')
        logging.info(f'Restarted container {cont.name}')


def delete_containers_and_network():
    # Remove containers
    for container in client.containers.list():
        # container.stop()
        container.remove(force=True)
        logging.info(f"Removed container {container.name}")

    # Remove network
    client.networks.get(network_name).remove()
    logging.info("Removed network")


def run_ansible_playbook(playbook_path: str) -> int:
    logging.info("Running Ansible playbook...")
    res = client.containers.get('cnc_machine').exec_run(
        f'ansible-playbook -i /root/ansible/inventory.ini /root/ansible/{playbook_path}'
    )

    if res.exit_code == 0:
        logging.info("Ansible playbook executed successfully")
        logging.info(res.output.decode('utf-8'))
    else:
        logging.error(f"Ansible playbook failed - code {res.exit_code}")
        logging.error(res.output.decode('utf-8'))

    return res.exit_code


def setup_infrastructure():
    create_network()
    build_ansible_image()
    build_debian_image()
    containers = create_containers()
    cnc_machine = create_cnc_machine()

    return containers, cnc_machine


if __name__ == '__main__':
    pass

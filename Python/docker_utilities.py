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
                                         detach=True,
                                         dns=['8.8.8.8', '8.8.4.4'])

    logging.info(f'Created container {container_name}')

    container.start()
    container.reload()
    logging.info(
        f'Started container {container_name} with IP address {container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]}'
    )


# apt update && apt install net-tools && ifconfig
# Create function to create containers
def create_containers():
    # Create containers
    for i in range(container_count):
        container_name = f'container_{i+2}'
        container = client.containers.create(image_name,
                                             name=container_name,
                                             network=network_name,
                                             platform=platform,
                                             command=start_command,
                                             detach=True,
                                             dns=['8.8.8.8', '8.8.4.4'])

        logging.info(f'Created container {container_name}')

        container.start()
        container.reload()
        logging.info(
            f'Started container {container_name} with IP address {container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"]}'
        )


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
        create_cnc_macine()
        create_containers()
        # Wait for user input
        pause()

    except:
        logging.exception("Exception occurred. Cleaning up...")
        # TODO: Remove containers and network
    delete_containers()


if __name__ == '__main__':
    main()
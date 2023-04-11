import docker

subnet = '10.10.10.'

def main():
    client = docker.from_env()
    for i in range(1, 4):
        container_name = f'ubuntu_{i}'
        container_ip = subnet + str(i)

        container = client.containers.run('ubuntu:latest', detach=True, name=container_name, hostname=container_name, network='bridge', command='tail -f /dev/null')
        network_config = client.networks.get('bridge').attrs['IPAM']['Config']
        ipv4_address = network_config[0]['Gateway'].split('/')[0]
        client.networks.get('bridge').connect(container, ipv4_address=container_ip)

        print(f'{container_name} has IP address: {container_ip}')

    print('Done')

if __name__ == '__main__':
    main()


# Fuzzible

Ansible is a popular automation tool used for configuring and managing systems. Ansible modules play a crucial role in performing various tasks and operations within Ansible. However, ensuring the quality and reliability of these modules can be challenging, especially as the number of modules grows.

Fuzzible helps in this challenge by automating the testing process. It parses the official module documentation, generates random playbooks, and executes them within clean Docker containers. By doing so, it simulates real-world scenarios and challenges the functionality, stability, and reliability of the Ansible modules.

## Initial Setup

To use Fuzzible, you need to have Docker and DockerPy installed on your system. Follow the steps below to set up the necessary dependencies:

Install Docker: Refer to the official Docker documentation for instructions on how to install Docker for your operating system.

1. Install [DockerPy](https://github.com/docker/docker-py) to manage Docker containers from within Python scripts

    ```bash
    pip3 install docker
    ```

    Optionally, you can install it in a Python virtual environment.

2. Clone this repository
3. Make sure Docker is running
4. Run the `main.py` script

    ```bash
    python3 main.py [options]
    ```
    ```bash
    usage: main.py [-h] -m MODULE_NAME -n NUM_TESTS [-s] [-i INTEGRATION_FILE] [-v]

    Fuzzer for Ansible modules

    options:
    -h, --help              show this help message and exit
    
    -m MODULE_NAME, --module_name MODULE_NAME
                            Name of the Ansible module

    -n NUM_TESTS, --num_tests NUM_TESTS
                            Number of fuzzed playbooks to generate

    -i INTEGRATION_FILE, --integration_file INTEGRATION_FILE
                            If set, uses the given integration file - which HAS to be placed inside the ansible/setup_playbooks folder

    -s, --create_spec     If set, creates specification file

    -v, --verbose         If set, sets log level to DEBUG

    ```

## Other useful links

Run the following command to fix Docker Socket connection error on macOS

```bash
sudo ln -sf "$HOME/.docker/run/docker.sock" /var/run/docker.sock
```

[Containers — Docker SDK for Python 6.0.1 documentation](https://docker-py.readthedocs.io/en/stable/containers.html)

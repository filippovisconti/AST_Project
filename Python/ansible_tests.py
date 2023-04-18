from models import Ansible_Task
from doc_page_parser import parse_examples_yaml
from docker_utilities import *
from ansible.inventory.manager import InventoryManager
from ansible.module_utils.common.collections import ImmutableDict
from ansible.playbook.play import Play
from ansible.parsing.dataloader import DataLoader
from ansible.plugins.callback import CallbackBase
from ansible.vars.manager import VariableManager
from ansible.executor.playbook_executor import PlaybookExecutor



def run_ansible_playbook():
    # Define Ansible inventory
    inventory = InventoryManager(loader=DataLoader(), sources='localhost,')
    inventory.add_group('docker_containers')
    for container in client.containers.list():
        inventory.add_host(container.attrs["NetworkSettings"]["Networks"][network_name]["IPAddress"], group='docker_containers')

    # Define Ansible variables
    variable_manager = VariableManager(loader=DataLoader(), inventory=inventory)

    # Define Ansible playbook
    playbook_path = 'playbook.yml'
    play_source = dict(
        name="Install ping on Docker containers",
        hosts='docker_containers',
        gather_facts='no',
        tasks=[
            dict(name="Install ping", apt=dict(name="iputils-ping", state="latest"))
        ]
    )

    # Run Ansible playbook
    play = Play().load(play_source, variable_manager=variable_manager, loader=DataLoader())
    playbook = PlaybookExecutor(playbooks=[playbook_path], inventory=inventory, variable_manager=variable_manager, loader=DataLoader())
    playbook._tqm._stdout_callback = CallbackBase()
    playbook.run()

def main():
    filename = "lineinfile_examples.yaml"
    module_examples: dict = parse_examples_yaml(filename=filename)

    with open('test.yml', 'w') as file:
        for example in module_examples:
            task = Ansible_Task(example['name'], 'ansible.builtin.lineinfile',
                                example['ansible.builtin.lineinfile'])
            file.write(str(task))
            
if __name__ == '__main__':
    main()
from models import Ansible_Task
from doc_page_parser import parse_examples_yaml


def main():
    filename = "lineinfile_examples.yaml"
    module_examples: dict = parse_examples_yaml(filename=filename)

    with open('test.yml', 'w') as file:
        for example in module_examples:
            task = Ansible_Task(example['name'], 'ansible.builtin.lineinfile',
                                example['ansible.builtin.lineinfile'])
            file.write(str(task))

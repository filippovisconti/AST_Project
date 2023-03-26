from bs4 import BeautifulSoup
from models import Ansible_Task
import pandas as pd
import requests, pprint, yaml


def parse_ansible_doc(url: str, enable_prints=False) -> None:
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    attributes_table = soup.find('table')

    attributes_df: pd.DataFrame = pd.read_html(str(attributes_table))[0]

    attributes_df['Parameter'] = attributes_df['Parameter'].str.split().str[0]

    attributes_dictionary = dict(
        zip(attributes_df.iloc[:, 0], attributes_df.iloc[:, 1]))

    if (enable_prints):
        print(attributes_df)
        pprint.pprint(attributes_dictionary)

    return attributes_dictionary


def parse_examples_yaml(url: str = None,
                        filename: str = None,
                        enable_prints=False) -> None:
    if (url == None and filename == None):
        raise Exception("Either url or filename must be provided")

    if (url != None and filename != None):
        raise Exception("Only one of url or filename must be provided")

    if (url != None):
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        pre = soup.find('pre')

        yaml_dict = yaml.safe_load(pre.text)

    if (filename != None):
        with open(filename, 'r') as stream:
            yaml_dict = yaml.safe_load(stream)

    if (enable_prints):
        pprint.pprint(yaml_dict)

    return yaml_dict


def main() -> None:
    url = "https://docs.ansible.com/ansible/latest/collections/ansible/builtin/lineinfile_module.html"
    filename = "lineinfile_examples.yaml"
    attributes_dictionary: dict = parse_ansible_doc(url)
    module_examples: dict = parse_examples_yaml(filename=filename,
                                                enable_prints=True)

    task = Ansible_Task('test', 'ansible.builtin.lineinfile',
                        attributes_dictionary)
    print(task)
    with open('test.yml', 'w') as file:
        for example in module_examples:
            task = Ansible_Task(example['name'], 'ansible.builtin.lineinfile',
                                example['ansible.builtin.lineinfile'])
            file.write(str(task))
            print(task)


if __name__ == "__main__":
    main()
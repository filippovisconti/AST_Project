import pandas as pd
import pprint
import requests
import yaml
from bs4 import BeautifulSoup

from models import Ansible_Task


# This function takes a URL for an (Ansible documentation) page as input. It returns a dictionary where the keys are
# the attribute names and the values are the descriptions of those attributes.
def parse_ansible_doc(url: str, enable_prints=False) -> dict:
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    attributes_table = soup.find('table')

    attributes_df: pd.DataFrame = pd.read_html(str(attributes_table))[0]
    attributes_dictionary = dict(zip(attributes_df.iloc[:, 0], attributes_df.iloc[:, 1]))

    if enable_prints:
        print(attributes_df)
        pprint.pprint(attributes_dictionary)

    return attributes_dictionary


# This function takes a dict and returns a dict of plausible values for the attributes
def extract_attribute_values(attributes_dictionary: dict) -> dict:
    plausible_values_dict = {}
    for attribute, comment in attributes_dictionary.items():
        attribute_name = attribute.split()[0]
        if "Choices:" in comment:
            choices = comment.split("Choices: ")[1]  # Extract the choices substring
            choices_list = choices.split(' ')  # Split the choices substring into a list of individual values
            choices_list = [choice.strip('"') for choice in
                            choices_list]  # Remove any surrounding quotes from the values
            plausible_values = [elem for elem in choices_list if elem not in ['←', '(default)']]

            plausible_values_dict[attribute_name] = plausible_values
        else:
            plausible_values_dict[attribute_name] = None

    return plausible_values_dict


# This function takes a dict and returns a dict of default values for the attributes
def get_default_value(attributes_dictionary: dict) -> dict:
    default_values_dict = {}
    for attribute, comment in attributes_dictionary.items():
        attribute_name = attribute.split()[0]
        if "Choices:" in comment:
            if "Choices:" in comment:
                choices = comment.split("Choices: ")[1]
                default_separator = ' ← (default)'
                default_pos = choices.find(default_separator)
                if default_pos != -1:
                    default_value = choices.split(default_separator)[0]
                    default_value = default_value.split(' ')[-1]
            default_values_dict[attribute_name] = default_value
        else:
            default_values_dict[attribute_name] = None

    return default_values_dict


def parse_examples_yaml(url: str = None,
                        filename: str = None,
                        enable_prints: bool = False) -> dict:
    if url is None and filename is None:
        raise Exception("Either url or filename must be provided")

    if url is not None and filename is not None:
        raise Exception("Only one of url or filename must be provided")

    if url is not None:
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        pre = soup.find('pre')

        yaml_dict = yaml.safe_load(pre.text)

    if filename is not None:
        with open(filename, 'r') as stream:
            yaml_dict = yaml.safe_load(stream)

    if enable_prints:
        pprint.pprint(yaml_dict)

    return yaml_dict


def main() -> None:
    url = "https://docs.ansible.com/ansible/latest/collections/ansible/builtin/lineinfile_module.html"
    filename = "lineinfile_examples.yaml"
    attributes_values_dictionary: dict = parse_ansible_doc(url)
    plausible_values_dictionary: dict = extract_attribute_values(attributes_values_dictionary)
    default_values_dict: dict = get_default_value(attributes_values_dictionary)

    module_examples: dict = parse_examples_yaml(filename=filename)

    task = Ansible_Task('test', 'ansible.builtin.lineinfile',
                        attributes_values_dictionary)


if __name__ == "__main__":
    main()

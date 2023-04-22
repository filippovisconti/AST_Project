from bs4 import BeautifulSoup
from models import Ansible_Task
import pandas as pd
import requests, pprint, yaml
import re


# This function takes a URL for an (Ansible documentation) page as input
# It returns a dictionary where the keys are the attribute names and the values are the descriptions of those attributes.


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


# This function takes a description string and returns a list of plausible values for that attribute
def extract_attribute_values(description: str) -> list:
    # If no possible value indicators are found, look for specific keywords in the description
    if "boolean" in description.lower():
        return ["True", "False"]
    if "string" in description.lower():
        return ["string"]
    # If no keywords are found, return None
    return None


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
    attributes_dictionary: dict = parse_ansible_doc(url)
    for attributes, comments in attributes_dictionary.items():
        plausible_values = extract_attribute_values(attributes)
        attribute_name = attributes.split()[0]
        print(f"{attribute_name}: {plausible_values}")

    module_examples: dict = parse_examples_yaml(filename=filename)

    task = Ansible_Task('test', 'ansible.builtin.lineinfile',
                        attributes_dictionary)


if __name__ == "__main__":
    main()

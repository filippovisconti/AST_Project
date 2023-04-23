from bs4 import BeautifulSoup
from models import Ansible_Task
import pandas as pd
import requests, pprint, yaml


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

    plausible_values_dict = {}  # dict with attribute name as key and their plausible value as values
    for attribute, comment in attributes_dictionary.items():
        plausible_values = extract_attribute_values(attribute, comment)
        attribute_name = attribute.split()[0]
        plausible_values_dict[attribute_name] = plausible_values
        #print(f"{attribute_name}: {plausible_values}")
    # print(plausible_values_dict)

    return plausible_values_dict


# This function takes a description string and returns a list of plausible values for that attribute
def extract_attribute_values(description: str, comment: str) -> list:
    if "Choices:" in comment:
        choices_string = comment.split("Choices: ")[1]  # Extract the choices substring
        choices_list = choices_string.split(' ')  # Split the choices substring into a list of individual values

        choices_list = [choice.strip('"') for choice in choices_list]  # Remove any surrounding quotes from the values
        choices_list = [elem for elem in choices_list if elem not in ['←', '(default)']]
        return choices_list
    #get type of the description
    # if "boolean" in description.lower():
    #     return ["boolean"]
    # if "string" in description.lower():
    #     return ["string"]
    # if "any" in description.lower():
    #     return ["any"]
    # if "path" in description.lower():
    #     return ["path"]
    # if "int" in description.lower():
    #     return ["int"]
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
    attributes_values_dictionary: dict = parse_ansible_doc(url)

    module_examples: dict = parse_examples_yaml(filename=filename)

    task = Ansible_Task('test', 'ansible.builtin.lineinfile',
                        attributes_values_dictionary)


if __name__ == "__main__":
    main()

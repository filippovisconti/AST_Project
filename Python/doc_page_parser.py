import pandas as pd
import pprint
import requests
import yaml
from bs4 import BeautifulSoup

from models import Ansible_Task


# This function takes a URL page as input and returns the html of the page
def get_html_of_url(url: str) -> str:
    response = requests.get(url)
    html = response.text
    # extract_data(html)
    extract_attribute_specification(html)
    return html


# This function takes a URL for an (Ansible documentation) page as input. It returns a dictionary where the keys are
# the attribute names and the values are the descriptions of those attributes.
def parse_ansible_doc(url: str, enable_prints=False) -> dict:
    html = get_html_of_url(url)

    soup = BeautifulSoup(html, 'html.parser')
    attributes_table = soup.find('table')
    with open("ansible_lininfile.html", "w") as file:
        # Write the HTML content to the file
        file.write(attributes_table.prettify())

    attributes_df: pd.DataFrame = pd.read_html(str(attributes_table))[0]
    attributes_dictionary = dict(zip(attributes_df.iloc[:, 0], attributes_df.iloc[:, 1]))

    if enable_prints:
        print(attributes_df)
        pprint.pprint(attributes_dictionary)
    return attributes_dictionary


# This function takes a dict and returns a dict of plausible values for the attributes
def get_plausible_values(attributes_dictionary: dict) -> dict:
    plausible_values_dict = {}
    for parameter, comment in attributes_dictionary.items():
        attribute_name = parameter.split()[0]
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
    for parameter, comment in attributes_dictionary.items():
        attribute_name = parameter.split()[0]
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


# This function takes a dict and returns a dict of value types for the attributes
def get_value_types(attributes_dictionary: dict) -> dict:
    valuetypes_dict = {}
    for attribute, comment in attributes_dictionary.items():
        attribute_name = attribute.split()[0]
        if "string" in attribute:
            valuetypes_dict[attribute_name] = "string"
        elif "boolean" in attribute:
            valuetypes_dict[attribute_name] = "boolean"
        elif "int" in attribute:
            valuetypes_dict[attribute_name] = "int"
        elif "float" in attribute:
            valuetypes_dict[attribute_name] = "float"
        elif "double" in attribute:
            valuetypes_dict[attribute_name] = "double"
        elif "path" in attribute:
            valuetypes_dict[attribute_name] = "path"
        elif "any" in attribute:
            valuetypes_dict[attribute_name] = "any"
        else:
            valuetypes_dict[attribute_name] = None
    return valuetypes_dict


# This function takes a dict and returns a dict of attribute version
def get_attribute_version(attributes_dictionary: dict) -> dict:
    attribute_version_dict = {}
    for attribute, comment in attributes_dictionary.items():
        attribute_name = attribute.split()[0]
        attribute_version = None
        if "added in" in attribute:
            parts = attribute.split(' ')

            for i in range(len(attribute_name) - 3):
                if parts[i] == 'added' and parts[i + 1] == 'in':
                    attribute_version = f"{parts[i + 2]} {parts[i + 3]}"
                    break
        attribute_version_dict[attribute_name] = attribute_version
    return attribute_version_dict


# TODO get more module specification from html by using class and id
def extract_data(soup):
    data = {}
    try:
        data['name'] = soup.select_one('.ansible-option-title strong').text
    except AttributeError:
        data['name'] = None

    try:
        data['aliases'] = soup.select_one('.ansible-option-aliases').text.split(': ')[1]
    except AttributeError:
        data['aliases'] = None

    try:
        data['type'] = soup.select_one('.ansible-option-type').text
    except AttributeError:
        data['type'] = None

    try:
        data['version_added'] = soup.select_one('.ansible-option-versionadded').text.split()[2] + " " + \
                                soup.select_one('.ansible-option-versionadded').text.split()[3]
    except AttributeError:
        data['version_added'] = None

    try:
        # TODO bug fix, not getting the text descripton, getting name instead
        # data['description'] = soup.select_one('.ansible-option-cell p').text.strip()
        data['description'] = soup.select_one('.ansible-option-cell p:nth-of-type(1)').text
    except:
        data['description'] = None

    # paragraphs = soup.find_all('p')
    # print(paragraphs)
    # data_p = {}
    # for p in paragraphs:
    #   code = p.find('code')
    # data['paragraph'] = data_p
    return data


# TODO save it in a dict an add it correctly to the specifiation dict
def extract_attribute_specification(html):
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find('table')
    cell = soup.find_all('tr')

    data = {}
    for attribute_class in cell:
        # print(attribute_class)
        result = extract_data(attribute_class)
        print(result)
    return data


# create dictionary of dictionaries
def get_attribute_specifications(attributes_dictionary):
    attribute_specifications_dict = {}
    plausible_values_dictionary: dict = get_plausible_values(attributes_dictionary)
    default_values_dict: dict = get_default_value(attributes_dictionary)
    attributes_value_types_dict: dict = get_value_types(attributes_dictionary)
    attributes_version_dict: dict = get_attribute_version(attributes_dictionary)

    for attribute, comment in attributes_dictionary.items():
        attribute_name = attribute.split()[0]
        specification_dict = {
            "value type": attributes_value_types_dict.get(attribute_name),
            "version": attributes_version_dict.get(attribute_name),
            "plausible values": plausible_values_dictionary.get(attribute_name),
            "default value": default_values_dict.get(attribute_name),
            "comment": comment
        }
        attribute_specifications_dict[attribute_name] = specification_dict
        # print(f"{attribute_name}: {specification_dict}")
    return attribute_specifications_dict


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
    attributes_specification_dict: dict = get_attribute_specifications(attributes_values_dictionary)

    module_examples: dict = parse_examples_yaml(filename=filename)

    task = Ansible_Task('test', 'ansible.builtin.lineinfile',
                        attributes_values_dictionary)


if __name__ == "__main__":
    main()

import pandas as pd
import pprint
import requests
import yaml
import json
from bs4 import BeautifulSoup

from models import Ansible_Task


# TODO clean code: delete unnecessary things
# TODO create json file
# This function takes a URL page as input and returns the html of the page
def get_html_of_url(url: str) -> str:
    response = requests.get(url)
    html = response.text
    return html


def extract_attribute_data(table_html):
    data = {}

    try:
        name = table_html.select_one('.ansible-option-title strong').text
        data['name'] = name
    except AttributeError:
        data['name'] = None

    try:
        data['type'] = table_html.select_one('.ansible-option-type').text
    except AttributeError:
        data['type'] = None

    try:
        if table_html.select_one('.ansible-option-required').text is not None:
            data['required'] = True
        else:
            data['required'] = False
    except AttributeError:
        data['required'] = False

    # TODO get description without slash
    div_class = table_html.find_all('div')
    try:
        data['description'] = div_class[-1].text.replace('\n', ' ')
        data['description'] = data['description'].replace('\\', ' ')
    except:
        data['description'] = None

    try:
        data['choices'] = [li.text.strip() for li in table_html.select('.ansible-option-cell ul.simple li')]
    except:
        data['choices'] = None

    # TODO default value not correct, is blank
    try:
        data['default value'] = table_html.select_one(
            '.ansible-option-cell ul.simple li span.ansible-option-choices-default-mark').previous_sibling.strip() \
            if table_html.select_one(
            '.ansible-option-cell ul.simple li span.ansible-option-choices-default-mark') else None
    except:
        data['default value'] = None

    # TODO  "deprecated": false

    # TODO - Question: Do we need version added, aliases
    try:
        data['aliases'] = table_html.select_one('.ansible-option-aliases').text.split(': ')[1]
    except AttributeError:
        data['aliases'] = None

    try:
        data['version added'] = table_html.select_one('.ansible-option-versionadded').text.split()[2] + " " + \
                                table_html.select_one('.ansible-option-versionadded').text.split()[3]
    except AttributeError:
        data['version added'] = None

    try:
        pre_tags = table_html.find_all('code', class_='docutils literal notranslate')
        all_tags = []
        for tag in pre_tags:
            all_tags.append(tag.text.strip())
        data['tag'] = all_tags
    except:
        data['tag'] = None

    return data


def get_attribute_specification(html):
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find('table')
    cell = soup.find_all('tr')

    attribute_specifications = {}
    ignore_header = True

    for attribute_class in cell:
        if ignore_header is False:
            specifications = extract_attribute_data(attribute_class)
            attribute_specifications[specifications['name']] = specifications
        else:
            ignore_header = False
    return attribute_specifications


# TODO - Question: Do we need this?
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


# TODO do we need this?
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

    attributes_specification: dict = get_attribute_specification(get_html_of_url(url))

    # for attribute_name, specification in attributes_specification.items():
    #    print(f"{attribute_name}: {specification}")

    # Define the filename and path for the JSON file
    filename = "attribute_specification.json"

    # Write data to the JSON file
    with open(filename, "w") as file:
        json.dump(attributes_specification, file)

    print(f"The JSON file '{filename}' has been created.")

    # TODO - Question: Do we need this?
    filename = "lineinfile_examples.yaml"
    attributes_values_dictionary: dict = parse_ansible_doc(url)
    task = Ansible_Task('test', 'ansible.builtin.lineinfile', attributes_values_dictionary)
    module_examples: dict = parse_examples_yaml(filename=filename)


if __name__ == "__main__":
    main()

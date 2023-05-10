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


# todo module name, description, parameters
def get_module_specification(url: str) -> str:
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

    # TODO  "deprecated": false or true
    data['deprecate'] = True
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


if __name__ == "__main__":
    main()

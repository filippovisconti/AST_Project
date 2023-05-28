import logging

import requests
from bs4 import BeautifulSoup

import json


# This function takes a URL page as input and returns the html of the page
def get_html_of_url(url: str) -> str:
    response = requests.get(url)
    html = response.text
    return html


def get_module_specification(html):
    soup = BeautifulSoup(html, 'html.parser')
    data = {}
    module_name = soup.find(class_='breadcrumb-item active').text.strip()
    description = soup.find(class_='admonition-title').text.strip()
    data['module_name'] = module_name.split(' ')[0]
    data['description'] = description
    data['options'] = get_attribute_specification(html)
    return data


def get_attribute_specification(html):
    soup = BeautifulSoup(html, 'html.parser')
    soup = soup.find('table')
    cell = soup.find_all('tr')

    attribute_specifications = []
    ignore_header = True

    for attribute_class in cell:
        if ignore_header is False:
            specifications = extract_attribute_data(attribute_class)
            exclude_list = ['others', 'validate', 'content', 'decrypt', 'checksum']
            if specifications['name'] not in exclude_list:
                attribute_specifications.append(specifications)
        else:
            ignore_header = False
    return attribute_specifications


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
        data['type'] = ''

    if data['type'] == 'any':
        data['type'] = 'mode'

    elif data['name'] == 'user' or data['name'] == 'seuser' or data['name'] == 'owner':
        data['type'] = 'user'

    elif data['name'] == 'group':
        data['type'] = 'group'

    elif data['name'] == 'gid':
        data['type'] = 'gid'

    if data['type'] == 'list':
        data['element_type'] = 'name' if data['name'] == 'name' else 'str'

    try:
        required_text = table_html.select_one('.ansible-option-required').text
        data['required'] = required_text is not None

    except AttributeError:
        data['required'] = False

    if data['name'] == 'line':
        data['required'] = True

    div_class = table_html.find_all('div')
    try:
        data['description'] = div_class[-1].text.replace('\n', ' ').replace('\\', ' ')
    except IndexError:
        data['description'] = None

    try:
        data['choices'] = [li.text.strip().split(' ')[0] for li in
                           table_html.select('.ansible-option-cell ul.simple li')]
    except AttributeError:
        data['choices'] = []

    try:
        tmp = table_html.find(class_='ansible-option-default-bold').text.strip()
        data['default'] = tmp.split(' ')[0]
        if data['default'] == 'Default:':
            raise AttributeError
    except AttributeError:
        data['default'] = None

    try:
        description = div_class[-1].text.replace('\n', ' ').replace('\\', ' ')
        keyword1: str = "Mutually exclusive with"
        keyword2: str = "May not be used with"
        keyword3: str = "used instead of"

        if keyword1 in description or keyword2 in description or keyword3 in description:
            values = []
            lines = description.split('\n')
            for line in lines:
                if keyword1 in line:
                    value = line.split(keyword1)[1].split('.')[0].strip().split(' and ')
                    for v in value:
                        values.append(v)
                if keyword2 in line:
                    value = line.split(keyword2)[1].split('.')[0].strip().split(' or ')
                    for v in value:
                        values.append(v)
                '''
                if keyword3 in line:
                    value = line.split(keyword3)[1].strip().split(',')[0]
                    values.append(value)
                '''
            if values:
                logging.debug(f"{data['name']} is mutually exclusive with values: {values}")

            data['mutually_exclusive_with'] = values
        else:
            data['mutually_exclusive_with'] = []
    except AttributeError:
        data['mutually_exclusive_with'] = []

    data['deprecated'] = False
    return data


def create_jsonfile(filename, content):
    with open(filename, "w") as file:
        json.dump(content, file, sort_keys=True, indent=2)


def fix_name(name):
    return name.split('.')[-1].split(' ')[0]


def generate_json(builtin_module_name: str = None, dest_dir: str = 'specs') -> None:
    url = f"https://docs.ansible.com/ansible/latest/collections/ansible/builtin/{builtin_module_name}_module.html"

    html = get_html_of_url(url)
    module_specification = get_module_specification(html)

    name = fix_name(module_specification['module_name'])
    file_path = f"{dest_dir}/{name}_specification.json"

    create_jsonfile(file_path, module_specification)


if __name__ == "__main__":
    print("This file is not meant to be run directly.")
    print("Please run the main.py file instead.")
    generate_json('copy', dest_dir='specs')

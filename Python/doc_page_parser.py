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

    try:
        if table_html.select_one('.ansible-option-required').text is not None:
            data['required'] = True
        else:
            data['required'] = False
    except AttributeError:
        data['required'] = False

    div_class = table_html.find_all('div')
    try:
        data['description'] = div_class[-1].text.replace('\n', ' ').replace('\\', ' ')
        # data['description'] = data['description'].replace('\\', ' ')
    except:
        data['description'] = None

    try:
        data['choices'] = [li.text.strip().split(' ')[0] for li in
                           table_html.select('.ansible-option-cell ul.simple li')]
    except:
        data['choices'] = []

    try:
        tmp = table_html.find(class_='ansible-option-default-bold').text.strip()
        data['default'] = tmp.split(' ')[0]
    except:
        data['default'] = None

    try:
        description = div_class[-1].text.replace('\n', ' ').replace('\\', ' ')
        if "Mutually exclusive with " in description:
            keyword = "Mutually exclusive with"
            values = []
            lines = description.split('\n')
            for line in lines:
                print(line)
                if keyword in line:
                    value = line.split(keyword)[1].split('.')[0].strip()

                    values.append(value)
            print("Mutually exclusive with values:", values)
        data['mutually_exclusive_with'] = values
    except:
        data['mutually_exclusive_with'] = None

    # TODO  "deprecated": false or true
    data['deprecated'] = False
    return data


def create_jsonfile(filename, content):
    with open(filename, "w") as file:
        json.dump(content, file)


def fix_name(name):
    return name.split('.')[-1].split(' ')[0]


def generate_json(builtin_module_name: str) -> None:
    url = f"https://docs.ansible.com/ansible/latest/collections/ansible/builtin/{builtin_module_name}_module.html"
    html = get_html_of_url(url)
    module_specification = get_module_specification(html)
    name = fix_name(module_specification['module_name'])
    create_jsonfile(f"json/{name}_specification.json", module_specification)


if __name__ == "__main__":
    generate_json()
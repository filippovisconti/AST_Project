import requests
import json
from bs4 import BeautifulSoup


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
    data['module_name'] = module_name
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
        data['type'] = None

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
        data['choices'] = [li.text.strip() for li in table_html.select('.ansible-option-cell ul.simple li')]
    except:
        data['choices'] = None

    try:
        data['default value'] = table_html.find(class_='ansible-option-default-bold').text.strip()
    except:
        data['default value'] = None

    # TODO  "deprecated": false or true
    data['deprecated'] = False
    return data


def create_jsonfile(filename, content):
    with open(filename, "w") as file:
        json.dump(content, file)


def main() -> None:
    url = "https://docs.ansible.com/ansible/latest/collections/ansible/builtin/lineinfile_module.html"
    html = get_html_of_url(url)
    module_specification = get_module_specification(html)
    create_jsonfile("module_specification.json", module_specification)


if __name__ == "__main__":
    main()

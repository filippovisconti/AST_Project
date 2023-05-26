import grp
import os
import pwd
import random
from pathlib import Path
from typing import List


def generate_random_array(element_type: str, min_length: int = 1, max_length: int = 10) -> List:
    """Generates a random list of values of the specified element_type."""
    length = random.randint(min_length, max_length)
    if element_type == "str":
        return [str(random.randint(0, 100)) for _ in range(length)]
    elif element_type == "name":
        list_of_names = ['htop', 'git', 'net-tools', 'sudo', 'nvim', 'nano', 'lsof']
        return random.sample(list_of_names, 2)
    elif element_type == "int" or element_type == "number" or element_type == "integer":
        return [random.randint(1, 100) for _ in range(length)]
    elif element_type == "float":
        return [random.uniform(0.1, 100.0) for _ in range(length)]
    elif element_type == "bool":
        return [random.choice([True, False]) for _ in range(length)]
    else:
        raise ValueError(f"Unsupported element_type: {element_type}")


def generate_random_parameter_value(parameter_type: str, choices: List = None, element_type: str = None):
    """Generates a random value of the specified parameter_type."""
    if parameter_type == "str" or parameter_type == "string":
        if choices:
            return random.choice(choices)
        else:
            return f"str_{random.randint(0, 100)}"
    elif parameter_type == 'user':
        user_list = pwd.getpwall()

        if user_list:
            random_user = random.choice(user_list)
            return random_user.pw_name
        else:
            return 'root'
    elif parameter_type == 'group':
        group_list = grp.getgrall()

        if group_list:
            random_group = random.choice(group_list)
            return random_group.gr_name
        else:
            return 'root'
    elif parameter_type == 'gid':
        group_list = grp.getgrall()

        if group_list:
            random_group = random.choice(group_list)
            return random_group.gp_gid
        else:
            return '1'

    elif parameter_type == "path":
        if choices:
            return random.choice(choices)
        else:
            file_list = []
            for root, dirs, files in os.walk('/'):
                for file in files:
                    file_list.append(os.path.join(root, file))

            if file_list:
                choice = random.choice(file_list)
                path = Path(choice)
                owner = path.owner()

                while owner is 'root':
                    choice = random.choice(file_list)
                    path = Path(choice)
                    owner = path.owner()

                return choice

    elif parameter_type == "mode":
        if choices:
            return random.choice(choices)
        else:
            return "0644"
    elif parameter_type == "int" or parameter_type == "number" or parameter_type == "integer":
        if choices:
            return random.choice(choices)
        else:
            return random.randint(0, 100)
    elif parameter_type == "float":
        if choices:
            return random.choice(choices)
        else:
            return random.uniform(0.1, 100.0)
    elif parameter_type == "bool" or parameter_type == "boolean":
        return random.choice([True, False])
    elif parameter_type == "list":
        if element_type:
            return generate_random_array(element_type)
        else:
            raise ValueError("Missing element_type for list parameter.")
    else:
        raise ValueError(f"Unsupported parameter_type: {parameter_type}")

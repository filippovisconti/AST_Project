import grp
import os
import pwd
import random
from pathlib import Path
from typing import List


class StringGenerator:
    @staticmethod
    def generate_random_value(choices: List = None) -> str:
        if choices:
            return random.choice(choices)
        else:
            return f"str_{random.randint(0, 100)}"

class NameGenerator:
    @staticmethod
    def generate_random_value(choices: List = None) -> str:
        if choices:
            return random.choice(choices)
        else:
            list_of_names = ['htop', 'git', 'net-tools', 'sudo', 'nvim', 'nano', 'lsof']
            return random.choice(list_of_names)

class UserGenerator:
    @staticmethod
    def generate_random_value() -> str:
        user_list = pwd.getpwall()

        if user_list:
            random_user = random.choice(user_list)
            return random_user.pw_name
        else:
            return 'root'


class GroupGenerator:
    @staticmethod
    def generate_random_value() -> str:
        group_list = grp.getgrall()

        if group_list:
            random_group = random.choice(group_list)
            return random_group.gr_name
        else:
            return 'root'


class GidGenerator:
    @staticmethod
    def generate_random_value() -> str:
        group_list = grp.getgrall()

        if group_list:
            random_group = random.choice(group_list)
            return random_group.gp_gid
        else:
            return '1'


class PathGenerator:
    @staticmethod
    def generate_random_value(choices: List = None) -> str:
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

                while owner == 'root':
                    choice = random.choice(file_list)
                    path = Path(choice)
                    owner = path.owner()

                return choice


class ModeGenerator:
    @staticmethod
    def generate_random_value(choices: List = None) -> str:
        if choices:
            return random.choice(choices)
        else:
            return "0644"


class IntegerGenerator:
    @staticmethod
    def generate_random_value(choices: List = None) -> int:
        if choices:
            return random.choice(choices)
        else:
            return random.randint(1, 100)


class FloatGenerator:
    @staticmethod
    def generate_random_value(choices: List = None) -> float:
        if choices:
            return random.choice(choices)
        else:
            return random.uniform(0.1, 100.0)


class BooleanGenerator:
    @staticmethod
    def generate_random_value() -> bool:
        return random.choice([True, False])


class ListGenerator:
    @staticmethod
    def generate_random_value(element_type: str, min_length: int = 2, max_length: int = 10) -> list:

        length = random.randint(min_length, max_length)
        if element_type == "str" or element_type == "string":
            return [StringGenerator.generate_random_value() for _ in range(length)]
        elif element_type == "int" or element_type == "number" or element_type == "integer":
            return [IntegerGenerator.generate_random_value() for _ in range(length)]
        elif element_type == "float":
            return [FloatGenerator.generate_random_value() for _ in range(length)]
        elif element_type == "bool":
            return [BooleanGenerator.generate_random_value() for _ in range(length)]
        elif element_type == "name":
            list_of_names = ['htop', 'git', 'net-tools', 'sudo', 'nvim', 'nano', 'lsof']
            return random.sample(list_of_names, 2)
        else:
            raise ValueError(f"Unsupported element_type: {element_type}")

import grp
import os
import pwd
import random
import string
from typing import List


class StringGenerator:
    @staticmethod
    def generate_random_value(choices: List = None) -> str:
        if choices:
            return random.choice(choices)
        else:
            length = random.randint(3, 15)
            letters = string.ascii_lowercase
            word = ''.join(random.choice(letters) for _ in range(length))
            return word


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
        all_users = pwd.getpwall()
        all_users = [user.pw_name for user in all_users]
        print(all_users)
        choice = random.choice(all_users)
        exclude = ['nobody', 'nogroup', 'root', 'system']

        while choice in exclude and len(choice) > 10:
            choice = random.choice(all_users)

        return choice


class GroupGenerator:
    @staticmethod
    def generate_random_value() -> str:
        groups = grp.getgrall()

        non_root_groups = [group.gr_name for group in groups if group.gr_gid > 0]

        choice = random.choice(non_root_groups)
        exclude = ['nobody', 'nogroup']

        while choice in exclude:
            choice = random.choice(non_root_groups)

        return choice


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
    def starts_with(path: str, exclude: str) -> bool:
        return exclude in path

    @staticmethod
    def starts_with_any_of(path: str, excludes: List[str]) -> bool:
        for exclude in excludes:
            if PathGenerator.starts_with(path, exclude):
                return True
        return False

    @staticmethod
    def generate_random_value(choices: List = None) -> str:
        if choices:
            return random.choice(choices)
        else:
            exclude = ['/usr', '/sys', '/proc', '/ssl', '/devices',
                       '/dpkg', '/lib', '/lib64', '/bin', '/sbin', '/boot',
                       'uid', 'gid', 'shadow', 'pass']
            file_list = []
            for root, dirs, files in os.walk('/'):
                for file in files:
                    if not PathGenerator.starts_with_any_of(path=root, excludes=exclude):
                        file_list.append(os.path.join(root, file))

            if not file_list:
                raise ValueError(f"Could not generate a random path, file_list is empty.")

            choice = random.choice(file_list)

            while not os.access(choice, os.R_OK):
                choice = random.choice(file_list)

            # print(f"Generated path: {choice}", PathGenerator.starts_with_any_of(choice, exclude))
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


if __name__ == "__main__":
    print(UserGenerator.generate_random_value())

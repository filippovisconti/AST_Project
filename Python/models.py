import pprint
from typing import List, Optional

import yaml

import json
from generators import generate_random_parameter_value


class AnsibleModuleParameter:
    """
    A class to represent a parameter of an Ansible module.

    Parameters
    ----------
    name : str
        The name of the parameter.
    type : str
        The data type of the parameter.
        Can be "array", "boolean", "integer", "null",
        "number", "object", or "string".
    required : bool
        Whether the parameter is required or not.
    description : str
        A brief description of the parameter.
    mutually_exclusive_with : list of str, optional
        A list of parameter names that are mutually exclusive with this parameter.
    default : str, optional
        The default value of the parameter.
    choices : list, optional
        A list of valid choices for the parameter.
    element_type : str, optional
        The data type of the elements of an array parameter.
    deprecated : bool, optional
        Whether the parameter is deprecated or not.
    deprecated_reason : str, optional
        The reason for deprecating the parameter.
    """

    def __init__(
            self,
            name: str,
            type: str,
            required: bool,
            description: str,
            mutually_exclusive_with: Optional[List[str]] = None,
            default: Optional[str] = None,
            choices: Optional[List] = None,
            element_type: Optional[str] = None,
            deprecated: bool = False,
            deprecated_reason: Optional[str] = None,
    ):
        self.name = name
        self.type = type
        self.required = required
        self.description = description
        self.mutually_exclusive_with = mutually_exclusive_with
        self.default = default
        self.choices = choices
        self.element_type = element_type
        self.deprecated = deprecated
        self.deprecated_reason = deprecated_reason


class AnsibleModuleSpecification:
    """
    A class to represent the specification of an Ansible module.

    Parameters
    ----------
    module_name : str
        The name of the Ansible module.
    description : str
        A brief description of the Ansible module.
    options : list of AnsibleModuleParameter
        A list of parameters that the Ansible module accepts.
    """

    def __init__(
            self, module_name: str, description: str, options: List[AnsibleModuleParameter]
    ):
        self.module_name = module_name
        self.description = description
        self.options = options

    @classmethod
    def from_json(cls, file_path: str):
        """
        Create an instance of AnsibleModuleSpecification from a JSON file.

        Parameters
        ----------
        file_path : str
            The path to the JSON file to load.

        Returns
        -------
        AnsibleModuleSpecification
            The parsed AnsibleModuleSpecification object.
        """
        with open(file_path, "r") as f:
            data = json.load(f)
        module_name = data["module_name"]
        description = data["description"]
        options = []
        for option in data["options"]:
            parameter = AnsibleModuleParameter(
                name=option["name"],
                type=option["type"],
                required=option["required"],
                description=option["description"],
                mutually_exclusive_with=option.get("mutually_exclusive_with"),
                default=option.get("default"),
                choices=option.get("choices"),
                element_type=option.get("element_type"),
                deprecated=option["deprecated"],
                deprecated_reason=option.get("deprecated_reason"),
            )
            options.append(parameter)
        return cls(module_name, description, options)


class Ansible_Task:
    """
    Ansible_Task class
    """

    def __init__(self, task_name, task_module, task_args):
        self.task_name: str = task_name
        self.task_module: str = task_module
        self.task_args: dict[str, str] = task_args

    def __str__(self):
        part = f'- name: {self.task_name}\n'
        part += f'  {self.task_module}:\n'

        for key, value in self.task_args.items():
            if (type(value) != str or key == "path" or key == "owner"
                    or key == "group" or key == "state" or key == "validate"
                    or (key == "line" and
                        ('192' in value or '127' in value or 'SELINUX' in value
                         or 'Listen' in value))):
                part += f"    {key}: {value}\n"
            elif key == "regexp" or key == "line":
                part += f"    {key}: '{value}'\n"
            else:
                part += f"    {key}: '{value}'\n"

        return part + "\n"

    def __repr__(self):
        return self.__str__()

    def write_to_file(self, file_path):
        with open(file_path, 'w') as f:
            f.write(str(self))

    @classmethod
    def from_json(cls, file_path: str):
        pass


class Ansible_Playbook:
    """
    Ansible_Playbook class
    """

    def __init__(self, playbook_name, hosts, tasks):
        self.playbook_name: str = playbook_name
        self.hosts: str = hosts
        self.tasks: list[Ansible_Task] = tasks

    def to_yaml(self, file_path):
        playbook_dict = {"- name": self.playbook_name,
                         "  hosts": self.hosts,
                         "    " : self.tasks}
        with open(file_path, 'w') as f:
            f.write("- name: " + self.playbook_name + "\n")
            f.write("  hosts: " + self.hosts + "\n")
            f.write("  tasks:\n")
            for task in self.tasks:
                f.write("  - name: " + task.task_name + "\n")
                f.write("    " + task.task_module + ":\n")
                for key, value in task.task_args.items():
                    f.write("      " + key + ": " + str(value) + "\n")


def create_task_from_spec_default(spec: AnsibleModuleSpecification) -> Ansible_Task:
    """
    Create an Ansible_Task from an AnsibleModuleSpecification using default values.

    Parameters
    ----------
    spec : AnsibleModuleSpecification
        The AnsibleModuleSpecification to create the Ansible_Task from.

    Returns
    -------
    Ansible_Task
        The created Ansible_Task.
    """
    task_name = f'Run {spec.module_name} module'
    task_module = spec.module_name
    task_args = {}
    for option in spec.options:
        # if option.required:
        # if mutually_exclusive_with:
        try:
            if option.default:
                task_args[option.name] = option.default
            elif option.choices:
                task_args[option.name] = option.choices[0]
            elif option.type == 'list':
                task_args[option.name] = generate_random_parameter_value(parameter_type=option.type,
                                                                         element_type=option.element_type)
            else:
                task_args[option.name] = generate_random_parameter_value(parameter_type=option.type)
        except Exception as e:
            print(e)
            print(option.name)

    return Ansible_Task(task_name, task_module, task_args)


def create_task_from_spec_random(spec: AnsibleModuleSpecification) -> list[Ansible_Task]:
    """
    Create an Ansible_Task from an AnsibleModuleSpecification using random values.

    Parameters
    ----------
    spec : AnsibleModuleSpecification
        The AnsibleModuleSpecification to create the Ansible_Task from.

    Returns
    -------
    Ansible_Task
        The created Ansible_Task.
    """
    task_name = f'Run {spec.module_name} module'
    task_module = spec.module_name
    tasks = []
    for i in range(3):
        task_args = {}
        # exclusive_parameters = []

        for option in spec.options:
            try:
                if option.type == 'list':
                    task_args[option.name] = generate_random_parameter_value(parameter_type=option.type,
                                                                             choices=option.choices,
                                                                             element_type=option.element_type)
                else:
                    task_args[option.name] = generate_random_parameter_value(parameter_type=option.type,
                                                                             choices=option.choices)
            except Exception as e:
                print(e)
                print(option.name)

        tasks.append(Ansible_Task(f"{task_name} {i}", task_module, task_args))

    return tasks


def main():
    from doc_page_parser import generate_json
    module_name = 'lineinfile'
    generate_json(module_name)
    t1 = create_task_from_spec_random(AnsibleModuleSpecification.from_json(f'json/{module_name}_specification.json'))
    p1 = Ansible_Playbook('Playbook name', 'all', t1)
    p1.to_yaml('trash/test.yaml')


if __name__ == '__main__':
    main()

import argparse
import grp
import json
import logging
import os
import pwd
import random
from typing import List, Optional
from typing import Union

logging.basicConfig(filename='/root/specs/specs_fuzzer.log', level=logging.INFO)

number_of_tasks = 10
number_of_combinations = 10


def generate_random_array(element_type: str, min_length: int = 1, max_length: int = 10) -> List:
    """Generates a random list of values of the specified element_type."""
    length = random.randint(min_length, max_length)
    if element_type == "str":
        return [str(random.randint(0, 100)) for _ in range(length)]
    elif element_type == "int":
        return [random.randint(0, 100) for _ in range(length)]
    elif element_type == "float":
        return [random.uniform(0.0, 100.0) for _ in range(length)]
    elif element_type == "bool":
        return [random.choice([True, False]) for _ in range(length)]
    else:
        raise ValueError(f"Unsupported element_type: {element_type}")


def generate_random_parameter_value(parameter_type: str, choices: List = None, element_type: str = None) -> Union[
    str, int, float, bool, list]:
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
                return random.choice(file_list)

            return f"/tmp/file_{random.randint(0, 100)}"

    elif parameter_type == "mode":
        if choices:
            return random.choice(choices)
        else:
            return "0644"
    elif parameter_type == "int" or parameter_type == "number":
        if choices:
            return random.choice(choices)
        else:
            return random.randint(0, 100)
    elif parameter_type == "float":
        if choices:
            return random.choice(choices)
        else:
            return random.uniform(0.0, 100.0)
    elif parameter_type == "bool" or parameter_type == "boolean":
        return random.choice([True, False])
    elif parameter_type == "list":
        if element_type:
            return generate_random_array(element_type)
        else:
            raise ValueError("Missing element_type for list parameter.")
    else:
        raise ValueError(f"Unsupported parameter_type: {parameter_type}")


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

    def __init__(self, name: str, type: str, required: bool, description: str,
                 mutually_exclusive_with: Optional[List[str]] = None, default: Optional[str] = None,
                 choices: Optional[List] = None, element_type: Optional[str] = None, deprecated: bool = False,
                 deprecated_reason: Optional[str] = None, ):
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

    def __init__(self, module_name: str, description: str, options: List[AnsibleModuleParameter]):
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
            parameter = AnsibleModuleParameter(name=option["name"], type=option["type"], required=option["required"],
                                               description=option["description"],
                                               mutually_exclusive_with=option.get("mutually_exclusive_with"),
                                               default=option.get("default"), choices=option.get("choices"),
                                               element_type=option.get("element_type"), deprecated=option["deprecated"],
                                               deprecated_reason=option.get("deprecated_reason"), )
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
            if (type(
                    value) != str or key == "path" or key == "owner" or key == "group" or key == "state" or key == "validate" or (
                    key == "line" and ('192' in value or '127' in value or 'SELINUX' in value or 'Listen' in value))):
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
        playbook_dict = {"- name": self.playbook_name, "  hosts": self.hosts, "    ": self.tasks}
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
        if option.mutually_exclusive_with:
            if not option.required:
                logging.info(f"Mutually exclusive parameter {option.name} is not required")
                continue
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


def create_task_from_spec_random(spec: AnsibleModuleSpecification) -> Ansible_Task:
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
    task_args = {}

    for option in spec.options:
        if option.mutually_exclusive_with:
            if not option.required:
                logging.info(f"Mutually exclusive parameter {option.name} is not required")
                continue
        try:
            if option.type == 'list':
                task_args[option.name] = generate_random_parameter_value(parameter_type=option.type,
                                                                         choices=option.choices,
                                                                         element_type=option.element_type)
            else:
                task_args[option.name] = generate_random_parameter_value(parameter_type=option.type,
                                                                         choices=option.choices)
        except Exception as e:
            logging.error(e)
            logging.error(option.name)

    return Ansible_Task(f"{task_name}", task_module, task_args)


def create_task_from_combi_random(spec: AnsibleModuleSpecification, parameters: list) -> Ansible_Task:
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
    task_args = {}

    for parameter in parameters:
        for option in spec.options:
            if option.name == parameter:
                print(option.name)
                print(option.type)
                try:
                    if option.type == 'list':
                        task_args[option.name] = generate_random_parameter_value(parameter_type=option.type,
                                                                                 choices=option.choices,
                                                                                 element_type=option.element_type)
                    else:
                        task_args[option.name] = generate_random_parameter_value(parameter_type=option.type,
                                                                                 choices=option.choices)
                except Exception as e:
                    logging.error(e)
                    logging.error(option.name)

    return Ansible_Task(f"{task_name}", task_module, task_args)


def create_playbook(task: Ansible_Task, module_name: str, hosts: str, playbook_suffix: str = 'default'):
    logging.info(f'Creating playbook for {module_name} on hosts: {hosts}')
    playbook = Ansible_Playbook(f'Testing {module_name}_{playbook_suffix}', hosts, [task])
    playbook_path = f'/root/fuzzed_playbooks/{module_name}_{playbook_suffix}.yaml'

    logging.info(f'Writing playbook to {playbook_path}')
    playbook.to_yaml(file_path=playbook_path)


def get_random_parameter_options(spec: AnsibleModuleSpecification) -> list:
    """
        Generates a list of unique parameter combinations for a module based on a specification file.

        Returns:
            list: A list of unique parameter combinations.

        """
    required_parameters = []
    optional_parameters = []

    for option in spec.options:
        if option.required:
            required_parameters.append(option.name)
        else:
            optional_parameters.append(option.name)

    unique_combinations = []
    while len(unique_combinations) < number_of_combinations:
        unique_parameters = []
        unique_parameters.extend(required_parameters)
        num_optional_parameters = random.randint(0, len(optional_parameters))
        random_optional_parameters = random.sample(optional_parameters, num_optional_parameters)
        unique_parameters.extend(random_optional_parameters)
        unique_parameters = remove_mutually_exclusive_parameters(spec, unique_parameters)

        if unique_parameters not in unique_combinations:
            unique_combinations.append(unique_parameters)

    return unique_combinations


def remove_mutually_exclusive_parameters(spec: AnsibleModuleSpecification, unique_parameters: list) -> list:
    """
       Removes mutually exclusive parameters from a list of unique parameters.

       Args:
           spec (AnsibleModuleSpecification): The specification object containing options information.
           unique_parameters (list): The list of unique parameters to remove mutually exclusive parameters from.

       Returns:
           list: The updated list of unique parameters after removing mutually exclusive parameters.

       """
    # TODO: save all the unique parameters
    for parameter in unique_parameters:
        for option in spec.options:
            if option.name == parameter and option.mutually_exclusive_with:
                mutually_exclusive_parameters = [option.mutually_exclusive_with]
                unique_parameters = [param for param in unique_parameters if
                                     param not in sum(mutually_exclusive_parameters, [])]
                break
    return unique_parameters


def main():
    parser = argparse.ArgumentParser(description='Fuzzer for Ansible parameters')
    parser.add_argument('-s', '--specs_file', type=str, help='Path to the Ansible module specification JSON file')
    parser.add_argument('-m', '--module_name', type=str, help='Name of the Ansible module')
    parser.add_argument('--hosts', type=str, help='Hosts to run the playbook on', default='all')
    args = parser.parse_args()

    logging.info(f'Generating random tasks for {args.specs_file}')

    module_spec: AnsibleModuleSpecification = AnsibleModuleSpecification.from_json(args.specs_file)

    logging.info(f'Creating default task for {args.module_name}')
    default_task = create_task_from_spec_default(module_spec)

    create_playbook(task=default_task, module_name=args.module_name, hosts=args.hosts, playbook_suffix='default')

    logging.info(f'Creating {number_of_tasks} random tasks for {args.module_name}')
    for i in range(number_of_tasks):
        logging.info(f'Creating task {i} for {args.module_name}')
        task = create_task_from_spec_random(module_spec)
        create_playbook(task=task, module_name=args.module_name, hosts=args.hosts, playbook_suffix=f'{i}')

    parameter_combinations = get_random_parameter_options(module_spec)
    for combination in parameter_combinations:
        task = create_task_from_combi_random(module_spec, combination)
        # TODO create playback?
    open('/root/specs/inverse_lock', 'w').close()


if __name__ == '__main__':
    main()
    module_spec: AnsibleModuleSpecification = AnsibleModuleSpecification.from_json('lineinfile_specification.json')
    parameter_combinations = get_random_parameter_options(module_spec)
    for combination in parameter_combinations:
        print(combination)
        task = create_task_from_combi_random(module_spec, combination)
        print(task)

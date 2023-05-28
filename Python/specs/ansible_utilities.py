import logging
import random

from ansible_models import AnsibleModuleSpecification, Ansible_Task, Ansible_Playbook
from generators import generate_random_parameter_value


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
            task_args[option.name] = generate_random_parameter_value(parameter_type=option.type,
                                                                     choices=option.choices,
                                                                     element_type=option.element_type)

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
    parameters : list
        The list of parameters to use for the Ansible_Task.

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
                try:

                    task_args[option.name] = generate_random_parameter_value(parameter_type=option.type,
                                                                             choices=option.choices,
                                                                             element_type=option.element_type)

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


def get_random_parameter_options(spec: AnsibleModuleSpecification, num_tests: int) -> list[list[str]]:
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
    '''
    print("req", required_parameters)
    print("opt", optional_parameters)
    '''

    unique_combinations = []
    len_optional_parameters = len(optional_parameters)
    min_len = len_optional_parameters // 2

    while len(unique_combinations) < num_tests:

        num_optional_parameters = random.randint(min_len, len_optional_parameters)
        random_combination = random.sample(optional_parameters, num_optional_parameters)
        # print("rand", random_combination)
        random_combination = remove_mutually_exclusive_parameters(spec, random_combination)
        # print("clean", random_combination)

        random_combination.extend(required_parameters)
        if random_combination not in unique_combinations and len(unique_combinations) < num_tests:
            unique_combinations.append(random_combination)

    # print("final", unique_combinations)
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
    mut_excl_dict = {}

    for option in spec.options:
        if option.mutually_exclusive_with:
            mut_excl_dict[option.name] = option.mutually_exclusive_with

    for parameter in unique_parameters:
        if parameter in mut_excl_dict:
            for p in mut_excl_dict[parameter].copy():

                try:
                    unique_parameters.remove(p)
                    # print("removed", p)
                except ValueError:
                    pass
            # print("not removed", p)

    return unique_parameters

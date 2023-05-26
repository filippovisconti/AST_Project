import argparse
import logging

from ansible_models import *
from ansible_utilities import create_task_from_spec_default, create_task_from_combi_random, create_playbook, \
    get_random_parameter_options


# logging.basicConfig(filename='/root/specs/specs_fuzzer.log', level=logging.INFO)


def main():
    parser = argparse.ArgumentParser(description='Fuzzer for Ansible parameters')
    parser.add_argument('-s', '--specs_file', type=str, help='Path to the Ansible module specification JSON file')
    parser.add_argument('-m', '--module_name', type=str, help='Name of the Ansible module')
    parser.add_argument('-n', '--num_tests', type=int, help='Number of fuzzed playbooks to generate', default='15')
    parser.add_argument('--hosts', type=str, help='Hosts to run the playbook on', default='all')
    args = parser.parse_args()

    logging.info(f'Generating random tasks for {args.specs_file}')

    module_spec: AnsibleModuleSpecification = AnsibleModuleSpecification.from_json(args.specs_file)

    logging.info(f'Creating default task for {args.module_name}')
    default_task = create_task_from_spec_default(module_spec)

    create_playbook(task=default_task, module_name=args.module_name, hosts=args.hosts, playbook_suffix='default')

    logging.info(f'Creating random combinations for {args.module_name}')
    parameter_combinations = get_random_parameter_options(module_spec, args.num_tests)

    i = 0
    logging.info(f'Creating {args.num_tests} random tasks for {args.module_name}')
    for combination in parameter_combinations:
        task = create_task_from_combi_random(module_spec, combination)
        create_playbook(task=task, module_name=args.module_name, hosts=args.hosts, playbook_suffix=f'{i}')
        logging.info(f'Created task {i} for {args.module_name}')
        i += 1

    open('/root/specs/inverse_lock', 'w').close()


def main2():
    specs: AnsibleModuleSpecification = AnsibleModuleSpecification.from_json('apt_specification.json')
    par_combinations = get_random_parameter_options(specs, 10)
    print(par_combinations)


if __name__ == '__main__':
    main()
    '''
    main2()
    '''

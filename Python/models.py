class Ansible_Task:
    '''
    Ansible_Task class
    '''

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
            elif (key == "regexp" or key == "line"):
                part += f"    {key}: '{value}'\n"
            else:
                part += f"    {key}: '{value}'\n"

        return part + "\n"

from type_models import *


def generate_random_parameter_value(parameter_type: str, choices: List = None, element_type: str = None):
    """Generates a random value of the specified parameter_type."""
    try:
        if parameter_type == "str" or parameter_type == "string":
            return StringGenerator.generate_random_value(choices=choices)

        elif parameter_type == 'user':
            return UserGenerator.generate_random_value()

        elif parameter_type == 'group':
            return GroupGenerator.generate_random_value()

        elif parameter_type == 'gid':
            return GidGenerator.generate_random_value()

        elif parameter_type == "path":
            return PathGenerator.generate_random_value(choices=choices)

        elif parameter_type == "mode":
            return ModeGenerator.generate_random_value(choices=choices)

        elif parameter_type == "int" or parameter_type == "number" or parameter_type == "integer":
            return IntegerGenerator.generate_random_value(choices=choices)

        elif parameter_type == "float":
            return FloatGenerator.generate_random_value(choices=choices)

        elif parameter_type == "bool" or parameter_type == "boolean":
            return BooleanGenerator.generate_random_value()

        elif parameter_type == "list":
            return ListGenerator.generate_random_value(element_type=element_type, min_length=2, max_length=10)

        else:
            raise ValueError(f"Unsupported parameter_type: {parameter_type}")
    except Exception as e:
        print(f"Exception in generate_random_parameter_value: {e}, with parameter_type: {parameter_type}")
        raise e

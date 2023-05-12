import random
from typing import List, Union


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


def generate_random_parameter_value(parameter_type: str, choices: List = None, element_type: str = None) -> \
        Union[str, int, float, bool, list]:
    """Generates a random value of the specified parameter_type."""
    if parameter_type == "str" or parameter_type == "string":
        if choices:
            return random.choice(choices)
        else:
            return f"str_{random.randint(0, 100)}"
    elif parameter_type == "path":
        if choices:
            return random.choice(choices)
        else:
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

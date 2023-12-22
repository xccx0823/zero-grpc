import importlib
import re


def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def snake_to_camel(string):
    parts = string.split('_')
    return ''.join(part.capitalize() for part in parts)


def dynamic_import(import_string: str):
    module_name, obj = import_string.split(':')
    module = importlib.import_module(module_name)
    return getattr(module, obj)

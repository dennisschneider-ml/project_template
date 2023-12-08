#!/usr/bin/env python

import ast
from loguru import logger
import os
from argparse import ArgumentParser

import yaml


def get_config_path(input_path):
    directory, filename = os.path.split(input_path)

    filename = os.path.splitext(filename)[0]

    yaml_directory = os.path.join("configs", *(directory.split(os.path.sep)[1:]))
    yaml_filename = filename + ".yaml"
    yaml_path = os.path.join(yaml_directory, yaml_filename)

    return yaml_path


def get_constructor_parameters(src_path):
    with open(src_path, "r") as file:
        source = file.read()
    tree = ast.parse(source)
    parameters, model_name = None, None
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            decorators = node.decorator_list
            matching_decorator_found = next(
                (
                    ast.unparse(decorator).endswith(".register_module()")
                    for decorator in decorators
                ),
                None,
            )
            if matching_decorator_found:
                init_args = next(
                    func.args.args for func in node.body if func.name == "__init__"
                )
                model_name = node.name
                parameters = [a.arg for a in init_args]
                break
    if parameters is None:
        logger.warning(f"No decorated class found in '{src_path}'.")
        return

    config_parameters = {"type": model_name} | {param: "???" for param in parameters}
    del config_parameters["self"]
    # Ignore "kwargs"-parameter.
    if "kwargs" in config_parameters:
        del config_parameters["kwargs"]
    return config_parameters


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", dest="files", nargs="+")
    args = parser.parse_args()

    for src in args.files:
        config_path = get_config_path(src)
        model_params = get_constructor_parameters(src)

        if os.path.exists(config_path):
            with open(config_path, "r") as file:
                curr_config = yaml.load(file, Loader=yaml.FullLoader)
        else:
            # Create directory-structyre if not exists.
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            curr_config = {}
        new_keys = set(model_params.keys()) - set(curr_config.keys())
        if new_keys:
            changes = {k: model_params[k] for k in new_keys}
            model_name = changes["type"]
            del changes["type"]
            changes = {"type": model_name} | changes
            curr_config.update(changes)
            with open(config_path, "w+") as file:
                yaml.dump(curr_config, file, sort_keys=False)
            logger.info(f"Updated {tuple(new_keys)} in {config_path}.")

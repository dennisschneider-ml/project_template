#!/bin/python

import os
import inspect
import importlib
import logging
import yaml
from argparse import ArgumentParser


def get_config_path(input_path):
    directory, filename = os.path.split(input_path)

    filename = os.path.splitext(filename)[0]

    yaml_directory = os.path.join('configs', *(directory.split(os.path.sep)[1:]))
    yaml_filename = filename + '.yaml'
    yaml_path = os.path.join(yaml_directory, yaml_filename)

    return yaml_path


def get_constructor_parameters(src_path):
    src_path = src_path.split(".")[0].replace("/", ".")
    mod = importlib.import_module(src_path)
    model_name, model_cls = next(filter(lambda member: "Model" in member[0], inspect.getmembers(mod, inspect.isclass)))
    parameters = inspect.signature(model_cls).parameters
    config_parameters = {"type": model_name} | {param: "???" for param in parameters}
    # Ignore "kwargs"-parameter.
    if "kwargs" in config_parameters:
        del config_parameters["kwargs"]
    return config_parameters
   

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-f', dest="files", nargs="+")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    for src in args.files:
        config_path = get_config_path(src)
        model_params = get_constructor_parameters(src)

        if os.path.exists(config_path):
            with open(config_path, 'r') as file:
                curr_config = yaml.load(file, Loader=yaml.FullLoader)
        else:
            # Create directory-structyre if not exists.
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            curr_config = {}
        new_keys = set(model_params.keys()) - set(curr_config.keys())
        if new_keys:
            changes = {k: model_params[k]  for k in new_keys}
            model_name = changes["type"]
            del changes["type"]
            changes = {"type": model_name} | changes
            curr_config.update(changes)
            with open(config_path, 'w+') as file:
                yaml.dump(curr_config, file, sort_keys=False)
            logging.info(f"Updated {tuple(new_keys)} in {config_path}.")



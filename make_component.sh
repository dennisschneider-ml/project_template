#!/bin/sh

# Name: Component_Name
# Create directory, builder.py and __init__.py if not already exists
# Add module in directory. Let it import builder and register to the Registry.
# make_configs for new component.
# Add disclaimer, that you can now use `build_<component_name>` to build that component.

echo "Component Type: "
read component_type
echo "Component Name: "
read component_name
caps_component_type=${component_type^^}
component_class=$(echo $component_name | sed -r 's/_([a-z])/\U\1/gi; s/^([a-z])/\U\1/gi; s/$/Model/')

mkdir -p "src/$component_type"

[ -f "src/$component_type/__init__.py" ] || echo \
"""from .builder import ${caps_component_type}S, build_$component_type
from .$component_name import $component_class

__all__ = [
    '$component_class',
    '${caps_component_type}S',
    'build_$component_type'
]
""" > "src/$component_type/__init__.py"

[ -f "src/$component_type/builder.py" ] || echo \
"""from src.utils.config import Registry, build_from_config


${caps_component_type}S = Registry(\"${component_type}s\")


def build_$component_type(cfg, default_args)=None):
    return build_from_config(cfg, ${caps_component_type}S, default_args=default_args)
""" > "src/$component_type/builder.py"

[ -f "src/$component_type/$component_class" ] || echo \
"""from .builder import ${caps_component_type}S

@${caps_component_type}S.register_module()
class $component_class:

    def __init__(self):
        pass
"""

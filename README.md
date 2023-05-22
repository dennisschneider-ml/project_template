# Project Template

This template enables an easy installation, configuration management system and dataset reproducing system. \
The code should be placed in `src`, with each package representing a certain component of the end-system:

Let such a component be called `COMPONENT`, this should be adapted to the use-case.
```python
# src/.../builder.py
from src.utils.config import Registry, build_from_config

COMPONENTS = Registry("component_name")

def build_component(cfg, default_args=None):
    return build_from_config(cfg, COMPONENTS, default_args=default_args)


# src/.../actual_component_implementation.py
from .builder import COMPONENTS

@COMPONENTS.register_module()
class ImplementedComponentModel:

    def __init__(self, argument_1, argument_2, ...):
        ...
```

Running `make configs` now creates a corresponding configuration file in `./configs` which fills in the variables in the constructor. \
The configurations are built in the following way:
```shell
- configs/
----- base.yaml
----- config.yaml
----- experiment
--------- experiment01.yaml
--------- ...
```
The `base.yaml` file should define the base components and the general setup of the model.
```yaml
defaults:
  - model/solver/base
  - model/gnn/base
  - data/dataset1/concept
  - ...
```
The config.yaml should not be changed and simply makes the experiment-argument obligatory.
```yaml
defaults:
  - base
  - experiment: ???
```
Each experiment should use the components listed in `configs/model/...` and may override experiment-specific arguments.
```yaml
defaults:
  - model/gnn: other_model

model:
  gnn:
    depth: 5
    ...
```

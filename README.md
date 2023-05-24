# Research Template

This template enables an easy installation, configuration management system and dataset reproduction system. \
It revolves around modularizing the system into its components, as described in the following.

## Installation
Run the following command to install the environment.
```shell
.make/install
```

## Setup for Usage
The system can be used after initializing it:
```shell
source enter
```

## Getting Started

<details>
    <summary>
        1. Creating Components
    </summary>
    
</details>

<details>
    <summary>
        2. A look into the generated Config-files
    </summary>
    
</details>

<details>
    <summary>
        3. Bundling Components into single Experiments
    </summary>
    
</details>

<details>
    <summary>
        4. Bringing everything together: The complete System
    </summary>
    
</details>

<details>
    <summary>
        5. Running and Logging of results
    </summary>
    
</details>


## Running the System
Due to the ``source enter``-script temporarily adding the project directory to the path, the system can easily be used, including auto-completion:
```shell
run experiment=...
# Or with autocompletion
run e<TAB><TAB>
```
This command will list all available experiments, as found in `configs/experiments`.

## The Component-System
<details>
    <summary>
        Introduction
    </summary>
First, let me introduce you to the underlying workflow-assumption. \
A system is comprised of components.
Each component has a certain implementation and attributes.
However, especially in a research-context, multiple components need to be evaluated against eachother.
Thus, a system is assumed in which each component has its own implementation and configuration and an execution of the system is bundled within experiments. \
An experiment is comprised of a selection of components it uses and an optional overwriting of selected parameters.
In effect, an entire research system can be instantiated from configuration files, since components within a common type act similarly. \
The idea behind this template is, to create such components and component-types using the `add_component`-script and automatically creating corresponding configuration files.

Furthermore, a research project is in need of a reproducible dataset-creation system.
Thus, this template provides the command `make <dataset_name>` which automatically downloads and preprocesses all datasets given the implemented scripts.
Notable here, is the already implemented multi-core functionality of the provided preprocessing script, automatically using all physical cores present in the machine.
</details>


## Automated Configuration-Management
Running `add_component` opens a small terminal application to lead you through the creation of the component-based system:
```shell
Component Topic (often data, model, ...):
> model
Component Type:
> gnn
Component Name:
> base
```
This would create the directory `src/model/gnn/base/` and would provide `__init__.py`, `builder.py` and `base.py` files which are needed for the configuration environment.
The model is called `BaseModel` in `base.py`, which is where you implement the component itself.
The builder can be used in the following way to instantiate a model entirely from the generated config:
```python
from src.model.gnn import build_gnn

component = build_gnn(gnn_config, default_args={...})
```
While a corresponding yaml configuration-file is created in `configs/model/gnn/base.yaml`.
It declares each variable named in the constructor of the component-model.
Reload all change-affected configs by running `make configs`.


## Automated Dataset-Management
A Dataset can be added by creating a directory in `data/`.
Running `make list` now shows a new task showing this new directory.
Running `make <directory_name>` creates an initial directory-structure for this dataset. \
Next, the script `get_original_data.sh` should retrieve the dataset and store it in `data/<dataset_name>/original`.
Each file which exists in `original` but not in `preprocessed` is piped through `preprocess.py`.
Thus, this file should be implemented next to preprocess the data accordingly. \
This dataset-processing is done only for unprocessed data or if the `get_original_data.sh`-script is changed. Thus, large datasets can be processed over-night and can easily be made reproducable in a git-repository without storing the datasets themselves.


## The Configuration architecture
In general, the configurations are built in the following way:
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


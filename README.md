# Research Template

This template repository enables an easy configuration management system and dataset reproduction system for research projects. \
It revolves around modularizing the software system into its components, making the reproduction, management and logging of experiments easier. \
This project was developed after realizing a few pitfalls of past research-projects and in an attempt to address a reproduction and understanding of measurements multiple months after executing them.

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
    
After entering the environment with ``source enter``, we can start to build the architecture of our system component by component.
Assume, that components are structured in a similar fashion to the following:
````
├── model
│   ├── attributors
│   │   ├── nlp
│   │   ├── vision
│   ├── gans
│   │   ├── nlp
│   │   ├── vision
├── dataset
│   ├── imagenet
````
This architecture assumes - as is often the case in a research-context - that for a certain component within a software-architecture, we want to compare multiple different implementation against eachother. \
The directory-depths will in the following be known as ``topic`` (e.g. model, dataset), optionally ``type`` (e.g. attributors, gans) and ``name`` (e.g. base, nlp, imagenet). \
For initializing this structure, the command-line script ``add_component`` can be used to easily create multiple components.
Executing ``tree`` on the repository shows the created copmonents, including their configuration-files mirroring the source file-structure:
````
├── configs
│   ├── base.yaml
│   ├── config.yaml
│   ├── model
│   │   ├── attributors
│   │   │   ├── base.yaml
│   │   │   ├── nlp.yaml
│   │   │   ├── vision.yaml
├── src
│   ├── __init__.py
│   ├── model
│   │   ├── attributors
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── builder.py
│   │   │   ├── nlp.py
│   │   │   ├── vision.py
````
It immediately becomes apparent, that each implementation has a corresponding configuration file.
We will use this configuration file to instantiate an entire object out of it, by specifying all arguments of an object's constructor in the configuration file. \
Since keeping track of changing constructors and a configuration file can be cumbersome, simply executing ``make`` or ``make configs`` is sufficient to reload all configuration files of source files we have changed.
Thus, we will generate the following for a certain implementation source file:
````python
# model/attributors/base.py

class BaseModel(Module):

    def __init__(self, p_dropout, hidden_dim, use_softmax):
        pass
````
````yaml
type: BaseModel
p_dropout: ???
hidden_dim: ???
use_softmax: ???
````
We can now fill in the standard configuration for each component.
This is simply the out-of-the-box configuration which can later be overwritten in the respective Experiments.
</details>

<details>
    <summary>
        2. A look into the generated Config-files
    </summary>

Each config file consists of a ``type``, which declares the class to instantiate and a set of parameters to fill in the constructor.
Note here, that the ``**kwargs`` argument will never appear here while any manually added argument will automatically be passed to the constructor in the expected ``**kwargs`` behavior. \
</details>

<details>
    <summary>
        3. Bundling Components into stand-alone Experiments
    </summary>
    
Since in a research-context, different experiments consist of different architecture-combinations, the template offers an easy interface to create new, independent experiments, which can easily be logged, evaluated and stashed, if need be. \
The config-directory ``configs/experiment`` will be scanned for any ``yaml``-files and recommends them in the commandline upon entering ``run e<TAB><TAB>`` or ``run experiment=<TAB>``.
An experiment configuration is defined in the following way:
````yaml
# Path to all components
defaults:
    - model/attributors: nlp.yaml
    - model/gans: nlp/yaml

# Explicit overwriting of certain parameters
model:
    attributors:
        p_dropout: 0.3
````
To define a default system-configuration, the same is recommended to be done in the ``configs/base.yaml``-file.
</details>

<details>
    <summary>
        4. Bringing everything together: The complete System
    </summary>
    
After having created the entire architecture, the project can be combined in the ``run``-script.
Note, that imports should be conducted within the ``main``-function due to prevent slowing down the auto-completion of Hydra. \
The single components now can conveniently be parsed from the config by using the respective ``builder.py``-classes.
````python
from src.model.attributors import build_attributor
from src.model.gans import build_gan

...

model_conf = config["model"]
attributor = build_attributor(model_conf.pop("attributor"))
gan = build_gan(model_conf.pop("gan"))

# Now use these components in a reasonable way.
# In an ML context, this would probably mean, concatenating them in a Sequential-Model and
# Run this model within a Solver-Object, which itself is instantiated from a Config.
# This Solver would have a Learning Rate, a Loss Function, an Optimizer Name, ...
````
</details>

<details>
    <summary>
        5. Running and Logging of results
    </summary>

As already introduced, the entire pipeline can be run using the following command:
````shell
run e<TAB><TAB>
# or
run experiment=<TAB>
````
This will list all available experiments which can conveniently be selected and run.
In the end, the results, logs and configurations are saved to ``outputs/<Date>/<Time>``. \
The log-level by default is ``DEBUG`` and uses the standard ``logging`` module.
The used configuration can be found in ``<output_dir>/.hydra/config.yaml``.
</details>

Furthermore, a research project is in need of a reproducible dataset-creation system.
Thus, this template provides the command `make <dataset_name>` which automatically downloads and preprocesses all datasets given the implemented scripts.
Notable here, is the already implemented multi-core functionality of the provided preprocessing script, automatically using all physical cores present in the machine.
</details>

<details>
    <summary>
        6. Reproducing your results
    </summary>

After having used this Template, the input configurations, the logging at runtime and the end-results are saved in corresponding directories.
We successfully have accomplished full reproducibility!
But ... have we?
The answer is no! \
We have not yet talked about the processing and retrieving of our datasets.
This is another feature of this template and is easily explained.
After having decided on datasets to use for your research project, add corresponding directories to the ``data``-directory.
Running ``make`` or ``make <directory_name>`` will automatically create a predefined directory structure for each dataset:
````
├── data
│   ├── dataset1
│   │   ├── get_original_data.sh
│   │   ├── original
│   │   ├── preprocess.py
│   │   ├── preprocessed
````
As soon as you change the ``get_original_data.sh``-file, running ``make`` will execute the script, which should populate the ``original`` directory with the raw data-files.
Afterwards, for each file in ``original`` which does not have a counterpart in ``preprocessed``, the corresponding files will be piped through the ``preprocess.py``-script and saved to ``preprocessed``. \
Another execution of ``make`` on an already processed dataset will not run anything.
Notable here is, that the ``preprocess.py``-script per default uses all available hardware-cores to process the dataset in parallel.
</details>


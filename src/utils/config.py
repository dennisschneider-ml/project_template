from omegaconf import DictConfig, OmegaConf


def merge_with_subconfig(parameter: str, config: DictConfig) -> dict:
    dict_config: dict = OmegaConf.to_container(config, resolve=True)    #type: ignore
    subconfig = dict_config.pop(parameter)                            
    base_config = dict_config
    return _merge_dicts(base_config, subconfig)                        


def _merge_dicts(base_dict: dict, override_dict: dict) -> dict:
    for k, v in override_dict.items():
        if isinstance(v, dict):
            base_dict[k] = _merge_dicts(base_dict[k], v)
        else:
            base_dict[k] = v
    return base_dict


def build_from_config(config: DictConfig, registry, default_args=None):
    if 'type' not in config:
        if default_args is None or 'type' not in default_args:
            raise KeyError('config must contain "type" attribute')
    args = config
    if default_args is not None:
        for name, value in default_args.items():
            args.setdefault(name, value)
    obj_type = args.pop("type")

    obj_class = registry.get(obj_type)
    if obj_class is None:
        raise KeyError(f'{obj_type} is not in the {registry.name} registry')
    return obj_class(**args)

def test():
    print("lol")

class Registry:

    def __init__(self, name, build_func=None) -> None:
        self._name = name
        self._module_dict = dict()

        if build_func is None:
            self.build_func = build_from_config
        else:
            self.build_func = build_func

    def __len__(self):
        return len(self._module_dict)

    def __repr__(self):
        format_str = self.__class__.__name__ + \
                     f'(name={self._name}, ' \
                     f'items={self._module_dict})'
        return format_str

    @property
    def name(self):
        return self._name

    @property
    def module_dict(self):
        return self._module_dict

    def get(self, key):
        scope, real_key = self.split_scope_key(key)
        return self._module_dict[real_key]

    @staticmethod
    def split_scope_key(key):
        split_index = key.find('.')
        if split_index != -1:
            return key[:split_index], key[split_index + 1:]
        else:
            return None, key

    def build(self, *args, **kwargs):
        return self.build_func(*args, **kwargs, registry=self)

    def register_module(self, name=None, force=False, module=None):
        def _register(cls):
            self._register_module(
                module_class=cls, module_name=name, force=force)
            return cls

        return _register

    def _register_module(self, module_class, module_name, force=False):
        if module_name is None:
            module_name = module_class.__name__
        if isinstance(module_name, str):
            module_name = [module_name]
        for name in module_name:
            if not force and name in self._module_dict:
                raise KeyError(f'{name} is already registered '
                               f'in {self.name}')
            self._module_dict[name] = module_class


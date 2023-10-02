import os

from doit.tools import Interactive
from pathlib import Path


DOIT_CONFIG = {
    'action_string_formatting': 'new',
    'default_tasks': os.listdir("data") + ["configs"]
}


def task_datasets():
    """
    Process all datasets.
    """
    root_dir = Path("data")
    if not root_dir.exists():
        root_dir.mkdir()
        print("Initially created datasets directory.")
    datasets = filter(lambda d: d.is_dir(), root_dir.iterdir())
    for dataset_dir in datasets:
        yield {
            "name": f"create_preprocess_{dataset_dir.basename}",
            "actions": ["cp .make/preprocess.py %s" % dataset_dir],
            "uptodate": [(dataset_dir / "preprocess.py").exists()],
        }
        yield {
            "name": f"create_fetch_{dataset_dir.basename}",
            "actions": ["echo -n > %s/get_original_data.sh" % dataset_dir],
            "uptodate": [(dataset_dir / "get_original_data.sh").exists()],
        }
        yield {
            "name": f"mkd_preprocess_{dataset_dir.basename}",
            "actions": ["mkdir %s/original" % dataset_dir],
            "uptodate": [(dataset_dir / "original").exists()],
        }
        yield {
            "name": f"mkd_original_{dataset_dir.basename}",
            "actions": ["mkdir %s/preprocessed" % dataset_dir],
            "uptodate": [(dataset_dir / "preprocessed").exists()],
        }
        yield {
            "name": f"exec_fetch_{dataset_dir.basename}",
            "file_dep": [dataset_dir / "get_original_data.sh"],
            "uptodate": [False],
            "actions": ["bash {dependencies}"],
        }
        for orig_file in Path.iterdir(dataset_dir / "original"):
            yield {
                "name": f"exec_preprocess_{dataset_dir}_{orig_file}",
                "uptodate": [True],
                "file_dep": [
                    dataset_dir / "original" / orig_file / "graph_data.csv"
                ],
                "targets": [dataset_dir / "preprocessed" / (orig_file + ".pt")],
                "actions": [
                    dataset_dir + "/preprocess.py {dependencies} {targets}",
                ],
                "verbosity": 2,
            }


def task_configs():
    """Sync configs with class-constructors."""
    ignore_files = ["builder.py", "__init__.py"]
    ignore_dirs = ["utils", "__pycache__"]

    python_files = _list_files("src", ignore_files, ignore_dirs)
    return {
        # "uptodate": [len(python_files) == 0],
        "file_dep": list(python_files),
        "actions": [
            'python make_configs.py -f {changed}'
        ],
        "verbosity": 2,
    }


def task_purge():
    """Clean the outputs directory."""
    return {
        "uptodate": [len(os.listdir("outputs")) == 0],
        "actions": [
            Interactive('git clean -ix outputs/*')
        ],
    }

    
def _list_files(directory, exclude_names=[], exclude_dirs=[]):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py") and file not in exclude_names:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
    return file_paths


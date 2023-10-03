from pathlib import Path

from doit.tools import Interactive

DOIT_CONFIG = {"action_string_formatting": "new", "default_tasks": ["configs"]}


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
            "name": f"create_preprocess_{dataset_dir.name}",
            "actions": ["cp .make/preprocess.py %s" % dataset_dir],
            "uptodate": [(dataset_dir / "preprocess.py").exists()],
        }
        yield {
            "name": f"create_fetch_{dataset_dir.name}",
            "actions": ["echo -n > %s/get_original_data.sh" % dataset_dir],
            "uptodate": [(dataset_dir / "get_original_data.sh").exists()],
        }
        yield {
            "name": f"mkd_preprocess_{dataset_dir.name}",
            "actions": ["mkdir %s/original" % dataset_dir],
            "uptodate": [(dataset_dir / "original").exists()],
        }
        yield {
            "name": f"mkd_original_{dataset_dir.name}",
            "actions": ["mkdir %s/preprocessed" % dataset_dir],
            "uptodate": [(dataset_dir / "preprocessed").exists()],
        }
        yield {
            "name": f"exec_fetch_{dataset_dir.name}",
            "file_dep": [dataset_dir / "get_original_data.sh"],
            "uptodate": [False],
            "actions": ["bash {dependencies}"],
        }
        if not (dataset_dir / "original").exists():
            return
        for orig_file in Path.iterdir(dataset_dir / "original"):
            yield {
                "name": f"exec_preprocess_{dataset_dir}_{orig_file}",
                "uptodate": [True],
                "file_dep": [dataset_dir / "original" / orig_file / "graph_data.csv"],
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

    python_files = _list_files(Path("src"), ignore_files, ignore_dirs)
    return {
        # "uptodate": [len(python_files) == 0],
        "file_dep": list(python_files),
        "actions": ["python make_configs.py -f {changed}"],
        "verbosity": 2,
    }


def task_purge():
    """Clean the outputs directory."""
    return {
        "uptodate": [len(list(Path("outputs").iterdir())) == 0],
        "actions": [Interactive("git clean -ix outputs/*")],
    }


def _list_files(directory, exclude_names=[], exclude_dirs=[]):
    file_paths = []
    for file_path in directory.rglob("*.py"):
        if file_path.name not in exclude_names and not any(
            exclude_dir in file_path.parts for exclude_dir in exclude_dirs
        ):
            file_paths.append(str(file_path))
    return file_paths

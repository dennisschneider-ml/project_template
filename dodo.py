DOIT_CONFIG = {
    'action_string_formatting': 'new'
}

from doit.tools import Interactive
import os
from pathlib import Path
import shutil


def task_install():
    """Install the environment."""
    return {
        "file_dep": ["requirements.txt"],
        "targets": [".venv"],
        "actions": [
            '.make/install',
        ]
    }


def task_datasets():
    """
    Process all datasets.
    """
    root_dir = Path("data")
    datasets = filter(lambda d: d.is_dir(), root_dir.iterdir())
    for dataset_dir in datasets:
        yield _process_dataset(dataset_dir)
    return {
        "basename": "datasets",
        "file_dep": ["data"],
        "actions": []
    }


def task_configs():
    """Sync configs with class-constructors."""
    ignore_files = ["builder.py", "__init__.py"]
    ignore_dirs = ["utils", "__pycache__"]

    python_files = _list_files("src", ignore_files, ignore_dirs)
    return {
        "uptodate": [len(python_files) == 0],
        "file_dep": list(python_files),
        "actions": [
            'python make_configs.py -f {dependencies}'
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


def _process_dataset(dataset_dir):
    """
    Process an entire dataset.
    Create the file-structure if needed (original- and preprocessed directories).
    Process each original file which has no corresponding preprocessed file.
    """
    original_dir = dataset_dir / "original"
    preprocessed_dir = dataset_dir / "preprocessed"
    if not original_dir.exists():
        original_dir.mkdir(exist_ok=True)
        preprocessed_dir.mkdir(exist_ok=True)
        (dataset_dir / "get_original_data.sh").touch(exist_ok=True)
        shutil.copy(".make/preprocess.py", str(dataset_dir))
    # If get_original_data.sh has been changed, run it to retrieve original data.
    yield {
        "doc": f"Fetch original data for {dataset_dir.name}.",
        "basename": dataset_dir.name,
        "name": "Fetch",
        "file_dep": [dataset_dir / "get_original_data.sh"],
        "actions": [
            'sh {dependencies}'
        ]
    }
    for original_file in original_dir.iterdir():
        corresponding_prep_file = preprocessed_dir / original_file.name
        yield _preprocess_file(original_file, corresponding_prep_file)
            

def _preprocess_file(original_file, prep_file):
    """
    Pipe a single original file through the preprocessing-script and save it in
    a corresponding preprocessed file.
    """
    dataset_path = original_file.parent.parent
    yield {
        "doc": "Preprocess the dataset %s." % dataset_path.name,
        "basename": dataset_path.name,
        "name": "Preprocess",
        "file_dep": [original_file],
        "targets": [prep_file],
        "actions": [
            'python %s {dependencies} {targets}' % (dataset_path / "preprocess.py")
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


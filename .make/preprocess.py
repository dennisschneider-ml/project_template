#!/bin/python

import logging
from argparse import ArgumentParser
from multiprocessing import Pool

import numpy as np
import pandas as pd
import psutil


def process(data: pd.DataFrame) -> pd.DataFrame:
    """
    Process an equally-split chunk of the entire dataset to ensure maximum utility of multicore-CPUs.
    The results of the functions running parallel will in the end be concatenated.
    """
    return data


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("infile")
    parser.add_argument("outfile")
    args = parser.parse_args()

    all_items = pd.read_csv(args.infile)
    original_size = len(all_items)
    logging.info(f"Original dataset-length: {original_size}")

    # Get amount of physical CPU-cores for maximum utility usage.
    num_cpus = psutil.cpu_count(logical=False)

    # Divide DataFrame into equal chunks to be processed in parallel.
    sub_dfs = np.array_split(all_items, num_cpus)
    del all_items

    process_pool = Pool(processes=num_cpus)
    resulting_dfs = process_pool.map(process, sub_dfs)
    dataset = pd.concat(resulting_dfs, ignore_index=True)

    preprocessed_size = len(dataset)
    logging.info(
        f"The preprocessed dataset consists of {preprocessed_size} samples. This equates to {100*preprocessed_size/original_size}% of the original dataset.",
        flush=True,
    )

    dataset.to_csv(args.outfile)

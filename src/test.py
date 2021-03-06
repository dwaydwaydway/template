import argparse
import ipdb
import numpy as np
import torch
import random
import subprocess
import sys
import warnings

from box import Box
from pathlib import Path

from modules.logger import create_logger


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
            '-c', '--config', dest='config_path',
            default='./config.yaml', type=Path,
            help='the path of config file')
    args = parser.parse_args()
    return vars(args)


def main(config_path):
    warnings.filterwarnings("ignore", message="numpy.dtype size changed")
    warnings.filterwarnings("ignore", message="numpy.ufunc size changed")
    warnings.filterwarnings(
        module='nltk', category=UserWarning,
        message='\nThe hypothesis contains 0 counts of \d-gram overlaps\.',
        action='ignore')
    config = Box.from_yaml(config_path.open())
    torch.cuda.set_device(config.train.device)
    logger = create_logger(name="MAIN")
    logger.info(f'[-] Config loaded from {config_path}')
    logger.info(f'[-] Experiment: {config.test.exp}')

    exp_path = \
        Path(config.data.data_dir) / "exp" / config.model / config.test.exp

    random.seed(config.random_seed)
    np.random.seed(config.random_seed)
    torch.manual_seed(config.random_seed)
    torch.cuda.manual_seed(config.random_seed)
    logger.info('[-] Random seed set to {}'.format(config.random_seed))

    logger.info(f'[*] Initialize {config.model} tester...')
    T = __import__(config.model, fromlist=['tester'])
    tester = T.tester.Tester(config, config.train.device)
    logger.info('[-] Tester initialization completed')
    logger.info('[*] Start testing...')
    tester.test()


if __name__ == "__main__":
    with ipdb.launch_ipdb_on_exception():
        sys.breakpointhook = ipdb.set_trace
        args = parse_args()
        main(**args)

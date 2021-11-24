import random
import numpy as np


def fix_random_seeds(seed: int):
    print(f"fix random seed to {seed}.")
    random.seed(seed)
    np.random.seed(seed)
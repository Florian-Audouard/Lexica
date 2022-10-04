from tqdm import tqdm

import time

with tqdm(total=100) as pbar:
    for _ in range(5):
        time.sleep(1)
        pbar.update(1)

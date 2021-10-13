#

# a simple script to tune things

import multiprocessing
from multiprocessing import Pool, Lock, Manager
import subprocess
import os
import sys
import time
import numpy as np
np.random.seed(12345)

# --
# global lock!
_global_lock = Lock()
manager = multiprocessing.Manager()
Global = manager.Namespace()
Global.idx = 0
Global.gpu_available = ''  # note: cannot be a complex object, which will not be sync
_global_log = "_stdout.log"
# --

# def run_cmd(cmd: str):
#     try:
#         tmp_out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
#         n = 0
#         output = str(tmp_out.decode())  # byte->str
#     except subprocess.CalledProcessError as grepexc:
#         n = grepexc.returncode
#         output = grepexc.output
#     return output

def run_cmd(cmd: str):
    print(f"Run {cmd}")
    return os.system(cmd)

def run_one(arg_str: str):
    # --
    gpu_id = None
    while True:  # not getting resource?
        with _global_lock:
            print(f"{arg_str} {Global.gpu_available}")
            for ii, vv in enumerate(Global.gpu_available):
                if vv == '1':
                    gpu_id = ii
                    break
            if gpu_id is not None:
                _rs = list(Global.gpu_available)
                _rs[gpu_id] = '0'
                Global.gpu_available = ''.join(_rs)  # take it!!
                cur_idx = Global.idx
                Global.idx = Global.idx + 1
                print(f"Claim {gpu_id} with {cur_idx}, currently {Global.gpu_available}")
                break
            else:  # otherwise wait for some time
                print("Resource not found, wait ...")
                time.sleep(10)
    print(f"Start task {cur_idx}: {arg_str}")
    # --
    _log_suffix = '_'.join(''.join(arg_str.split("--")).split())
    run_cmd(f"CUDA_VISIBLE_DEVICES={gpu_id} EXTRA_ARGS='{arg_str} --qa_save_name zmodel{cur_idx}' bash ../train_qa.sh 2>&1 | tee _log{cur_idx}.{_log_suffix}")
    # --
    with _global_lock:
        _rs = list(Global.gpu_available)
        _rs[gpu_id] = '1'
        Global.gpu_available = ''.join(_rs)  # put it back!
        print(f"End task {cur_idx}: {arg_str}")
    # --

def run_them(ranges: list, gpu_ids: list, shuffle=False):
    # --
    # put resources
    _rs = ['0'] * (max(gpu_ids) + 1)
    for ii in gpu_ids:
        _rs[ii] = '1'
    Global.gpu_available = ''.join(_rs)
    # --
    # first expand get all ranges
    all_args = [""]
    for one_ranges in ranges:
        new_all_args = []
        for a in all_args:
            for a2 in one_ranges:
                new_all_args.append(a+" "+a2)
        all_args = new_all_args
    # shuffle them all
    print(f"All tasks = {len(all_args)}")
    if shuffle:
        np.random.shuffle(all_args)
    # run them
    with Pool(len(gpu_ids)) as p:
        p.map(run_one, all_args)
    # --

# --
def main():
    # --
    tune_ranges1013 = [
        [f"--learning_rate {z}" for z in [1e-5, 3e-5, 5e-5]],
        [f"--qa_label_negratio {z}" for z in [5, 10]],
    ]
    # --
    tr = tune_ranges1013
    run_them(tr, [1,2,3])

if __name__ == '__main__':
    main()

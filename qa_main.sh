#!/bin/bash

# note: assume that we are at the root dir of 'opera-TA1-qa'
csr_in=$(readlink -f $1)
csr_out=$(readlink -f $2)
topics=$(readlink -f $3)

SCRIPT_DIR="$( cd "$( dirname ${BASH_SOURCE[0]}  )" && pwd )"
mkdir -p ${csr_out}
python3 ${SCRIPT_DIR}/qa_main.py --model ${SCRIPT_DIR}/zmodel.best --input_topic $topics --input_path $csr_in --output_path $csr_out

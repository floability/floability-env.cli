#!/bin/bash

# Following is a sample execution of this script:
# ./floability-env-cli.sh  --notebook {notebook_path} --kernel {kernel_name}

trap '' SIGINT

helpFunction()
{
   echo "Incorrect command-line usage"
   exit 1
}

while [ "${1:-}" != '' ]; do
    case "$1" in
      '--notebook')
        shift
        notebook=$1 ;;
      '--kernel')
        shift
        kernel=$1 ;;
      '--transform')
        shift
        transform=$1 ;;
        *) helpFunction ;;
    esac
    shift
done

echo "Running the notebook at path: $notebook with kernel: $kernel."
cmd="jupyter notebook --MultiKernelManager.default_kernel_name=$kernel $notebook"
eval "$cmd"
echo "Successfully completed notebook execution and auditing."
trap - SIGINT
cmd="sciunit export e1"
eval "$cmd"

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
      '--password')
        shift
        password=$1 ;;
      '--transform')
        shift
        transform=$1 ;;
        *) helpFunction ;;
    esac
    shift
done

echo "Creating a copy opf notebook $notebook"
# create a copy of the notebook in the current directory with appended _copy
filename=$(basename -- "$notebook")
name="${filename%.*}"
ext="${filename##*.}"
copied_notebook="${name}_copy.${ext}"
cp $notebook $copied_notebook

# Start the strace command in the background
echo "Starting strace for PID $PARENT_PID..."
strace -qqq -r -z -f -o  $(pwd)/strace_worker.txt vine_worker localhost 9123 &
# Capture the PID of the strace process
STRACE_PID=$!

# Wait a moment to ensure strace starts
sleep 1

cmd="pip3 install nbformat pyyaml"
eval "$cmd"

cmd="python code_injection.py $copied_notebook $password $(pwd)/strace_manager.txt"
eval "$cmd"

echo "Running the notebook at path: $copied_notebook with kernel: $kernel."
cmd="jupyter notebook --no-browser --ip=0.0.0.0 --MultiKernelManager.default_kernel_name=$kernel $copied_notebook"
eval "$cmd"
echo "Successfully completed notebook execution and auditing."
trap - SIGINT

# Clean up: Kill the strace process at the end
echo "Stopping strace..."
kill -TERM "$STRACE_PID" 2>/dev/null
sleep 1  # Give it a moment to terminate

# remove the copied notebook
echo "Removing the copied notebook $copied_notebook"
rm -f $(pwd)/$copied_notebook

cmd="python generate_requirements.py $(pwd)/strace_manager.txt $(pwd)/strace_worker.txt"
eval "$cmd"
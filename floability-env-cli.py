# Following is a sample execution of this script:
# python floability-env-cli.py --notebook {notebook_path} --kernel {kernel_name}

import argparse
import shutil
import os
import subprocess
import signal
import time
import nbformat

def get_parsed_arguments():
    """
    Parse command-line arguments for the Floability-ENV CLI.
    """
    parser = argparse.ArgumentParser(
            description="Floability-ENV CLI: Capture dependencies of notebooks in Floability environments."
        )

    parser.add_argument("--notebook", help="path of the notebook file", required=True)
    parser.add_argument("--kernel", help="name of the Jupyter kernel to use", required=True)
    return parser.parse_args()

strace_worker = os.getcwd()+"/strace_worker.txt"
strace_manager = os.getcwd()+"/strace_manager.txt"
open_trace_log = os.getcwd()+"/open_trace.log"

args = get_parsed_arguments()
notebook_path = args.notebook.strip()
kernel_name = args.kernel.strip()

notebook_name = notebook_path.split("/")[-1]
notebook_path_str = '/'.join(notebook_path.split("/")[:-1])
if notebook_path_str != "":
    notebook_copy_path = notebook_path_str + "/copy_" + notebook_name
else:
    notebook_copy_path = "copy_" + notebook_name
shutil.copy(notebook_path, notebook_copy_path)
print("Created temp copy of the notebook: ", notebook_name)

# Add code to the top of the notebook to capture data dependencies
code_to_add = ""
with open("log_data_deps.txt", "r") as f:
    code_to_add = f.read()
    code_to_add = code_to_add.replace("open_trace_log", open_trace_log)

def add_code_to_notebook(notebook_path, code):
    """
    Add code to the top of a Jupyter notebook.
    """
    with open(notebook_path, 'r') as f:
        nb = nbformat.read(f, as_version=4)

    # Create a new code cell
    new_cell = nbformat.v4.new_code_cell(code)
    
    # Insert the new cell at the beginning
    nb.cells.insert(0, new_cell)

    # Write the modified notebook back to the file
    with open(notebook_path, 'w') as f:
        nbformat.write(nb, f)

add_code_to_notebook(notebook_copy_path, code_to_add)
print("Added code to the top of the notebook.")

print("Starting vine workers with strace...")
p_worker = subprocess.Popen(['strace', '-qqq', '-r', '-z', '-f', '-o', strace_worker, '-e', 'trace=openat,fstat,newfstatat', 'vine_worker', 'localhost', '9123'], start_new_session=True)
worker_pid = p_worker.pid
print("worker_pid:", worker_pid)

start = time.time()
# Execute the notebook in background using the specified kernel
print("Starting the notebook with strace... ")
p_manager = subprocess.run(['strace', '-qqq', '-r', '-z', '-f', '-o', strace_manager, '-e', 'trace=openat,fstat,newfstatat', 'jupyter', 'execute', '--ExecutePreprocessor.kernel_name=' + kernel_name, notebook_copy_path])
print("time taken to execute the notebook: ", time.time() - start)

# Remove the copied notebook
os.remove(notebook_copy_path)
print("Removed notebook copy.")

# Shutdown processes
os.killpg(os.getpgid(worker_pid), signal.SIGTERM)
print("Removed vine worker process tree.")

start = time.time()
# Find the dependencies and generate YAML file
p = subprocess.Popen(['python', 'generate_requirements.py', strace_manager, strace_worker])
p.wait()

# Generate verified YAML files for worker and manager
p = subprocess.Popen(['python', 'generate_verified_env_yaml.py', '-r', 'worker_requirements.txt', '-o', 'worker_environment.yml'])
p.wait()

p = subprocess.Popen(['python', 'generate_verified_env_yaml.py', '-r', 'manager_requirements.txt', '-o', 'manager_environment.yml'])
p.wait()
print("Generated verified YAML files for worker and manager.")

print("time taken to generate verified YAML files: ", time.time() - start)

start = time.time()
# Find data dependencies and generate TXT file
p = subprocess.Popen(['python', 'generate_data_deps.py', open_trace_log])
p.wait()
print("time taken to generate data dep file: ", time.time() - start)

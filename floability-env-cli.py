# Following is a sample execution of this script:
# python floability-env-cli.py  --notebook {notebook_path}

import argparse
import shutil
import os
import subprocess
import signal

def get_parsed_arguments():
    """
    Parse command-line arguments for the Floability-ENV CLI.
    """
    parser = argparse.ArgumentParser(
            description="Floability-ENV CLI: Capture dependencies of notebooks in Floability environments."
        )

    parser.add_argument("--notebook", help="path of the notebook file")
    return parser.parse_args()

strace_worker = os.getcwd()+"/strace_worker.txt"
strace_manager = os.getcwd()+"/strace_manager.txt"
open_trace_log = os.getcwd()+"/open_trace.log"

args = get_parsed_arguments()
if args.notebook:
    notebook_path = args.notebook.strip()

notebook_name = notebook_path.split("/")[-1]
notebook_path_str = '/'.join(notebook_path.split("/")[:-1])
if notebook_path_str != "":
	notebook_copy_path = notebook_path_str + "/copy_" + notebook_name
else:
	notebook_copy_path = "copy_" + notebook_name
shutil.copy(notebook_path, notebook_copy_path)
print("Created temp copy of the notebook: ", notebook_name)

# add code to the top of the notebook to capture data depencies
code_to_add = f"""
import builtins
import os

log_file = "{open_trace_log}"
if os.path.exists(log_file):
    os.remove(log_file)

def open(file, mode='r', *args, **kwargs):
    with builtins.open(log_file, "a") as log:
        log.write(file + "\\n")
    return builtins.open(file, mode, *args, **kwargs)

original_open = builtins.open
def traced_open(file, mode='r', *args, **kwargs):
    with original_open(log_file, "a") as log:
        log.write(file + "\\n")
    return original_open(file, mode, *args, **kwargs)
builtins.open = traced_open
"""

# use nbformat to add the code to the top of the notebook
import nbformat

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
p_worker = subprocess.Popen(['strace', '-qqq', '-r', '-z', '-f', '-o', strace_worker, 'vine_worker', 'localhost', '9123'], start_new_session=True)
worker_pid = p_worker.pid
print("worker_pid:", worker_pid)

# execute the notebook in background
print("Starting the notebook with strace... ")
p_manager = subprocess.run(['strace', '-qqq', '-r', '-z', '-f', '-o', strace_manager, 'jupyter', 'execute', notebook_copy_path])

# remove the copied notebook
os.remove(notebook_copy_path)
print("Removed notebook copy.")

# shutdown processes
os.killpg(os.getpgid(worker_pid), signal.SIGTERM)
print("Removed vine worker process tree.")

# find the dependencies and geneate yaml file
p = subprocess.Popen(['python', 'generate_requirements.py', strace_manager, strace_worker])
p.wait()


# find data dependencies and generate txt file
p = subprocess.Popen(['python', 'generate_data_dep.py', open_trace_log])
p.wait()
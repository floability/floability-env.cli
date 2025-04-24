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

args = get_parsed_arguments()
if args.notebook:
    notebook_path = args.notebook.strip()

notebook_name = notebook_path.split("/")[-1]
notebook_copy_path = os.getcwd()+"/copy_" + notebook_name
shutil.copy(notebook_path, notebook_copy_path)
print("Created temp copy of the notebook: ", notebook_name)

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
print("Created environment.yml")

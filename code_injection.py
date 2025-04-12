import nbformat

def add_code_cells(notebook_path, top_code, end_code, output_path=None):
    
    try:
        with open(notebook_path, 'r') as f:
            nb = nbformat.read(f, as_version=4)
        
        top_cell = nbformat.v4.new_code_cell(source=top_code)
        end_cell = nbformat.v4.new_code_cell(source=end_code)
        
        if "cells" not in nb or not nb.cells:
            nb.cells = [top_cell, end_cell]  # If empty, add both
        else:
            # Insert at top (index 0) and append at end
            nb.cells.insert(0, top_cell)
            nb.cells.append(end_cell)
        
        # Save the modified notebook
        output_path = output_path or notebook_path
        with open(output_path, 'w') as f:
            nbformat.write(nb, f)
        print(f"Added cells to top and end of {output_path}")
        
    except FileNotFoundError:
        print(f"Error: Notebook '{notebook_path}' not found")
    except Exception as e:
        print(f"Error adding cells: {str(e)}")


top_code = """\
import subprocess
import os
import time

# Get the kernel PID
mgr_parent_pid = os.getpid()
print(f"Kernel PID: {mgr_parent_pid}")

# Define the strace command
strace_cmd = [
    "sudo", "-S",  # -S reads password from stdin
    "strace",
    "-qqq",  
    "-r",   
    "-z",  
    "-f",    # Follow forks/threads
    "-o", "strace_manager_file", 
    "-p", str(mgr_parent_pid),
]

# Start strace in the background with sudo
mgr_strace = subprocess.Popen(
    strace_cmd,
    stdin=subprocess.PIPE,  # Enable stdin for password
    stdout=subprocess.PIPE,  
    stderr=subprocess.PIPE, 
    preexec_fn=os.setsid
)

# Send the sudo password
password = "dummy_password"  # Replace with your actual password
mgr_strace.stdin.write(password.encode() + b"\\n")  # Encode and add newline
mgr_strace.stdin.flush() 

print("strace is running in the background. Execute your cells now!")

time.sleep(1)
mgr_strace.stdin.close()

from functools import wraps
def worker(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with open('_tmp.txt', 'w') as f: 
            f.write('hello1')
            result = func(*args, **kwargs)
            f.write('hello2')
            print(result)
            return result
    return wrapper
"""

end_code = """\
import signal

try:
    # Terminate the process group (sudo and strace)
    os.killpg(os.getpgid(mgr_strace.pid), signal.SIGTERM)
    mgr_strace.wait(timeout=5)
    print(f"strace group terminated, exit code: {mgr_strace.returncode}")
except subprocess.TimeoutExpired:
    print("Graceful termination timed out, forcing kill")
    # Kill the process group
    os.killpg(os.getpgid(mgr_strace.pid), signal.SIGKILL)
    mgr_strace.wait()
    # Double-check strace is gone
    #subprocess.run(f"sudo pkill -f 'strace -p {mgr_parent_pid}'", shell=True)
    print("strace group killed")
"""

import sys

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python add_cells.py <notebook_path> <sudo_password>")
        sys.exit(1)
    notebook_path = sys.argv[1]
    password = sys.argv[2]
    path = sys.argv[3]
    # Update the password in the top_code
    top_code = top_code.replace('dummy_password', password)
    top_code = top_code.replace('strace_manager_file', path)
    # Call the function to add cells
    add_code_cells(notebook_path, top_code, end_code)
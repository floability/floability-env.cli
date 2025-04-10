import os
import re

def process_strace_log(file_path):
    manager_packages = []
    worker_packages = []
    seen_manager = set()
    seen_worker = set()
    
    before_first_open = True
    between_opens = False
    
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Check for the delimiter file "_tmp.txt"
                if 'openat' in line and '_tmp.txt' in line:
                    if before_first_open:
                        before_first_open = False  # End manager phase
                        between_opens = True       # Start worker phase
                    elif between_opens:
                        between_opens = False      # End worker phase
                    continue
                
                # Skip lines without 'openat' or 'site-packages'
                if 'openat' not in line or 'site-packages' not in line:
                    continue
                    
                try:
                    start = line.index('"') + 1
                    end = line.index('"', start)
                    full_path = line[start:end]
                    path_parts = full_path.split('/')
                    
                    try:
                        site_packages_idx = path_parts.index('site-packages')
                        if site_packages_idx + 1 < len(path_parts):
                            package_name = path_parts[site_packages_idx + 1]
                            
                            # Skip if there's nothing after the package name
                            if site_packages_idx + 2 >= len(path_parts):
                                continue  # Path ends at package directory (e.g., /site-packages/_distutils_hack)
                            
                            package_dir = '/'.join(path_parts[:site_packages_idx + 2])
                            
                            # Determine which list to add to based on phase
                            if before_first_open:
                                if package_name not in seen_manager:
                                    seen_manager.add(package_name)
                                    version = find_package_version(package_dir)
                                    package_entry = {
                                        'package': package_name,
                                        'path': package_dir,
                                        'version': version if version else 'Not found'
                                    }
                                    manager_packages.append(package_entry)
                            elif between_opens:
                                if package_name not in seen_worker:
                                    seen_worker.add(package_name)
                                    version = find_package_version(package_dir)
                                    package_entry = {
                                        'package': package_name,
                                        'path': package_dir,
                                        'version': version if version else 'Not found'
                                    }
                                    worker_packages.append(package_entry)
                    except ValueError:
                        continue
                        
                except ValueError:
                    continue
                    
        return manager_packages, worker_packages
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return [], []
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        return [], []

def find_package_version(package_dir):
    try:
        for (dirpath, dirnames, filenames) in os.walk(package_dir):
            potential_files = [f for f in filenames if 'version' in f.lower()] + ['__init__.py']
            
            for version_file in potential_files:
                if version_file in filenames:
                    try:
                        with open(os.path.join(dirpath, version_file), 'r') as f:
                            lines = f.readlines()
                            for line in lines:
                                version_match = re.search(r'^_*version_*\s*=[\s]*[\'"]([^\'"]+)[\'"]', line)
                                if version_match:
                                    version = version_match.group(1).strip()
                                    if version and version[0].isdigit():
                                        return version
                    except Exception as e:
                        print(f"Error reading {version_file} in {dirpath}: {str(e)}")
                        continue
            break
        return None
        
    except Exception as e:
        print(f"Error finding version for {package_dir}: {str(e)}")
        return None

def generate_requirements_txt(manager_packages, worker_packages, output_file="requirements.txt"):
    """Generate a single requirements.txt with manager and worker sections"""
    try:
        with open(output_file, 'w') as f:
            # Manager requirements
            f.write("# Manager Requirements\n")
            for entry in manager_packages:
                package = entry['package']
                version = entry['version']
                if version and version != 'Not found':
                    f.write(f"{package}=={version}\n")
                else:
                    f.write(f"{package}\n")
            
            # Separator
            f.write("\n# Worker Requirements\n")
            
            # Worker requirements
            for entry in worker_packages:
                package = entry['package']
                version = entry['version']
                if version and version != 'Not found':
                    f.write(f"{package}=={version}\n")
                else:
                    f.write(f"{package}\n")
                    
        print(f"Generated {output_file} successfully")
    except Exception as e:
        print(f"Error generating requirements.txt: {str(e)}")

def main():
    log_file = "strace_manager.txt"
    manager_packages, worker_packages = process_strace_log(log_file)
    
    if manager_packages or worker_packages:
        print("Manager Packages:")
        for entry in manager_packages:
            print(f"Package: {entry['package']}")
            print(f"Path: {entry['path']}")
            print(f"Version: {entry['version']}")
            print("---")
            
        print("Worker Packages:")
        for entry in worker_packages:
            print(f"Package: {entry['package']}")
            print(f"Path: {entry['path']}")
            print(f"Version: {entry['version']}")
            print("---")
        
        # Generate requirements.txt with both sections
        generate_requirements_txt(manager_packages, worker_packages)
    else:
        print("No packages found or error occurred")

if __name__ == "__main__":
    main()
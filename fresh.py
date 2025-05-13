#!/usr/bin/env python3
import os
import shutil
import subprocess
import tempfile
import sys

def run_command(command):
    print(f"Running: {command}")
    process = subprocess.run(command, shell=True, check=True)
    return process

def main():
    # Check if docker-compose.yaml and Dockerfile exist in current directory
    current_docker_compose = os.path.exists("docker-compose.yaml")
    current_dockerfile = os.path.exists("Dockerfile")
    
    if current_docker_compose:
        print("Keeping existing docker-compose.yaml")
    
    if current_dockerfile:
        print("Keeping existing Dockerfile")

    # Create a temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        # Clone the repository
        repo_url = "https://github.com/open-webui/open-webui.git"
        clone_cmd = f"git clone {repo_url} {temp_dir}"
        try:
            run_command(clone_cmd)
        except subprocess.CalledProcessError:
            print("Failed to clone the repository")
            return 1

        # Files to copy (excluding docker-compose.yaml and Dockerfile if they exist)
        docker_files = [".dockerignore", "backend/.dockerignore"]
        
        # Only add these files if they don't exist in current directory
        if not current_docker_compose:
            docker_files.append("docker-compose.yaml")
        
        if not current_dockerfile:
            docker_files.append("Dockerfile")

        # Create necessary directories
        os.makedirs("backend", exist_ok=True)
        
        # Copy the Docker-related files
        for file in docker_files:
            src_path = os.path.join(temp_dir, file)
            if os.path.exists(src_path):
                # Ensure target directory exists
                if '/' in file:
                    dir_path = os.path.dirname(file)
                    os.makedirs(dir_path, exist_ok=True)
                
                # Copy the file
                shutil.copy2(src_path, file)
                print(f"Copied {file}")
            else:
                print(f"Warning: File {file} not found in the repository")

        # Clone the backend directory
        backend_src = os.path.join(temp_dir, "backend")
        if os.path.exists(backend_src):
            # Copy requirements.txt
            req_file = os.path.join(backend_src, "requirements.txt")
            if os.path.exists(req_file):
                shutil.copy2(req_file, "backend/requirements.txt")
                print("Copied backend/requirements.txt")
            else:
                print("Warning: requirements.txt not found in the backend directory")
            
            # Copy start.sh
            start_file = os.path.join(backend_src, "start.sh")
            if os.path.exists(start_file):
                shutil.copy2(start_file, "backend/start.sh")
                print("Copied backend/start.sh")
            else:
                print("Warning: start.sh not found in the backend directory")
                
            # Create data directory
            os.makedirs("backend/data", exist_ok=True)
            print("Created backend/data directory")
            
            # Copy the open_webui directory
            open_webui_src = os.path.join(backend_src, "open_webui")
            if os.path.exists(open_webui_src):
                shutil.copytree(open_webui_src, "backend/open_webui", dirs_exist_ok=True)
                print("Copied backend/open_webui directory")
            else:
                print("Warning: open_webui directory not found in the backend directory")
        else:
            print("Warning: backend directory not found in the repository")

    print("\nFresh clone completed! Docker-related files and backend code have been kept.")
    print("Existing docker-compose.yaml and Dockerfile were preserved.")
    print("To build and run the containers, use: docker-compose up -d")
    return 0

if __name__ == "__main__":
    sys.exit(main())


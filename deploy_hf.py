"""Deploy overworker to Hugging Face Spaces."""
import os
from huggingface_hub import HfApi, HfFolder
import shutil

# Set the token from environment variable
token = os.getenv("HF_TOKEN")
if not token:
    raise ValueError("HF_TOKEN environment variable not set")
HfFolder.save_token(token)

api = HfApi()

# Space configuration
space_id = "luguog/overworker"
space_name = "overworker"

# Try to create the space
try:
    print(f"Creating Space: {space_id}")
    api.create_repo(
        repo_id=space_id,
        repo_type="space",
        space_sdk="gradio",
        private=False,
        token=token
    )
    print(f"Space created successfully: https://huggingface.co/spaces/{space_id}")
except Exception as e:
    if "already exists" in str(e).lower() or "already created" in str(e).lower() or "already created this space repo" in str(e).lower():
        print(f"Space already exists: {space_id}")
        print("Proceeding with file upload...")
    else:
        print(f"Error creating space: {e}")
        print("Please create the space manually at: https://huggingface.co/spaces/new")
        print("Choose 'Gradio' as SDK and name it 'overworker'")
        print("")
        print("Your Hugging Face username: luguog")
        print("Space will be: https://huggingface.co/spaces/luguog/overworker")
        print("")
        print("After creating the space, run this script again.")
        exit(1)
print("")

# Files to upload (minimal viable set)
files_to_upload = [
    "main.py",
    "requirements.txt",
    "Dockerfile",
]

# Upload all project files
all_files = []
for root, dirs, files in os.walk("."):
    # Skip .git, __pycache__, .venv, node_modules
    dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.venv', 'node_modules', '.pytest_cache']]
    for file in files:
        if file.endswith('.py') or file.endswith('.txt') or file.endswith('.md') or file.endswith('.html') or file.endswith('.json') or file.endswith('.yaml'):
            file_path = os.path.join(root, file)
            if file_path.startswith('./'):
                file_path = file_path[2:]
            all_files.append(file_path)

# Upload all files (skip deploy_hf.py to avoid token exposure)
print(f"\nUploading {len(all_files)} files to Space...")
for file_path in all_files:
    if file_path == "deploy_hf.py":
        continue  # Skip deployment script to avoid token exposure
    if os.path.exists(file_path):
        try:
            api.upload_file(
                path_or_fileobj=file_path,
                path_in_repo=file_path,
                repo_id=space_id,
                repo_type="space",
                token=token
            )
            print(f"✓ Uploaded: {file_path}")
        except Exception as e:
            print(f"✗ Failed to upload {file_path}: {e}")

# Upload files
print("\nUploading files to Space...")
for file in files_to_upload:
    if os.path.exists(file):
        try:
            api.upload_file(
                path_or_fileobj=file,
                path_in_repo=file,
                repo_id=space_id,
                repo_type="space",
                token=token
            )
            print(f"✓ Uploaded: {file}")
        except Exception as e:
            print(f"✗ Failed to upload {file}: {e}")
    else:
        print(f"✗ File not found: {file}")

# Upload tests directory
if os.path.exists("tests"):
    for root, dirs, files in os.walk("tests"):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, "tests")
            repo_path = f"tests/{rel_path}"
            try:
                api.upload_file(
                    path_or_fileobj=file_path,
                    path_in_repo=repo_path,
                    repo_id=space_id,
                    repo_type="space",
                    token=token
                )
                print(f"✓ Uploaded: {repo_path}")
            except Exception as e:
                print(f"✗ Failed to upload {repo_path}: {e}")

print(f"\n✓ Deployment complete!")
print(f"View your Space at: https://huggingface.co/spaces/{space_id}")

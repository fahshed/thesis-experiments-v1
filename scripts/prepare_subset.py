import os
import shutil
import random

def create_random_subset(source_dir: str, target_dir: str, num_samples: int = 50):
    """
    Randomly selects a subset of applicant directories and copies them to a new target folder.
    """
    if not os.path.exists(source_dir):
        print(f"Error: Directory '{source_dir}' does not exist.")
        return

    # Ensure target exists
    os.makedirs(target_dir, exist_ok=True)
    
    # Get all subdirectories (applicants)
    applicants = [d for d in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, d))]
    print(f"Found {len(applicants)} total applicants in {source_dir}.")
    
    if len(applicants) < num_samples:
        print(f"Warning: Only found {len(applicants)} applicants. Copying all of them.")
        num_samples = len(applicants)
        
    # Randomly sample
    selected_applicants = random.sample(applicants, num_samples)
    print(f"Randomly selected {num_samples} applicants. Copying files...")
    
    copied_count = 0
    for app in selected_applicants:
        src_path = os.path.join(source_dir, app)
        dst_path = os.path.join(target_dir, app)
        
        # Copy the directory and its contents
        if not os.path.exists(dst_path):
            shutil.copytree(src_path, dst_path)
            copied_count += 1
            
    print(f"Successfully copied {copied_count} applicants to {target_dir}!")

if __name__ == "__main__":
    SOURCE = "dataset/clean_matches"
    TARGET = "dataset/clean_matches_50"
    
    print("Preparing 50-CV Subset...")
    create_random_subset(SOURCE, TARGET, num_samples=50)

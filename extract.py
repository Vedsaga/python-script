import argparse
import os
import shutil
import tarfile

def extract_tar_gz(file_path, extract_path, filenames=None):
    with tarfile.open(file_path, "r:gz") as tar:
        if filenames:
            tar.extractall(path=extract_path, members=[tar.getmember(f) for f in filenames])
        else:
            tar.extractall(path=extract_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract files from a .tar.gz archive')
    parser.add_argument('input_file', type=str, help='Path to input .tar.gz file')
    args = parser.parse_args()

    input_file = args.input_file

    # Extract file name without the extension
    output_dir = os.path.splitext(os.path.basename(input_file))[0]

    # If output directory already exists, delete it
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)

    # Create the output directory
    os.makedirs(output_dir)

    # Extract files to the output directory
    extract_tar_gz(input_file, output_dir)

    # Flatten the directory structure
    for dirpath, _, filenames in os.walk(output_dir):
        for filename in filenames:
            src_path = os.path.join(dirpath, filename)
            dst_path = os.path.join(output_dir, filename)
            shutil.move(src_path, dst_path)

    # Remove empty directories
    for dirpath, dirnames, _ in os.walk(output_dir, topdown=False):
        for dirname in dirnames:
            os.rmdir(os.path.join(dirpath, dirname))

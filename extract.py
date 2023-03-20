import argparse
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
    parser.add_argument('output_dir', type=str, help='Path to output directory')
    parser.add_argument('--filenames', nargs='+', help='List of filenames to extract')
    args = parser.parse_args()

    input_file = args.input_file
    output_dir = args.output_dir
    filenames = args.filenames

    extract_tar_gz(input_file, output_dir, filenames)

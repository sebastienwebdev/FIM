import hashlib
import os
from time import sleep, strftime
from getpass import getuser

def calculate_file_hash(filepath):
    """Calculate the SHA512 hash of a file."""
    hash_sha512 = hashlib.sha512()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha512.update(chunk)
    return hash_sha512.hexdigest()

def erase_baseline_if_already_exists():
    """Delete baseline.txt if it exists."""
    if os.path.exists('baseline.txt'):
        os.remove('baseline.txt')

def collect_new_baseline():
    """Collect a new baseline of file hashes, ignoring certain file types."""
    erase_baseline_if_already_exists()
    files_directory = './Files'
    if not os.path.exists(files_directory):
        os.makedirs(files_directory)
    files = [f for f in os.listdir(files_directory) if os.path.isfile(os.path.join(files_directory, f)) and not f.startswith('.')]
    with open('baseline.txt', 'a') as baseline_file:
        for f in files:
            file_path = os.path.join(files_directory, f)
            file_hash = calculate_file_hash(file_path)
            baseline_file.write(f"{file_path}|{file_hash}\n")

def audit_log(message):
    """Write a message to the audit log with a timestamp and user information."""
    with open("audit_log.txt", "a") as log_file:
        timestamp = strftime("%Y-%m-%d %H:%M:%S")
        user = getuser()
        log_file.write(f"[{timestamp}][User: {user}] {message}\n")

def begin_monitoring():
    """Monitor files for changes, deletions, and new copies based on the saved baseline, including detailed audit logs."""
    file_hash_dictionary = {}
    with open('baseline.txt', 'r') as baseline_file:
        for line in baseline_file:
            path, hash_value = line.strip().split('|')
            file_hash_dictionary[path] = hash_value

    while True:
        sleep(1)
        observed_files = set(f for f in os.listdir('./Files') if not f.startswith('.'))
        baseline_files = set(file_hash_dictionary.keys())
        current_files = [os.path.join('./Files', f) for f in observed_files]

        # Check for new or changed files
        for file_path in current_files:
            if file_path not in baseline_files:
                print(f"{file_path} has been added!", flush=True)
                audit_log(f"File added: {file_path}")
                # Update dictionary with new file hash
                file_hash_dictionary[file_path] = calculate_file_hash(file_path)
            else:
                file_hash = calculate_file_hash(file_path)
                if file_hash_dictionary[file_path] != file_hash:
                    print(f"{file_path} has been modified.", flush=True)
                    audit_log(f"File modified: {file_path}")
                    # Update dictionary to reflect changes
                    file_hash_dictionary[file_path] = file_hash

        # Check for deleted files
        deleted_files = baseline_files - set(current_files)
        for file_path in deleted_files:
            print(f"{file_path} has been deleted.", flush=True)
            audit_log(f"File deleted: {file_path}")
            # Remove from dictionary
            del file_hash_dictionary[file_path]

def main():
    print("\nWhat would you like to do?\n")
    print("    A) Collect new Baseline?")
    print("    B) Begin monitoring files with saved Baseline?\n")
    response = input("Please enter 'A' or 'B': ").upper()

    if response == 'A':
        collect_new_baseline()
    elif response == 'B':
        begin_monitoring()

if __name__ == "__main__":
    main()

import subprocess
import os

# get current directory
main_dir = os.path.dirname(os.path.abspath(__file__))
setup_shell_path = os.path.join(main_dir, 'setup_script.sh')

if not os.path.exists(setup_shell_path):
    print('Shell script does not exist.')
    exit(1)

if not os.access(setup_shell_path, os.X_OK):
    print('Shell script is not executable.')
    exit(1)


def create_lock_file():
    lock_file = os.path.join(main_dir, 'update.lock')
    with open(lock_file, 'w') as f:
        f.write('')


def remove_lock_file():
    lock_file = os.path.join(main_dir, 'update.lock')
    os.remove(lock_file)


if __name__ == '__main__':
    command = ["sudo", "/bin/bash", setup_shell_path]
    create_lock_file()
    subprocess.run(command)
    remove_lock_file()

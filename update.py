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


if __name__ == '__main__':
    command = ["sudo", "/bin/bash", setup_shell_path]
    subprocess.run(command)

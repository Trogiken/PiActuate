import subprocess
import pkg_resources
import shutil
import os

# get current directory
main_dir = os.path.dirname(os.path.realpath(__file__))
setup_shell_path = os.path.join(main_dir, 'setup_script.sh')

if not os.path.exists(setup_shell_path):
    print('Shell script does not exist.')
    exit(1)

if not os.access(setup_shell_path, os.X_OK):
    print('Shell script is not executable.')
    exit(1)

static_files_path = os.path.join(main_dir, 'webui', 'staticfiles')
if os.path.exists(static_files_path):
    print('Removing static files...')
    shutil.rmtree(static_files_path)


def get_package_location(package_name):
    try:
        dist = pkg_resources.get_distribution(package_name)
        return dist.location
    except pkg_resources.DistributionNotFound:
        return None


def write_update_log(msg: str):
    with open(os.path.join(main_dir, 'update.log'), 'w') as f:
        f.write(f"""More specifc update logs are stored in '{get_package_location("pyupgrader")}'\n""")
        f.write(msg)


if __name__ == '__main__':
    command = ["/bin/bash", setup_shell_path]
    command.append(0, "sudo")
    os.system("sudo apt-get update && sudo apt-get upgrade -y")

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        write_update_log(result.stdout)
        print('Shell script finished running, rebooting...')
        os.system("sudo reboot")
    except subprocess.CalledProcessError as e:
        print('Shell script did not finish successfully.')
        print('Output:', e.output)
        print('Error:', e.stderr)
        write_update_log(e.stderr)

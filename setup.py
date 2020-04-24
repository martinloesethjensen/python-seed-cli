import fileinput
import os
import shlex
import shutil
import subprocess
from pathlib import Path

OLD_SEED_MODULE = "Android-Seed"
APP_BUILD_GRADLE = "/app/build.gradle"
APP_NAME_CHANGE = "APP_NAME_CHANGE"
KEYSTORE_PASSWORD = "KEYSTORE_PASSWORD"
KEYSTORE_ALIAS = "KEYSTORE_ALIAS"
SEED_PACKAGE_NAME = "dk.adaptmobile.android_seed"
APP_SRC_PATH = "/app/src/main/java"
GITHUB_ORG = "adaptdk"
BITRISE_PROJECT_LOCATION_PLACEHOLDER = "SEED_PROJECT_NAME"
BITRISE_YAML_FILE = "bitrise.yml"
BITRISE_ORG = "org id"


def find_and_replace(find, replace, file_name):
    with fileinput.FileInput(file_name, inplace=True) as file:
        for line in file:
            print(line.replace(replace, find), end='')


def find_replace_in_dir(directory, find, replace):
    for path, dirs, files in os.walk(os.path.abspath(directory)):
        for filename in files:
            if filename.endswith(('.kt', '.xml', '.gradle')):
                filepath = os.path.join(path, filename)
                with open(filepath) as file:
                    file_text = file.read()
                file_text = file_text.replace(find, replace)
                with open(filepath, "w") as file:
                    file.write(file_text)


def move_folder(source, destination, avoid_folders=()):
    for _, dirs, files in os.walk(os.path.abspath(source)):
        for avoid_folder in avoid_folders:
            if avoid_folder in dirs:
                dirs.remove(avoid_folder)
        for _dir in dirs:
            shutil.move('{0}/{1}'.format(source, _dir), destination)
        for _file in files:
            shutil.move('{0}/{1}'.format(source, _file), destination)


def dynamic_folder_structure(seed_package_name_split, new_package_name_split):
    old_package_count = len(seed_package_name_split)
    new_package_count = len(new_package_name_split)

    ranger = range(old_package_count) if old_package_count >= new_package_count else range(new_package_count)
    count_condition = old_package_count if old_package_count <= new_package_count else new_package_count

    avoid_folders = []
    cwd = ""
    folder = ""
    for i in ranger:
        if i < count_condition:
            os.rename(seed_package_name_split[i], new_package_name_split[i])
            os.chdir(new_package_name_split[i])
            cwd = os.getcwd()
            folder = cwd
        elif i > old_package_count - 1:
            avoid_folders.append(new_package_name_split[i])
            folder += "/" + new_package_name_split[i]
            os.mkdir(folder)
            if i == new_package_count - 1:
                move_folder(source=cwd, destination=folder, avoid_folders=avoid_folders)
            else:
                os.chdir(new_package_name_split[i])
        else:
            source = '{0}/{1}'.format(cwd, seed_package_name_split[i])
            move_folder(source=source, destination=cwd)
            os.rmdir(source)


# This generates the keystore without the keytool cli.
def generate_keystore():
    os.chdir("launch")
    cmd = f'keytool -genkey -v -keystore release.keystore -keyalg RSA -keysize 4096 -validity 10000 -alias {alias} -dname "cn=Unknown, ou=Unknown, o=Unknown, c=Unknown" -storepass {password} -keypass {password}'
    args = shlex.split(cmd)
    subprocess.Popen(args)
    os.chdir("..")
    print("Will take some time to do this process, please wait for a while...")


def rename_package_dirs():
    os.chdir(project_module + APP_SRC_PATH)
    dynamic_folder_structure(SEED_PACKAGE_NAME.split("."), package_name.split("."))
    os.chdir(project_module_path)
    find_replace_in_dir(os.getcwd(), SEED_PACKAGE_NAME, package_name)
    os.chdir('..')


def rename_app_name():
    find_and_replace(find=app_name, replace=APP_NAME_CHANGE, file_name=project_module + APP_BUILD_GRADLE)
    print(f'Changed app_name to {app_name}')


def rename_project_module():
    os.rename(OLD_SEED_MODULE, project_module)
    print(f'Renamed project module to {project_module}')


def rename_keystore_fields():
    find_and_replace(find=alias, replace=KEYSTORE_ALIAS, file_name=project_module + APP_BUILD_GRADLE)
    find_and_replace(find=password, replace=KEYSTORE_PASSWORD, file_name=project_module + APP_BUILD_GRADLE)


def create_private_repo():
    subprocess.run(["hub", "create", "--private", "{org}/{repo_name}".format(org=GITHUB_ORG, repo_name=project_module)])


def change_remote_url():
    subprocess.run(
        ["git", "remote", "set-url", "origin",
         "git@github.com:{org}/{repo_name}.git".format(org=GITHUB_ORG, repo_name=project_module)])
    print(f'Changed remote origin url to: ')
    subprocess.run(["git", "remote", "--verbose"])


def initial_commit():
    subprocess.run(["git", "add", "--all"])
    subprocess.run(["git", "commit", "-m", "Initial commit"])  # TODO: Could take on a commit message 🤔
    subprocess.run(["git", "push", "-u", "origin", "master"])


def setup_branch(branch):
    subprocess.run(["git", "checkout", "-b", branch])
    print(f'Changed branch to: ')
    subprocess.run(["git", "branch"])
    subprocess.run(["git", "push", "--set-upstream", "origin", branch])


def rename_bitrise_project_location_placeholder():
    find_and_replace(find=project_module, replace=BITRISE_PROJECT_LOCATION_PLACEHOLDER, file_name=BITRISE_YAML_FILE)
    print(f'Changed Bitrise PROJECT_LOCATION to: {project_module}')


def read_bitrise_token() -> str:
    home = str(Path.home())
    filename = f'{home}/.am_seed_token'
    mode = "r" if os.path.isfile(filename) and os.path.getsize(filename) else "w"

    with open(filename, mode) as file:
        filesize = os.path.getsize(filename)

        # Save token from input into the created file
        if filesize == 0 or mode == "w":
            bitrise_token = input("Enter Bitrise api token: ")
            file.write(f'{bitrise_token}')
        else:
            # Read token from existing file that is not empty
            bitrise_token = file.read()

        file.close()

        return bitrise_token


def setup_bitrise():
    cmd = f'bash -c "bash <(curl -sfL "https://raw.githubusercontent.com/bitrise-io/bitrise-add-new-project/master/_scripts/run.sh") --api-token "{bitrise_api_token}" --org "{BITRISE_ORG}" --public "false" --website"'
    args = shlex.split(cmd)
    subprocess.run(args)


if __name__ == '__main__':
    project_module = input("Name project module: ").replace(" ", "-")
    rename_project_module()

    rename_bitrise_project_location_placeholder()

    project_module_path = "{0}/{1}".format(os.getcwd(), project_module)

    app_name = input("What's the app name: ")
    rename_app_name()

    package_name = input("Enter new package name like -> dk.adaptmobile.android_seed: ")
    rename_package_dirs()

    alias = input("Alias for the keystore: ")
    password = input("Password for the keystore: ")
    rename_keystore_fields()
    generate_keystore()

    create_private_repo()

    change_remote_url()

    os.remove("setup.py")

    initial_commit()
    setup_branch("stage")
    setup_branch("develop")

    bitrise_api_token = read_bitrise_token()

    setup_bitrise()

import os
import shlex
import subprocess

from consts import \
    APP_BUILD_GRADLE, \
    APP_JAVA_PATH, \
    APP_NAME_CHANGE, \
    OLD_SEED_MODULE, \
    SEED_PACKAGE_NAME, \
    KEYSTORE_ALIAS, \
    KEYSTORE_PASSWORD, \
    GITHUB_ORG
from helpers import find_replace_in_dir, find_and_replace, dynamic_folder_structure


# This generates the keystore without the keytool cli.
def generate_keystore():
    os.chdir("launch")
    cmd = f'keytool -genkey -v -keystore release.keystore -keyalg RSA -keysize 16384 -validity 10000 -alias {alias} -dname "cn=Unknown, ou=Unknown, o=Unknown, c=Unknown" -storepass {password} -keypass {password}'
    args = shlex.split(cmd)
    subprocess.Popen(args)
    os.chdir("..")
    print("Will take some time to do this process, please wait a few minutes")


def rename_package_dirs():
    os.chdir(project_module + APP_JAVA_PATH)

    dynamic_folder_structure(SEED_PACKAGE_NAME.split("."), package_name.split("."))

    print("Current working directory: " + os.getcwd())
    os.chdir(project_module_path)
    print("Changed directory to: " + os.getcwd())
    find_replace_in_dir(os.getcwd(), SEED_PACKAGE_NAME, package_name)
    os.chdir('..')
    print("Changed directory to: " + os.getcwd())


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
    subprocess.run(["hub", "create", "--private", "adaptdk/{repo_name}".format(repo_name=project_module)])


def change_remote_url():
    subprocess.run(
        ["git", "remote", "set-url", "origin",
         "git@github.com:{org}/{repo_name}.git".format(org=GITHUB_ORG, repo_name=project_module)])
    print(f'Changed remote origin url to: ')
    subprocess.run(["git", "remote", "--verbose"])


if __name__ == '__main__':
    project_module = input("Name project module: ")
    rename_project_module()

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
    os.remove("consts.py")
    os.remove("helpers.py")

import fileinput
import os
import shlex
import subprocess

OLD_SEED_MODULE = "Android-Seed"
APP_BUILD_GRADLE = "/app/build.gradle"
APP_NAME_CHANGE = "APP_NAME_CHANGE"
KEYSTORE_PASSWORD = "KEYSTORE_PASSWORD"
KEYSTORE_ALIAS = "KEYSTORE_ALIAS"
SEED_PACKAGE_NAME = "dk.adaptmobile.android_seed"
APP_JAVA_PATH = "/app/src/main/java"
GITHUB_ORG = "adaptdk"


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


# This generates the keystore without the keytool cli.
def generate_keystore():
    os.chdir("launch")
    cmd = f'keytool -genkey -v -keystore release.keystore -keyalg RSA -keysize 16384 -validity 10000 -alias {alias} -dname "cn=Unknown, ou=Unknown, o=Unknown, c=Unknown" -storepass {password} -keypass {password}'
    args = shlex.split(cmd)
    subprocess.Popen(args)
    os.chdir("..")
    print("Will take some time to do this process, please wait a few minutes")


def rename_package_dirs():
    os.chdir(root_module + APP_JAVA_PATH)

    seed_package_name_split = SEED_PACKAGE_NAME.split(".")
    new_package_name_split = package_name.split(".")

    for i in range(len(seed_package_name_split)):
        os.rename(seed_package_name_split[i], new_package_name_split[i])
        os.chdir(new_package_name_split[i])

    os.chdir('../../../../../../..')
    find_replace_in_dir(os.getcwd(), SEED_PACKAGE_NAME, package_name)
    os.chdir('..')


def rename_app_name():
    find_and_replace(find=app_name, replace=APP_NAME_CHANGE, file_name=root_module + APP_BUILD_GRADLE)
    print(f'Changed app_name to {app_name}')


def rename_root_module():
    os.rename("Android-Seed", root_module)
    print(f'Renamed root module to {root_module}')


def rename_keystore_fields():
    find_and_replace(find=alias, replace=KEYSTORE_ALIAS, file_name=root_module + APP_BUILD_GRADLE)
    find_and_replace(find=password, replace=KEYSTORE_PASSWORD, file_name=root_module + APP_BUILD_GRADLE)


def create_private_repo():
    subprocess.run(["hub", "create", "--private", "adaptdk/{repo_name}".format(repo_name=root_module)])


def change_remote_url():
    subprocess.run(
        ["git", "remote", "set-url", "origin",
         "git@github.com:{org}/{repo_name}.git".format(org=GITHUB_ORG, repo_name=root_module)])
    print(f'Changed remote origin url to: ')
    subprocess.run(["git", "remote", "--verbose"])


if __name__ == '__main__':
    root_module = input("Name root module: ")
    rename_root_module()

    app_name = input("What's the app name: ")
    rename_app_name()

    package_name = input("Enter new package name like -> dk.adaptmobile.android_seed: ")
    rename_package_dirs()

    alias = input("Alias for the keystore: ")
    password = input("Password for the keystore: ")
    rename_keystore_fields()
    generate_keystore()  # Should be run at the end

    create_private_repo()

    change_remote_url()

    os.remove("setup.py")

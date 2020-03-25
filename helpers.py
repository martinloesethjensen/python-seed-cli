import fileinput
import os
import shutil


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

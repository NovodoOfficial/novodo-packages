# H=========================================================================================================================================== Novodo script - main =====H #

# I================================================================================================================================================= SYSTEM IMPORTS =====I #

import novUtils as utils

# I================================================================================================================================================== OTHER IMPORTS =====I #

import subprocess
import json
import sys
import os

# I======================================================================================================================================================== IMPORTS =====I #

# F====================================================================================================================================================== FUNCTIONS =====F #

def get_packages(root_dir):
    second_level_dirs = []
    for dirpath, dirnames, _ in os.walk(root_dir):
        if len(dirpath.split(os.sep)) - len(root_dir.split(os.sep)) == 1:
            for dirname in dirnames:
                second_level_dirs.append(os.path.join(dirpath, dirname))
    return second_level_dirs

def get_package_names(packages):
    package_names = []

    for package in packages:
        package_name = os.path.basename(package)
        package_names.append(package_name)

    return package_names

def get_package_full_names(packages):
    package_full_names = []

    for package in packages:
        package_full_name = os.path.split(package)[-1]
        package_full_names.append(package_full_name)

    return package_full_names

def is_unique(item, item_list):
    if item_list.count(item) == 1:
        return True
    return False

def get_app_json(repo):
    app_json_path = os.path.join(repo, "app.json")
    with open(app_json_path, "r") as config_file:
        app_json = json.load(config_file)
        return app_json

# F====================================================================================================================================================== FUNCTIONS =====F #

# M=========================================================================================================================================================== MAIN =====M #

def mainRun():
    all_args = sys.argv
    args = all_args[1:]

    if not len(args) in [2, 3]:
        utils.logging.error(f"Invalid arguments for run: {args}")
        sys.exit(1)

    if len(args) == 2:
        package = args[0]
        option = args[1]

        packages = get_packages(utils.PACKAGES_FOLDER)
        package_names = get_package_names(packages)

        package_full_names = get_package_full_names(packages)

        if package in package_names:
            if not is_unique(package, package_names):
                utils.logging.error("Package name is not unique, use the command, \"nov run <username> <package> <option>\"")
                sys.exit(1)
        else:
            utils.logging.error(f"Package not found (\"{package}\"), available packages:\n- {"\n- ".join(package_full_names)}")
            sys.exit(1)

        app_index = package_names.index(package)
        repo_folder = packages[app_index]

        app_json = get_app_json(repo_folder)

        buttons = app_json["buttons"]

        button_names = []

        button_files = []
        button_file_names = []

        scripts_dir = os.path.join(repo_folder, "scripts")
        
        for button in buttons:
            filename = button["file"]
            button_file_names.append(filename)
            file = f"{filename}.py"

            script_path = os.path.join(scripts_dir, file)

            button_files.append(script_path)

            button_name = button["name"]
            button_names.append(button_name)

        if option in button_names or option in button_file_names:
            if option in button_names:
                option_index = button_names.index(option)
                option_file = button_files[option_index]
                if not is_unique(button_names[option_index], button_names):
                    utils.logging.error(utils.Messages.REPEATED_OPTION)
                    sys.exit(1)
            else:
                option_file = button_files[button_file_names.index(option)]
                if not is_unique(option, button_file_names):
                    utils.logging.error(utils.Messages.REPEATED_OPTION)
                    sys.exit(1)
        else:
            try:
                option_int = int(option)
                option_file = button_files[option_int]
            except ValueError:
                utils.logging.ERROR("Invalid option for package")
                sys.exit(1)
        
        file_exists = os.path.isdir(scripts_dir) and os.path.isfile(option_file)

        if file_exists:
            subprocess.run([sys.executable, option_file])
            sys.exit(0)

# M=========================================================================================================================================================== MAIN =====M #

# R============================================================================================================================================================ RUN =====R #

if __name__ == "__main__":
    try:
        mainRun()
        
    except KeyboardInterrupt:
        utils.logging.debug("KeyboardInterrupt Exit")
        sys.exit(0)

    except Exception as e:
        utils.logging.error(f'Error - {e}')
        utils.logging.error(utils.traceback.format_exc())
        raise

# R============================================================================================================================================================ RUN =====R #

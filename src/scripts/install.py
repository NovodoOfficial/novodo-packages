# H====================================================================================== Novodo script - install =====H #

# I=============================================================================================== SYSTEM IMPORTS =====I #

import novUtils as utils

# I================================================================================================ OTHER IMPORTS =====I #

import sys
import os

# I====================================================================================================== IMPORTS =====I #

# M========================================================================================================= MAIN =====M #

def mainInstall():
    args = sys.argv[1:]

    if not len(args) in [1, 2]:
        utils.logging.error(f"Invalid arguments for install: {args}")
        sys.exit(1)

    package_owner = args[0]

    if len(args) == 1:
        package_name = package_owner
        package_owner = utils.Github.USER
    else:
        package_name = args[1]

    token = utils.Github.get_token(utils.CONFIG_DIR)

    if not utils.Github.repo_exists(package_owner, package_name, token):
        utils.logging.error(f"Repository {package_owner}/{package_name} does not exist.")
        sys.exit(1)

    repo_size_kb = utils.Github.get_repo_size(package_owner, package_name)

    repo_size_formatted = utils.format_size(repo_size_kb)

    message = f"Installing \"{package_name}\" will be {repo_size_formatted}, install? ([Y]es/[N]o)\n"

    install_confimation = utils.get_input(message).lower()

    if install_confimation in utils.Y_LIST:
        repo_url = f"https://github.com/{package_owner}/{package_name}"
        user_folder = os.path.join(utils.PACKAGES_FOLDER, package_owner)
        repo_folder = os.path.join(user_folder, package_name)

        os.makedirs(f"{user_folder}/{package_name}", exist_ok=True)

        utils.logging.info(f"Installing \"{package_name}\" to \"{repo_folder}\"")

        branch = "main"
        utils.Github.download_and_extract_repo(repo_url, repo_folder, branch, token)

# M========================================================================================================= MAIN =====M #

# R========================================================================================================== RUN =====R #

if __name__ == "__main__":
    try:
        mainInstall()
        
    except KeyboardInterrupt:
        utils.logging.debug("KeyboardInterrupt Exit")
        sys.exit(0)

    except Exception as e:
        utils.logging.error(f'Error - {e}')
        utils.logging.error(utils.traceback.format_exc())
        raise

# R========================================================================================================== RUN =====R #

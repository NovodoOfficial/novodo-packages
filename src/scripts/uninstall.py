# H==================================================================================== Novodo script - uninstall =====H #

# I=============================================================================================== SYSTEM IMPORTS =====I #

import novUtils as utils

# I================================================================================================ OTHER IMPORTS =====I #

import shutil
import sys
import os

# I====================================================================================================== IMPORTS =====I #

# V==================================================================================================== CONSTANTS =====V #

Markdown = utils.Markdown
Color = Markdown.Color
Branding = utils.Branding

# V==================================================================================================== CONSTANTS =====V #

# M========================================================================================================= MAIN =====M #

def mainUninstall():
    args = sys.argv[1:]

    if len(args) != 2:
        utils.logging.error(f"Invalid arguments for uninstall: {args}")
        sys.exit(1)

    package_owner = args[0]
    package_name = args[1]

    user_folder = os.path.join(utils.PACKAGES_FOLDER, package_owner)
    repo_folder = os.path.join(user_folder, package_name)

    if not os.path.exists(repo_folder):
        utils.logging.error(f"Repository {package_owner}/{package_name} does not exist.")
        sys.exit(1)

    message = f"Uninstall {Color.RED}\"{Color.BLUE}{package_name}{Color.RED}\"{Color.RESET}? ([Y]es/[N]o)"

    uninstall_confimation = utils.get_input(message).lower()

    if uninstall_confimation in utils.Y_LIST:
        message = f"Enter the name of the package to confirm the uninstallation: {Color.RED}\"{Color.BLUE}{package_owner}/{package_name}{Color.RED}\"{Color.RESET}"

        uninstall_confimation = utils.get_input(message)

        uninstall_target = f"{package_owner}/{package_name}"

        if uninstall_confimation != uninstall_target:
            utils.logging.error(f"Uninstallation aborted.")
            sys.exit(1)

        utils.logging.info(f"Uninstalling {Color.RED}\"{Color.BLUE}{package_name}{Color.RED}\"{Color.RESET} from {Color.RED}\"{Color.BLUE}{repo_folder}{Color.RED}\"{Color.RESET}")
        shutil.rmtree(repo_folder)
        sys.exit(0)

    else:
        utils.logging.error(f"Uninstall aborted.")
        sys.exit(1)

# M========================================================================================================= MAIN =====M #

# R========================================================================================================== RUN =====R #

if __name__ == "__main__":
    try:
        mainUninstall()
        
    except KeyboardInterrupt:
        utils.logging.debug("KeyboardInterrupt Exit")
        sys.exit(0)

    except Exception as e:
        utils.logging.error(f'Error - {e}')
        utils.logging.error(utils.traceback.format_exc())
        raise

# R========================================================================================================== RUN =====R #

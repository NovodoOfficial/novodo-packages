# H======================================================================================================================================== Novodo script - uninstall =====H #

# I================================================================================================================================================= SYSTEM IMPORTS =====I #

import novUtils as utils

# I================================================================================================================================================== OTHER IMPORTS =====I #

import sys
import os

# I======================================================================================================================================================== IMPORTS =====I #

# M=========================================================================================================================================================== MAIN =====M #

def mainUninstall():
    args = sys.argv[1:]

    if not len(args) in [2, 3]:
        utils.logging.error(f"Invalid arguments for uninstall: {args}")
        sys.exit(1)

    package_owner = args[0]
    package_name = args[1]

    branch = "main"
    
    if len(args) == 3:
        branch = args[2]

    repo_size_kb = utils.Github.get_repo_size(package_owner, package_name)

    repo_size_formatted = utils.format_size(repo_size_kb)

    message = f"Uninstalling \"{package_name}\" will be {repo_size_formatted}, uninstall? ([Y]es/[N]o)\n"

    

# M=========================================================================================================================================================== MAIN =====M #

# R============================================================================================================================================================ RUN =====R #

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

# R============================================================================================================================================================ RUN =====R #

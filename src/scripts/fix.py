# H========================================================================================== Novodo script - fix =====H #

# I=============================================================================================== SYSTEM IMPORTS =====I #

import novUtils as utils

# I================================================================================================ OTHER IMPORTS =====I #

import subprocess
import sys
import os

# I====================================================================================================== IMPORTS =====I #

# F==================================================================================================== FUNCTIONS =====F #

def ask_path(path):
    confirm = utils.get_input(f"Overwrite \"{path}\"? ([Y]es/[N]o/[C]ancel)")

    if confirm in utils.CANCEL_LIST:
        sys.exit(1)
    elif not confirm in utils.Y_LIST:
        return False
    return True

# F==================================================================================================== FUNCTIONS =====F #

# M========================================================================================================= MAIN =====M #

def mainFix():
    args = sys.argv[1:]

    if len(args) != 1:
        utils.logging.error(f"Invalid arguments for fix: {args}")
        sys.exit(1)

    # todo Write code

# M========================================================================================================= MAIN =====M #

# R========================================================================================================== RUN =====R #

if __name__ == "__main__":
    try:
        mainFix()
        
    except KeyboardInterrupt:
        utils.logging.debug("KeyboardInterrupt Exit")
        sys.exit(0)

    except Exception as e:
        utils.logging.error(f'Error - {e}')
        utils.logging.error(utils.traceback.format_exc())
        raise

# R========================================================================================================== RUN =====R #

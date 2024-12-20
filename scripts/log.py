# H========================================================================================= Novodo script - main =====H #

# I=============================================================================================== SYSTEM IMPORTS =====I #

import novUtils as utils

# I================================================================================================ OTHER IMPORTS =====I #

import sys

# I====================================================================================================== IMPORTS =====I #

# M========================================================================================================= MAIN =====M #

def mainLog():
    utils.logging.info(f"Novodo Packages logs stored at \"{utils.LOGGING_PATH}\"")

# M========================================================================================================= MAIN =====M #

# R========================================================================================================== RUN =====R #

if __name__ == "__main__":
    utils.atexit.register(utils.on_exit)
    try:
        mainLog()

    except KeyboardInterrupt:
        utils.logging.debug("KeyboardInterrupt Exit")
        sys.exit(0)

    except Exception as e:
        utils.logging.error(f'Error - {e}')
        utils.logging.error(utils.traceback.format_exc())
        raise

# R========================================================================================================== RUN =====R #


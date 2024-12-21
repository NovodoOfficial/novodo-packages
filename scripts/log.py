# H========================================================================================= Novodo script - main =====H #

# I=============================================================================================== SYSTEM IMPORTS =====I #

import novUtils as utils

# I================================================================================================ OTHER IMPORTS =====I #

import sys

# I====================================================================================================== IMPORTS =====I #

# V==================================================================================================== CONSTANTS =====V #

Markdown = utils.Markdown
Color = Markdown.Color
Color.RESET = Markdown.RESET
Branding = utils.Branding

# V==================================================================================================== CONSTANTS =====V #

# M========================================================================================================= MAIN =====M #

def mainLog():
    utils.logging.info(f"{Branding.ANSI}Novodo Packages{Color.RESET} logs stored at {Color.RED}\"{Color.BLUE}{utils.LOGGING_PATH}{Color.RED}\"{Color.RESET}")

# M========================================================================================================= MAIN =====M #

# R========================================================================================================== RUN =====R #

if __name__ == "__main__":
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


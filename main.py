# H========================================================================================= Novodo script - main =====H #

# I=============================================================================================== SYSTEM IMPORTS =====I #

import scripts.novUtils as utils

# I================================================================================================ OTHER IMPORTS =====I #

import subprocess
import sys
import os

# I====================================================================================================== IMPORTS =====I #

# M========================================================================================================= MAIN =====M #

def main():
    args = sys.argv[1:]

    if len(args) == 0:
        utils.logging.info(f"Novodo Packages v0.0.1 from \"{utils.SCRIPT_PATH}\"\n{utils.Branding.ANSI}\n{utils.Branding.BANNER}\n{utils.Markdown.RESET}")

        sys.exit(0)

    SCRIPTS_FOLDER_DIR = os.path.join(utils.SCRIPT_DIR, "scripts")

    command = args[0]
    command_file = os.path.join(SCRIPTS_FOLDER_DIR, f"{command}.py")

    file_args = args[1:]

    command_exists = os.path.isdir(SCRIPTS_FOLDER_DIR) and os.path.isfile(command_file)

    if command_exists:
        subprocess.run([sys.executable, command_file, *file_args])
        sys.exit(0)
    
    if os.path.isdir(SCRIPTS_FOLDER_DIR):
        utils.logging.error(f"Command \"{command}\" does not exist or is not found at expected location: \"{command_file}\"")
    else:
        utils.logging.error(f"Scripts folder not found at expected location: \"{SCRIPTS_FOLDER_DIR}\"")

    sys.exit(1)

# M========================================================================================================= MAIN =====M #

# R========================================================================================================== RUN =====R #

if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        utils.logging.debug("KeyboardInterrupt Exit")
        sys.exit(0)

    except Exception as e:
        utils.logging.error(f'Error - {e}')
        utils.logging.error(utils.traceback.format_exc())
        raise

# R========================================================================================================== RUN =====R #


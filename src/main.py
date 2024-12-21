# H========================================================================================= Novodo script - main =====H #

# I=============================================================================================== SYSTEM IMPORTS =====I #

import scripts.novUtils as utils

# I================================================================================================ OTHER IMPORTS =====I #

import subprocess
import shlex
import sys
import os

# I====================================================================================================== IMPORTS =====I #

# V==================================================================================================== CONSTANTS =====V #

Markdown = utils.Markdown
Color = Markdown.Color
Color.RESET = Markdown.RESET
Branding = utils.Branding

# V==================================================================================================== CONSTANTS =====V #

# F==================================================================================================== FUNCTIONS =====F #

def interactive_console():
    utils.set_window_title("Novodo Packages Console")

    input_string = f"{Branding.ANSI}{utils.SCRIPT_PATH}{Color.BLUE}>{Color.RESET} "

    while True:
        command_line = input(input_string).strip()
        command_args = shlex.split(command_line)

        if not command_args:
            continue

        command = command_args[0]
        args = command_args[1:]

        console_commands = ["clear", "cls", "exit", "quit"]

        if command in ["exit", "quit"]:
            break
        elif command in ["clear", "cls"]:
            utils.clear_screen()

        if command in console_commands:
            continue

        command_file = os.path.join(utils.SCRIPT_DIR, "scripts", f"{command}.py")

        if os.path.isfile(command_file):
            subprocess.run([sys.executable, command_file, *args])  # Pass args to subprocess
        else:
            utils.logging.error(f"{Color.RED}Error:{Color.RESET}\nCommand {Color.RED}\"{Color.BLUE}{command}{Color.RED}\"{Color.RESET} does not exist or is not found at expected location: {Color.RED}\"{Color.BLUE}{command_file}{Color.RED}\"{Color.RESET}")

# F==================================================================================================== FUNCTIONS =====F #

# M========================================================================================================= MAIN =====M #

def main():
    args = sys.argv[1:]

    if len(args) == 0:
        use_interactive_console = True
    elif len(args) == 1:
        if args[0] in ["--console", "console"]:
            use_interactive_console = True

    if use_interactive_console:
        message = f"{Branding.ANSI}Novodo Packages {Color.RESET}iteractive console {Color.BLUE}v{utils.VERSION}{Color.RESET} from {Color.RED}\"{Color.BLUE}{utils.SCRIPT_PATH}{Color.RED}\"{Color.RESET}\n{Branding.ANSI}\n{Branding.BANNER}\n{Color.RESET}\nType {Color.RED}\"{Color.BLUE}exit{Color.RED}\"{Color.RESET} or {Color.RED}\"{Color.BLUE}quit{Color.RED}\"{Color.RESET} to quit\n"

        utils.logging.info(message)
        interactive_console()

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

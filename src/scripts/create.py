# H======================================================================================= Novodo script - create =====H #

# I=============================================================================================== SYSTEM IMPORTS =====I #

import novUtils as utils
import threading

# I================================================================================================ OTHER IMPORTS =====I #

import time
import sys
import os

# I====================================================================================================== IMPORTS =====I #

# V==================================================================================================== CONSTANTS =====V #

Markdown = utils.Markdown
Color = Markdown.Color
Branding = utils.Branding

# V==================================================================================================== CONSTANTS =====V #

# F==================================================================================================== FUNCTIONS =====F #

spinner_running = False

def start_spinning(message):
    global spinner_running
    spinner_running = True
    def spin():
        spinner = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        while spinner_running:
            for char in spinner:
                if not spinner_running:
                    break
                sys.stdout.write(f"\r{char} {message} ")
                sys.stdout.flush()
                time.sleep(0.1)
    threading.Thread(target=spin).start()

def stop_spinning(end_message):
    global spinner_running
    spinner_running = False
    utils.MoveCursor.up()
    clear_row()
    sys.stdout.write(f"\r{end_message} \n")
    sys.stdout.flush()

def spin(count, message="", end_message=""):
    spinner = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
    for _ in range(count):
        for char in spinner:
            sys.stdout.write(f"\r{char} {message} ")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write(f"\r{end_message} \n")
    sys.stdout.flush()

def clear_row():
    try:
        width = os.get_terminal_size().columns
    except:
        width = 80
    
    sys.stdout.write("\r" + " " * width + "\r")

def create_package(options, token):
    print("options", options)
    utils.Github.fork_repo(utils.Github.TEMPLATE, utils.Github.USER, options["package_name"], token)

# F==================================================================================================== FUNCTIONS =====F #

# M========================================================================================================= MAIN =====M #

def mainCreate():
    spin(3, f"Starting {Branding.ANSI}Novodo Packages{Color.RESET} create process", f"{Color.GREEN}✓ {Branding.ANSI}Novodo Packages{Color.RESET} create process initiated")

    token = utils.Github.get_token(utils.CONFIG_DIR)

    if not token:
        utils.logging.error(f"{Color.RED}✗{Color.RESET} No GitHub token found. Please run {Color.RED}\"{Color.BLUE}nov config token <token>{Color.RED}\"{Color.RESET}")
        sys.exit(1)

    questions = {
        "package_name": {
            "question": "What is the name of your package?",
            "type": "string"
        }
    }

    options = {}

    for key, value in questions.items():
        prefix = f"{Color.BLUE}?{Color.RESET}"
        question = value["question"]
        if value["type"] == "boolean":
            question += f" {Color.BLUE}([Y]es/[N]o){Color.RESET}"
        while True:
            question_string = f"{prefix} {question} "

            clear_row()
            answer = utils.get_input(question_string)
            if answer.lower() in utils.EXIT_LIST:
                utils.logging.info(f"{Color.RED}✗{Color.RESET} Exiting create process")
                sys.exit(0)
            try:
                if value["type"] == "number":
                    options[key] = float(answer)
                elif value["type"] == "boolean":
                    if answer.lower() in utils.Y_LIST or answer.lower() in utils.N_LIST:
                        options[key] = answer.lower() in utils.Y_LIST
                    else:
                        raise ValueError("Invalid boolean input")
                else:
                    if not answer:
                        raise ValueError("Empty string")
                    options[key] = answer
                break
            except ValueError as e:
                utils.MoveCursor.up()
                
                prefix = f"{Color.RED}?{Color.RESET} Invalid input for {Color.RED}\"{Color.BLUE}{key}{Color.RED}\"{Color.RESET}: {str(e).capitalize()}. Please try again:"
            
        utils.MoveCursor.up()
        done = f"{Color.GREEN}?{Color.RESET} {question} {answer}"
        done += " " * (max(len(question_string) - len(done), 0))
        utils.logging.info(done)

    create_package(options, token)

    spin(3, f"Finishing creation of {Color.RED}\"{Color.BLUE}{options['project_name']}{Color.RED}\"", f"{Color.GREEN}✓{Color.RESET} Created {Color.RED}\"{Color.BLUE}{options['project_name']}{Color.RED}\"{Color.RESET}")

# M========================================================================================================= MAIN =====M #

# R========================================================================================================== RUN =====R #

if __name__ == "__main__":
    try:
        mainCreate()

    except KeyboardInterrupt:
        utils.logging.debug("KeyboardInterrupt Exit")
        sys.exit(0)

    except Exception as e:
        utils.logging.error(f'Error - {e}')
        utils.logging.error(utils.traceback.format_exc())
        raise

# R========================================================================================================== RUN =====R #


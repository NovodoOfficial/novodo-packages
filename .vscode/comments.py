# H============================================================================ Novodo script - comment organiser =====H #

# I====================================================================================================== IMPORTS =====I #

import sys
import os
import re

# I====================================================================================================== IMPORTS =====I #

# F==================================================================================================== FUNCTIONS =====F #

def replace_pattern_in_list(lines):
    modified_lines = []
    for line in lines:
        stripped_line = line.rstrip('\n')
        pattern = r'#\s*([a-zA-Z])\s*=\s*([^=]+)\s*'
        replacement = r'# \1= \2 =\1 #'
        modified_line = re.sub(pattern, replacement, stripped_line, flags=re.IGNORECASE)
        modified_lines.append(modified_line + '\n')

    return modified_lines

def modify_file(file_path, target_width, side):
    target_width = int(target_width)

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        lines = replace_pattern_in_list(lines)

        pattern = r'^(\s*)# ([A-Z@])=+ (.*) =+\2 #$'

        def generate_new_line(char, middle_text, width, leading_whitespace):
            side_equals_count = 5
            side_equals_string = "=" * side_equals_count

            equals_count = width - len(middle_text) - (2 * len(char)) - 4 - side_equals_count - len(leading_whitespace)
            equals_string = "=" * equals_count

            if side == "r":
                new_line = f"{leading_whitespace}# {char}{equals_string} {middle_text} {side_equals_string}{char} #\n"
            else:
                new_line = f"{leading_whitespace}# {char}{side_equals_string} {middle_text} {equals_string}{char} #\n"

            return new_line

        modified_lines = []
        for line in lines:
            match = re.match(pattern, line)
            if match:
                leading_whitespace = match.group(1) or ""
                char = match.group(2)
                middle_text = match.group(3).strip()
                modified_lines.append(generate_new_line(char, middle_text, target_width, leading_whitespace))
            else:
                modified_lines.append(line)

        with open(file_path, 'w') as file:
            file.writelines(modified_lines)

        print("File modified successfully.")

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

def process_directory(directory, target_width, side, ignore_list=None):
    if ignore_list is None:
        ignore_list = []

    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if os.path.join(root, d) not in ignore_list]
        
        for file in files:
            file_path = os.path.join(root, file)
            if file_path in ignore_list:
                continue
            modify_file(file_path, target_width, side)

# F==================================================================================================== FUNCTIONS =====F #

# M========================================================================================================= MAIN =====M #

def mainComments():
    if len(sys.argv) < 4:
        print("Usage: python script.py <file_path_or_directory> <target_width> <side (\"l\"/\"r\")> [ignore_list]")
        sys.exit(1)
    else:
        file_path_or_directory = sys.argv[1]
        target_width = sys.argv[2]
        side = sys.argv[3]
        ignore_list = sys.argv[4:] if len(sys.argv) > 4 else []

        ignore_list = [os.path.abspath(path) for path in ignore_list]

        if os.path.isdir(file_path_or_directory):
            process_directory(file_path_or_directory, target_width, side, ignore_list)
        else:
            if os.path.abspath(file_path_or_directory) not in ignore_list:
                modify_file(file_path_or_directory, target_width, side)
        sys.exit(0)

# M========================================================================================================= MAIN =====M #

# R========================================================================================================== RUN =====R #

if __name__ == "__main__":
    utils.atexit.register(utils.on_exit)
    try:
        mainComments()
        
    except KeyboardInterrupt:
        print("KeyboardInterrupt Exit")
        sys.exit(0)

# R========================================================================================================== RUN =====R #

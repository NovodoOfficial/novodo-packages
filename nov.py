from utilities import Commands
from utilities import Errors
import commands
import sys
import os

args = sys.argv[1:]

if not args:
    print("[!] Error - No command provided, usage:")
    print(" └> nov <command> [arguments]")
    sys.exit(1)

command = args[0]
command_args = args[1:]

try:
    Commands.safe_execute_command(command, command_args)
except Errors.CommandError as e:
    print(f"[!] Error - An issue was incountered while running the command \"{command}\":")
    print(f" └> {e}")
    exit(1)

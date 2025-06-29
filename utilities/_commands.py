from ._errors import CommandError
from ._dotdict import DotDict

_commands = []

def Command(func: callable, name: str, min_args: int=None, max_args: int=None) -> callable:
    _commands.append(DotDict({
        "name": name,
        "func": func,
        "min_args": min_args,
        "max_args": max_args
    }))

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

def get_commands() -> list:
    return _commands

def safe_get_command(name: str, args: list) -> DotDict:
    command = None
    for command in _commands:
        if command.name == name:
            break
    
    if not command:
        raise CommandError(f"Command \"{name}\" not found")
    
    raise_minimum = command.min_args is not None and len(args) < command.min_args
    raise_maximum = command.min_args is not None and len(args) > command.max_args
    if raise_minimum or raise_maximum:
        raise CommandError(f"Command takes {command.min_args}-{command.max_args} arguments, but expected {len(args)} were given")
    
    return command

def safe_execute_command(name: str, args: list) -> None:
    command = safe_get_command(name, args)
    command.func(*args)

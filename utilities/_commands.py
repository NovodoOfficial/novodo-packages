from ._dotdict import DotDict
from ._errors import Errors

class Commands:
    _commands = []

    @classmethod
    def Command(cls, func: callable, name: str, min_args: int = None, max_args: int = None) -> callable:
        cls._commands.append(DotDict({
            "name": name,
            "func": func,
            "min_args": min_args,
            "max_args": max_args
        }))

        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    @classmethod
    def get_commands(cls) -> list:
        return cls._commands

    @classmethod
    def safe_get_command(cls, name: str, args: list):
        command = None
        for cmd in cls._commands:
            if cmd.name == name:
                command = cmd
                break

        if command is None:
            raise Errors.CommandError(f"Command \"{name}\" not found")

        if command.min_args is not None and len(args) < command.min_args:
            raise Errors.CommandError(f"Command \"{name}\" expects at least {command.min_args} arguments, got {len(args)}")
        if command.max_args is not None and len(args) > command.max_args:
            raise Errors.CommandError(f"Command \"{name}\" expects at most {command.max_args} arguments, got {len(args)}")

        return command

    @classmethod
    def safe_execute_command(cls, name: str, args: list) -> None:
        command = cls.safe_get_command(name, args)
        command.func(*args)

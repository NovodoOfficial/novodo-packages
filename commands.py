from utilities import Commands

@Commands.Command("install", args=(1, 2))
def install(args: list):
    print(f"Args: {args}")
    print(f"Install: {', '.join(args)}")

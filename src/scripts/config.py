# H======================================================================================= Novodo script - config =====H #

# I=============================================================================================== SYSTEM IMPORTS =====I #

import novUtils as utils

# I================================================================================================ OTHER IMPORTS =====I #

import sys

# I====================================================================================================== IMPORTS =====I #

# M========================================================================================================= MAIN =====M #

def mainConfig():
    all_args = sys.argv

    args_parsed = []

    for i in all_args:
        if " " in i:
            i = f"\"{i}\""

        args_parsed.append(i)

    command = " ".join(args_parsed)

    args = all_args[1:]

    if not len(args) in [1, 2]:
        utils.logging.error(f"Invalid arguments for config: {args}")
        sys.exit(1)

    if args[0] in ["create", "reset"]:
        if len(args) != 1:
            utils.logging.error(f"Invalid command:\n{command}")

        utils.Config.save(utils.CONFIG_DIR, utils.CONFIG_TEMPLATE)

    elif args[0] == "token":
        if len(args) != 2:
            utils.logging.error(f"Invalid command:\n{command}")

        config = utils.Config.load(utils.CONFIG_DIR)

        config = utils.Config.set_option("system/github/toekn", args[1], config)

        utils.Config.save(utils.CONFIG_DIR, config)

# M========================================================================================================= MAIN =====M #

# R========================================================================================================== RUN =====R #

if __name__ == "__main__":
    try:
        mainConfig()
        
    except KeyboardInterrupt:
        utils.logging.debug("KeyboardInterrupt Exit")
        sys.exit(0)

    except Exception as e:
        utils.logging.error(f'Error - {e}')
        utils.logging.error(utils.traceback.format_exc())
        raise

# R========================================================================================================== RUN =====R #

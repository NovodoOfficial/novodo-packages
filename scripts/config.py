# H======================================================================================= Novodo script - config =====H #

# I=============================================================================================== SYSTEM IMPORTS =====I #

import novUtils as utils

# I================================================================================================ OTHER IMPORTS =====I #

import sys
import os

# I====================================================================================================== IMPORTS =====I #

# F==================================================================================================== FUNCTIONS =====F #

def backup_config_message(overide=False):
    confirm = "b"
    if not overide:
        confirm = utils.get_input(f"The config file at \"{utils.CONFIG_PATH}\" is going to be modified,\nconfirm action? ([B]ackup first/[Y]es/[N]o)\n").lower()

    if not confirm in utils.Y_LIST + utils.BACKUP_LIST:
        utils.logging.info(utils.Messages.CANNOT_CONTINUE)
        sys.exit(1)

    if confirm in utils.BACKUP_LIST:
        utils.logging.info(f"Backing up \"{utils.CONFIG_PATH}\" to \"{utils.CONFIG_BACKUP_DIR}\"")

        backup = utils.Config.backup(utils.CONFIG_PATH, utils.CONFIG_BACKUP_PATH)
        utils.logging.info(f"Backed up \"{utils.CONFIG_PATH}\" as \"{backup}\"")

# F==================================================================================================== FUNCTIONS =====F #

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

        backup_config_message()

        utils.Config.save(utils.CONFIG_PATH, utils.CONFIG_TEMPLATE)

    elif args[0] == "token":
        if len(args) != 2:
            utils.logging.error(f"Invalid command:\n{command}")

        backup_config_message()

        config = utils.Config.load(utils.CONFIG_PATH)

        config["Github"]["Token"] = args[1]

        utils.Config.save(utils.CONFIG_PATH, config)

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

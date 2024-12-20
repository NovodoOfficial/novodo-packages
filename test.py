import scripts.novUtils as utils
import json

config = utils.Config.load(utils.CONFIG_DIR)

template_pretty = json.dumps(config, indent=4)

# utils.clearScreen()

adress = "system/github/token"

config = utils.Config.set_option(adress, None, config)

utils.Config.save(config, utils.CONFIG_DIR)

utils.Github.get_token(utils.CONFIG_DIR)
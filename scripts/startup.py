import time
import sys

import novUtils as utils

print(utils.CONFIG_TEMPLATE)

for i in range(0, 5):
    print(5 - i)
    time.sleep(1)

print("Exiting")

time.sleep(0.5)

sys.exit(0)

# todo General
import adafruit_logging as logging
import supervisor

logger = logging.getLogger("keyboard")

if supervisor.runtime.serial_connected:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)

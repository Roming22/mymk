import adafruit_logging as logging
import supervisor

logger = logging.getLogger()

if supervisor.runtime.serial_connected:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.ERROR)

from loguru import logger

FILE_PATH = "./app/logs/app.log"

# logger.remove()
logger.add(
    FILE_PATH,
    rotation="1 minute",
    retention=2,
)

import json
from helper.logs import logger
from http_client import HC_HTTPClient
from helper.config import URL_INDEX


if __name__ == "__main__":
    logger.info("\n\n")
    logger.info("----------------------START NEW SESSION----------------------")

    connect = HC_HTTPClient()
    data = connect.scrapping(URL_INDEX)

    with open("./app/resources/page_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

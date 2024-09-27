import os
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("URL")
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")


if __name__ == "__main__":
    [print(f"{k} = {v}") for k, v in locals().items() if k.isupper()]

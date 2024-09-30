from time import sleep
import requests
import json
from bs4 import BeautifulSoup
from helper.config import HEADERS, URL_LOGIN, URL_INDEX, DATA, COOKIES_PATH


class HTTPClient:
    def __init__(self) -> None:
        self._session = requests.Session()


class HC_HTTPClient(HTTPClient):
    def __init__(self) -> None:
        super().__init__()

        with open(COOKIES_PATH, "r", encoding="utf-8") as file:
            try:
                cookies_dict = json.load(file)

                self._session.cookies.update(cookies_dict)
                response = self._session.get(url=URL_INDEX, headers=HEADERS)
                status_code = response.status_code
            except:
                status_code = 400

        if status_code > 201:
            response = self._session.post(url=URL_LOGIN, headers=HEADERS, data=DATA)
            self.dump_cookies()
            print("Enter with login.")
        else:
            print("Enter with cookies.")

    def scrapping(
        self,
        url: str,
        website_data: list = list(),
        path: str = "./app/downloads/pages",
    ) -> dict:
        src = self._session.get(url=url, headers=HEADERS)
        print(src.status_code, url)
        soup = BeautifulSoup(src.text, "lxml")
        page_data = None

        if soup.find("table", class_="stream-table"):

            trs = soup.find("table", class_="stream-table").find_all("a")
            for tr in trs:
                cours_name = tr.find("span", class_="stream-title").text
                course_url = "https://healthcreation.ru" + tr.get("href")
                page_data = {
                    "title": cours_name,
                    "url": course_url,
                    "children": list(),
                }

                if course_url:
                    website_data.append(page_data)
                    self.scrapping(course_url, page_data.get("children"))

        """elif soup.find_all("div", class_="link title"):

            trs = soup.find_all("div", class_="link title")
            for tr in trs:
                cours_name = tr.text.strip().split("\t")[0]
                course_url = "https://healthcreation.ru" + tr.get("href")
                page_data = {
                    "title": cours_name,
                    "url": course_url,
                    "children": list(),
                }
                website_data.append(page_data)

                if course_url:
                    page_data["children"].append(
                        self.scrapping(course_url, website_data)
                    )

        elif soup.find_all("strong", class_="redactor-inline-converted"):

            trs = soup.find_all("strong", class_="redactor-inline-converted")
            for tr in trs:
                cours_name = tr.text.strip()
                course_url = tr.find("a")
                if course_url:
                    page_data = {
                        "title": cours_name,
                        "url": course_url.get("href"),
                        "children": list(),
                    }

                    page_data["children"].append(self.scrapping(course_url.get("href")))

        elif soup.find("iframe", class_="vhi-iframe js--vhi-iframe"):

            player_url = soup.find("iframe", class_="vhi-iframe js--vhi-iframe").get(
                "src"
            )

            if player_url:
                src = self._session(player_url)
                soup = BeautifulSoup(src.text, "lxml")

                trs = soup.find_all("script")
                configs_script = None
                for script in trs:
                    if "window.configs =" in script.string:
                        configs_script = script.string.strip().split(
                            "window.configs = "
                        )[1]
                        configs_dict = json.loads(configs_script)
                        break

                players_list_url = configs_dict.get("masterPlaylistUrl")

                page_data = {"title": "players_list", "url": players_list_url}

        else:
            return"""

        return website_data

    def dump_cookies(self) -> None:
        cookies_dict = self._session.cookies.get_dict()
        with open(COOKIES_PATH, "w", encoding="utf-8") as file:
            json.dump(cookies_dict, file)


if __name__ == "__main__":
    connect = HC_HTTPClient()
    data = connect.scrapping(URL_INDEX)

    # with open("./app/resources/page_data.txt", "w", encoding="utf-8") as file:
    #    file.write(**data[0])

    # with open("./app/resources/website_data.txt", "w", encoding="utf-8") as file:
    #    file.write(**data[1])

    print(data)
    # print("\n\n")
    # print(data[1])

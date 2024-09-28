from time import sleep
import requests
import json
from bs4 import BeautifulSoup
from helper.config import HEADERS, COOKIES, URL


class My_request:
    @staticmethod
    def get_response(url) -> requests.Response:
        response = requests.get(
            url=url,
            headers=HEADERS,
            cookies=COOKIES,
        )
        print(response)
        sleep(1)
        return response

    def get_data(self, url: str) -> dict | None:
        src = self.get_response(url)
        soup = BeautifulSoup(src.text, "lxml")

        if soup.find("table", class_="stream-table"):

            trs = soup.find("table", class_="stream-table").find_all("a")
            for tr in trs:
                cours_name = tr.find("span", class_="stream-title").text
                course_url = "https://healthcreation.ru" + tr.get("href")
                page_data = {"title": cours_name, "url": course_url, "children": list()}

                if course_url:
                    page_data["children"].append(self.get_data(course_url))

        elif soup.find_all("div", class_="link title"):

            trs = soup.find_all("div", class_="link title")
            for tr in trs:
                cours_name = tr.text.strip().split("\t")[0]
                course_url = "https://healthcreation.ru" + tr.get("href")
                page_data = {"title": cours_name, "url": course_url, "children": list()}

                if course_url:
                    page_data["children"].append(self.get_data(course_url))

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
                    page_data["children"].append(self.get_data(course_url.get("href")))

        elif soup.find("iframe", class_="vhi-iframe js--vhi-iframe"):

            player_url = soup.find("iframe", class_="vhi-iframe js--vhi-iframe").get(
                "src"
            )

            if player_url:
                src = self.get_response(player_url)
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
            return

        return page_data


if __name__ == "__main__":
    data = My_request()
    print(data.get_data(URL))

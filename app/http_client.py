import json
import requests
from time import sleep
from bs4 import BeautifulSoup
from random import randint as rnd

from helper.logging_app import logger
from helper.folders import get_path
from helper.async_download_video import DownloadHLSAsync
from helper.config import HEADERS, URL_LOGIN, URL_INDEX, DATA, COOKIES_PATH


INDEX = "/index.html"


class HTTPClient:
    def __init__(self) -> None:
        self._session = requests.Session()


class HC_HTTPClient(HTTPClient):
    """HTTP client for healthcreation.ru

    Args:
        HTTPClient (_type_): creates a session
    """

    def __init__(self) -> None:
        super().__init__()

        with open(COOKIES_PATH, "r", encoding="utf-8") as file:
            try:
                # Load cookies from file
                cookies_dict = json.load(file)

                # Update cookies to session,
                # check if session works with loaded cookies,
                # get response status code
                self._session.cookies.update(cookies_dict)
                response = self._session.get(url=URL_INDEX, headers=HEADERS)
                status_code = response.status_code
            except Exception as ex:
                logger.error("Failed to load cookie file.")
                status_code = 400

        # If the cookie does not exist or the cookie is out of date
        if status_code > 201:
            # Raise the session by login and password,
            # dump cookies to a file
            response = self._session.post(url=URL_LOGIN, headers=HEADERS, data=DATA)
            self.dump_cookies()
            logger.debug("Login with login and password.")
        else:
            logger.debug("Logged in using cookies.")

    @staticmethod
    def save_html(path: str, source: str) -> None:
        """Save html text to index.html

        Args:
            path (str): path to save folder
            source (str): html text
        """
        with open(path + INDEX, "w") as file:
            file.write(source)
            logger.debug(f"File {path + INDEX} saved.")

    def __make_magic(
        self,
        path: str,
        cours_name: str,
        course_url: str,
        src: requests.Response,
        website_data: list[dict],
    ) -> None:
        """The function forms a dictionary with data (parsed pages),
        places it in a list of similar dictionaries and if it finds child links on the page,
        sends them to the parsing function

        Args:
            path (str): path to parsed data
            cours_name (str): course name
            course_url (str): cource url
            src (requests.Response): response to a request to the server
            website_data (list[dict]): list of dicts with response data
        """

        # We form the directory name,
        # save the parsed page to an HTML file,
        # and write the data to the dictionary
        new_path = get_path(path, cours_name)
        self.save_html(new_path, src.text)
        page_data = {
            "title": cours_name,
            "url": course_url,
            "children": list(),
        }
        logger.debug(f"{page_data = }")

        # If there are child links on the page
        if course_url:
            # Add dictionary with parsed data to list,
            # parse child link
            website_data.append(page_data)
            self.scrapping(course_url, page_data.get("children"), new_path)

    def scrapping(
        self,
        url: str,
        website_data: list[dict] = list(),
        path: str = "./app/downloads/pages/",
    ) -> list[dict]:
        """Recursive function, parses a site with a multi-layered nested structure
        and writes data to a dictionary, dictionaries are stored in a list.
        When the function finds a link to a streaming video,
        downloads it to a folder with the course name.

        Args:
            url (str): link to landing page
            website_data (list[dict], optional): list of dictionaries with data from the target link. Defaults to list().
            path (str, optional): the path where the parsed data will be stored. Defaults to "./app/downloads/pages/".

        Returns:
            list[dict]: return the expanded list
        """

        sleep(rnd(1, 3))  # we sleep so as not to overload the server

        # Get response from server,
        src = self._session.get(url=url, headers=HEADERS)
        logger.debug(f"{src.status_code, url}")

        # Parse response data with bs4
        soup = BeautifulSoup(src.text, "lxml")

        # We search for combinations of tags on the page,
        # if we find the necessary combination,
        # we collect the data and write it into the dictionary
        if soup.find("table", class_="stream-table"):
            logger.info(f"soup.find('table', class_='stream-table')")

            # we find all tags with links, take each link and title,
            # and recursively send it for processing
            trs = soup.find("table", class_="stream-table").find_all("a")
            for tr in trs:
                cours_name = tr.find("span", class_="stream-title").text
                course_url = "https://healthcreation.ru" + tr.get("href")

                self.__make_magic(path, cours_name, course_url, src, website_data)

        elif soup.find_all("div", class_="link title"):
            logger.info(f'soup.find_all("div", class_="link title")')

            trs = soup.find_all("div", class_="link title")
            for tr in trs:
                cours_name = tr.text.strip().split("\t")[0]
                course_url = "https://healthcreation.ru" + tr.get("href")

                self.__make_magic(path, cours_name, course_url, src, website_data)

        elif soup.find_all("strong", class_="redactor-inline-converted"):
            logger.info(f'soup.find_all("strong", class_="redactor-inline-converted")')

            trs = soup.find_all("strong", class_="redactor-inline-converted")
            for tr in trs:
                cours_name = tr.text.strip()
                course_url_dirty = tr.find("a")
                if course_url_dirty:
                    course_url = course_url_dirty.get("href")

                    self.__make_magic(path, cours_name, course_url, src, website_data)

        # or, if we find a video, we save it
        elif soup.find("iframe", class_="vhi-iframe js--vhi-iframe"):
            logger.info(f'soup.find("iframe", class_="vhi-iframe js--vhi-iframe")')

            # find frame with link to video player
            player_url = soup.find("iframe", class_="vhi-iframe js--vhi-iframe").get(
                "src"
            )

            # if the link is valid
            if player_url:
                # get response and parse it with bs4
                src = self._session.get(player_url)
                soup = BeautifulSoup(src.text, "lxml")

                # We find all the tags with the <script>,
                # among them we find the one that starts with "window.configs = ",
                # we pull out the dictionary with the player settings from it
                trs = soup.find_all("script")
                configs_script = None
                for script in trs:
                    if "window.configs =" in script.string:
                        configs_script = script.string.strip().split(
                            "window.configs = "
                        )[1]
                        configs_dict: dict = json.loads(configs_script)
                        break

                # from the dictionary we take a link to
                # a list of links to videos of different resolutions
                players_list_url = configs_dict.get("masterPlaylistUrl")

                # write data to dict and appand this to general list
                page_data = {"title": "players_list", "url": players_list_url}
                website_data.append(page_data)

                """# Send a list of videos to the module for downloading video content
                download = DownloadHLS(players_list_url, path)
                print(download.get_hls_video(session=self._session))"""

                # Send a list of videos to the module for async downloading video content
                download = DownloadHLSAsync(players_list_url, path)
                if download():
                    download.run_async()

        return website_data

    def dump_cookies(self) -> None:
        """Dump cookies of session to file"""
        cookies_dict = self._session.cookies.get_dict()
        with open(COOKIES_PATH, "w", encoding="utf-8") as file:
            json.dump(cookies_dict, file)
            logger.info(f"Dump cookies to {COOKIES_PATH}")


if __name__ == "__main__":
    connect = HC_HTTPClient()
    data = connect.scrapping(URL_INDEX)

    with open("./app/resources/page_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

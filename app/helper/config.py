import os
from dotenv import load_dotenv

load_dotenv()

URL_LOGIN = "https://healthcreation.ru/cms/system/login"
URL_INDEX = "https://healthcreation.ru/teach/control/stream/index"
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
COOKIES_PATH = "./app/resources/cookies.json"

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "ru,ru-RU;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "max-age=0",
    "Connection": "keep-alive",
    # "Cookie": "_ym_uid=1724226012457725689; _ym_d=1724226012; gc_visitor_59148=%7B%22id%22%3A6248834160%2C%22sfix%22%3A1%7D; dd_bdfhyr=55f523ba3ce1344d40e5e8efe4683d06; gdpr=0; _ym_isad=1; gc_visit_59148=%7B%22id%22%3A11260577637%2C%22sid%22%3A6502167147%7D; _ym_visorc=w; PHPSESSID5=3de767b7cc6fce50cacb3086bdd88c2b; _csrf=Lm9pU0leG0e0Tg3Qmnh_BsKwo0UcrQVB; gc_counter_59148=%7B%22id%22%3A6502167147%2C%22last_activity%22%3A%222024-09-28%2023%3A48%3A02%22%2C%22user_id%22%3A400267093%2C%22utm_id%22%3A1256%2C%22partner_code_id%22%3Anull%2C%22ad_offer_id%22%3Anull%2C%22fuid%22%3Anull%2C%22fpid%22%3Anull%2C%22city_id%22%3Anull%7D",
    "Referer": "https://healthcreation.ru/cms/system/login?required=true",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
}
DATA = {
    "action": "processXdget",
    "xdgetId": "99945_1_1_1_1_1_1",
    "params[action]": "login",
    "params[url]": URL_LOGIN,
    "params[email]": LOGIN,
    "params[password]": PASSWORD,
    "params[null]": "",
    "params[object_type]": "cms_page",
    "params[object_id]": "-1",
    "requestTime": "1727614805",
    "requestSimpleSign": "8c27baebbc8188fb96c8b506ba50f865",
    "gcSession": '{"id":6502167147,"last_activity":"2024-09-29 16:00:06","user_id":400267093,"utm_id":1256}',
    "gcVisit": '{"id":11264553906,"sid":6502167147}',
    "gcVisitor": '{"id":6248834160,"sfix":1}',
    "gcSessionHash": "d85a7c37a0c575749c177f36650e10a1",
}


if __name__ == "__main__":
    print("\nConstants:")
    [print(f"\t{k} = {v}") for k, v in locals().items() if k.isupper()]

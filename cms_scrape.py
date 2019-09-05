import requests

from utils import config


class CMSError(Exception):
    """Represents an error from Moodle API"""

    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class CMSScraper:
    """Uses the Moodle API to scrape docs"""

    ALLOWED_EXTS = (".doc", ".docx", ".pdf", ".pptx")

    def __init__(self, address, wstoken):
        self.REST_URL = address + "/webservice/rest/server.php"
        self.wstoken = wstoken
        self._userid = None

    def make_req(self, verb, params={}, data=None):
        query_params = {"wstoken": self.wstoken, "moodlewsrestformat": "json"}
        query_params.update(params)
        resp = requests.request(verb, self.REST_URL, params=query_params, data=data)
        resp = resp.json()
        if "exception" in resp:
            raise CMSError(resp["message"])
        return resp

    def get(self, wsfunc, params={}):
        params["wsfunction"] = wsfunc
        return self.make_req("get", params)

    def post(self, wsfunc, params={}, data={}):
        params["wsfunction"] = wsfunc
        return self.make_req("post", params, data)

    @property
    def userid(self) -> str:
        """Moodle UserID of user whose WebService Token is given"""
        if not self._userid:
            self._userid = self.get("core_webservice_get_site_info")["userid"]
        return self._userid

    @property
    def enrolled_courses(self):
        return self.get("core_enrol_get_users_courses", {"userid": self.userid})


if __name__ == '__main__':
    from utils import pprint_json
    scraper = CMSScraper(**config["MOODLE"])
    pprint_json(scraper.enrolled_courses)

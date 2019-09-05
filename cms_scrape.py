import shutil
import requests
from pathlib import Path
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

    def __init__(self, dl_root: Path, address, wstoken):
        self.dl_root = dl_root
        self.dl_root.mkdir(parents=True, exist_ok=True)
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

    def get_course_contents(self, course_id):
        return self.get("core_course_get_contents", {"courseid": course_id})

    def download_course(self, course):
        contents = self.get_course_contents(course["id"])
        crs_fold = self.dl_root / course["fullname"]
        crs_fold.mkdir(exist_ok=True)
        for topic in contents:
            modules = topic.get("modules")
            if not modules:
                continue
            topic_fold = crs_fold / topic["name"]
            topic_fold.mkdir(exist_ok=True)

            for module in modules:
                self.download_module(topic_fold, module)

    def download_module(self, topic_fold: Path, module):
        if module["modname"] != "resource":
            # TODO: add support for folders
            # skip folders, forums and other types of files
            return
        if not module["contents"]:
            return
        module_fold = topic_fold / module["name"]
        module_fold.mkdir(exist_ok=True)
        for content in module["contents"]:
            file_path = module_fold / content["filename"]
            self.download_file(file_path, content["fileurl"])

    def download_file(self, file_path: Path, file_url):
        with requests.get(file_url, params={"token": self.wstoken}, stream=True) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)

    def scrape(self):
        for crs in self.enrolled_courses:
            self.download_course(crs)


if __name__ == "__main__":
    scraper = CMSScraper(Path(config["PATHS"]["dl_root"]), **config["MOODLE"])
    scraper.scrape()

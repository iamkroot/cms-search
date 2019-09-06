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

    def get_enrolled_courses(self):
        return self.get("core_enrol_get_users_courses", {"userid": self.userid})

    def get_courses_docs(self):
        """Return document links of all the courses offered."""
        # For now, return docs of just the currently enrolled courses
        for course in self.get_enrolled_courses():
            yield course['fullname'], tuple(self.get_course_docs(course))

    def get_course_docs(self, course):
        crs_fold = Path(course["fullname"])
        contents = self.get("core_course_get_contents", {"courseid": course["id"]})
        for topic in contents:
            modules = topic.get("modules")
            if not modules:
                continue
            topic_fold = crs_fold / topic["name"]
            for module in modules:
                yield from self.get_module(topic_fold, module)

    @staticmethod
    def is_handout(module):
        return 'handout' in module['name'].lower()

    def get_module(self, topic_fold: Path, module):
        if module["modname"] not in ("resource", "folder"):
            return  # TODO: Add support for forums
        if self.is_handout(module) or not module["contents"]:
            return
        module_fold = topic_fold / module["name"]
        for content in module["contents"]:
            if content['type'] != 'file':
                continue
            yield {
                "file_path": module_fold / content["filename"],
                "updated_at": content['timemodified'],
                "file_url": content["fileurl"],
            }

    def download_file(self, file_path: Path, file_url):
        file_path.parent.mkdir(exist_ok=True, parents=True)
        with requests.get(file_url, params={"token": self.wstoken}, stream=True) as r:
            r.raise_for_status()
            with open(file_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)


if __name__ == "__main__":
    scraper = CMSScraper(Path(config["PATHS"]["dl_root"]), **config["MOODLE"])
    print(dict(scraper.get_courses_docs()))

from datetime import datetime
from pathlib import Path
from cms_scraper import CMSScraper
from database import Doc
from utils import config


class Indexer:
    """Generates and maintains the index in database."""

    ALLOWED_EXTS = (".doc", ".docx", ".pdf", ".ppt", ".pptx")

    def __init__(self):
        self.scraper = CMSScraper(Path(config["PATHS"]["dl_root"]), **config["MOODLE"])

    def update_index(self):
        for course_name, files in self.scraper.get_courses_docs():
            if not files:
                continue
            print("Checking", course_name, "for new docs.")
            course_docs = Doc.objects(course=course_name).only("file_path")
            doc_paths = set(doc.file_path for doc in course_docs)
            for file in files:
                file_path: Path = file["file_path"]
                if file_path.suffix not in self.ALLOWED_EXTS:
                    continue
                if str(file_path) in doc_paths:
                    # TODO: Also check updated_at of file
                    continue  # Already processed the file
                print("\tDownloading", file_path.name, end='. ')

                self.scraper.download_file(file_path, file["file_url"])
                print("Done.")
                # process(file['file_path'])  # Process the doc, store in JSON
                doc = Doc(
                    file_path=str(file_path),
                    course=course_name,
                    downloaded_at=datetime.now(),
                )
                doc.save()
                self.add_to_index(doc)

    def add_to_index(self, doc: Doc):
        pass


if __name__ == "__main__":
    Indexer().update_index()

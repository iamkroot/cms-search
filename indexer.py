from collections import Counter
from datetime import datetime
from pathlib import Path
from pathvalidate import sanitize_filepath

from cms_scraper import CMSScraper
from database import Doc, Index, IndexEntry
from extractor import extract_sentences
from preprocess import Preprocessor
from utils import config, get_real_path


class Indexer:
    """Generates and maintains the index in database."""

    ALLOWED_EXTS = (".doc", ".docx", ".pdf", ".ppt", ".pptx")

    def __init__(self):
        self.scraper = CMSScraper(Path(config["PATHS"]["dl_root"]), **config["MOODLE"])
        self.prep = Preprocessor()

    def update_index(self):
        for course_name, files in self.scraper.get_courses_docs():
            if not files:
                continue
            print("Checking", course_name, "for new docs.")
            course_docs = Doc.objects(course=course_name).only("file_path")
            doc_paths = set(doc.file_path for doc in course_docs)
            for file in files:
                file_path: Path = file["file_path"]
                sanitized_path = str(sanitize_filepath(file_path))
                if file_path.suffix not in self.ALLOWED_EXTS:
                    continue
                if sanitized_path in doc_paths:
                    # TODO: Also check updated_at of file
                    continue  # Already processed the file
                print("\tDownloading", file_path.name, end=". ")
                save_path = get_real_path(sanitized_path)
                # self.scraper.download_file(save_path, file["file_url"])
                print("Done.")
                sentences = extract_sentences(save_path)
                doc = Doc(
                    file_path=sanitized_path,
                    course=course_name,
                    downloaded_at=datetime.now(),
                )
                doc.save()
                self.add_to_index(doc, sentences)

    def add_to_index(self, doc: Doc, sentences):
        p_doc = self.prep.preprocess(" ".join(sentences))
        word_freq = Counter(p_doc)
        print("Number of unique words:", len(word_freq.keys()))
        for key, tf in word_freq.items():
            cnt = Index.objects(key=key).count()
            ie = IndexEntry(doc=doc, tf=tf)
            if cnt == 0:
                new_ent = Index(key=key)
                new_ent.documents = [ie]
                new_ent.save()
            else:
                ent = Index.objects(key=key).first()
                ent.update(add_to_set__documents=ie)
                ent.save()


if __name__ == "__main__":
    Indexer().update_index()

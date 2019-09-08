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

    # ALLOWED_EXTS = (".doc", ".docx", ".pdf", ".ppt", ".pptx")
    ALLOWED_EXTS = (".pptx",)

    def __init__(self):
        self.scraper = CMSScraper(Path(config["PATHS"]["dl_root"]), **config["MOODLE"])
        self.prep = Preprocessor()

    def update_index(self):
        """Function to download new files from CMS and add them to our MongoDB database
        """
        for course_name, files in self.scraper.get_courses_docs():
            if not files:
                continue
            print("Checking", course_name, "for new docs.")
            course_docs = Doc.objects(course=course_name).only(
                "file_path"
            )  # Get all the docs of the course
            doc_paths = set(doc.file_path for doc in course_docs)
            for file in files:
                file_path: Path = file["file_path"]
                if file_path.suffix not in self.ALLOWED_EXTS:
                    continue
                sanitized_path = str(
                    sanitize_filepath(file_path)
                )  # Remove illegal characters from the path
                if sanitized_path in doc_paths:
                    # TODO: Also check updated_at of file
                    continue  # Already processed the file
                print("\tDownloading", file_path.name, end=". ")
                save_path = get_real_path(sanitized_path)
                self.scraper.download_file(save_path, file["file_url"])
                print("Done.")
                doc = Doc(
                    file_path=sanitized_path,
                    course=course_name,
                    downloaded_at=datetime.now(),
                )
                doc.save()  # Add the new doc to DB
                sentences = extract_sentences(save_path)
                self.add_to_index(doc, sentences)

    def add_to_index(self, doc: Doc, sentences):
        """Function to add terms of the newly downloaded file to the index along with their term frequencies

        Args:
            doc (Doc) : MongoDB document/object of the downloaded file
            sentences (list) : Sentences extracted from the downloaded file
        """
        p_doc = self.prep.preprocess(" ".join(sentences))
        word_freq = Counter(p_doc)  # Prepare Hashmap with trem frequencies
        print("Number of unique words:", len(word_freq.keys()))
        for key, tf in word_freq.items():
            cnt = Index.objects(key=key).count()
            ie = IndexEntry(doc=doc, tf=tf)
            if cnt == 0:
                new_ent = Index(key=key)  # Create new index entry
                new_ent.documents = [ie]
                new_ent.save()
            else:
                ent = Index.objects(key=key).first()
                ent.update(
                    add_to_set__documents=ie
                )  # Update document list in the Index Entry
                ent.save()


if __name__ == "__main__":
    Indexer().update_index()

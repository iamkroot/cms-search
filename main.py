from preprocess import Preprocessor
from database import Doc, Index, IndexEntry

doc = Index.objects(key="i/o").first()
if doc:
    print(len(doc.documents))

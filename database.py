import mongoengine as me
from utils import config


class Doc(me.Document):
    _id = me.SequenceField(primary_key=True)
    file_path = me.StringField()
    course = me.StringField()
    num_terms = me.IntField()
    downloaded_at = me.DateTimeField()


class IndexEntry(me.EmbeddedDocument):
    doc = me.ReferenceField(Doc)
    tf = me.IntField()


class Index(me.Document):
    key = me.StringField()
    documents = me.SortedListField(me.EmbeddedDocumentField(IndexEntry), ordering="doc")
    meta  = {
        'indexes' : ['#key']
    }

print("Connecting to database.")
me.connect(**config["DB"])

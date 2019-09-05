import mongoengine as me
from utils import config


class Course(me.Document):
    name = me.StringField()
    documents = me.ListField(me.ReferenceField("Doc"))


class Doc(me.Document):
    _id = me.SequenceField()
    file_path = me.StringField()
    course = me.ReferenceField(Course)
    num_terms = me.IntField()
    downloaded_at = me.DateTimeField()


class IndexEntry(me.EmbeddedDocument):
    doc = me.ReferenceField(Doc)
    tf = me.IntField()


class Index(me.Document):
    key = me.StringField()
    documents = me.SortedListField(me.EmbeddedDocumentField(IndexEntry), ordering="doc")


print("Connecting to database.", end=' ')
me.connect(**config["DB"])
print("Done.")

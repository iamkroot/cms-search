from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer


class Preprocessor:
    """
        Preprocessor class provides methods to tokenize, lemmatize and remove stopwords
    """

    def __init__(self):
        self.stop_words = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        self.tokenizer = RegexpTokenizer(r'\w[\w-]+|\w[\w/]+')
        self.pattern = r"(?x)([A-Z]\.)+|\$?\d+(\.\d+)?%?|\w+([-']\w+)*|[+/\-@&*]"

    def tokenize(self, sent):
        return self.tokenizer.tokenize(sent)

    def lemmatize(self, tokens):
        return [self.lemmatizer.lemmatize(w.lower()) for w in tokens]

    def rem_stop(self, tokens):
        return [w for w in tokens if "-" in w or w.lower() not in self.stop_words]

    def preprocess(self, text):
        p_doc = self.tokenize(text)
        p_doc = self.rem_stop(p_doc)
        return self.lemmatize(p_doc)

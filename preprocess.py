import nltk
import glob
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer

class Preprocessor:
    """
        Preprocessor class provides methods to tokenize, lemmatize and remove stopwords
    """
    def __init__(self, path):
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        self.tokenizer = RegexpTokenizer(r'\w+')
        self.filepath = path
        self.fileNames = []
        self.files = []

    def extract_files(self):
        direc = glob.glob(self.filepath + "/*.txt")
        direc.sort()
        self.fileNames = direc;
        contents = []
        for d in direc:
            f = open(d);
            contents.append(f.read())
        return contents

    def tokenize(self,sent):
        return self.tokenizer.tokenize(sent)

    def lemmatize(self,tokens):
        return [self.lemmatizer.lemmatize(w) for w in tokens]

    def rem_stop(self,tokens):
        return [w for w in tokens if w.lower() not in self.stop_words]

    def preprocess(self):
        files = self.extract_files()
        # print(len(files), len(files[1]))
        prep = []
        for f in files:
            p = []
            p = self.tokenize(f)
            p = self.rem_stop(p);
            p = self.lemmatize(p);
            prep.append(p)
        print(prep[0])

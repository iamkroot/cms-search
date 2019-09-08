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
        self.tokenizer = RegexpTokenizer(r"\w[\w-]+|\w[\w/]+")

    def tokenize(self, sent):
        """Tokenizes the input into ref_words
        Args:
            sent (str) : Sentence to be tokenized
        Returns:
            list : List of tokenized words
        """
        return self.tokenizer.tokenize(sent)

    def rem_stop(self, tokens):
        """Removes stop words from input tokens
        Args:
        tokens(list) : List of tokens
        Returns:
        list: List of tokens with stopwords removed
        """
        return (w for w in tokens if "-" in w or w.lower() not in self.stop_words)

    def lemmatize(self, tokens):
        """Returns Base forms (lemmatizes) of input list of words
        Args:
            tokens(list) : List of tokens
        Returns:
            list : List of lemmatized tokens
        """
        return (self.lemmatizer.lemmatize(w.lower()) for w in tokens)

    def preprocess(self, text):
        """Preprocesses the input text
        Args:
            text (str) : Text to be pre-processed
        Returns:
            list : List of pre-processed tokens
        """
        p_doc = self.tokenize(text)
        p_doc = self.rem_stop(p_doc)
        return list(self.lemmatize(p_doc))

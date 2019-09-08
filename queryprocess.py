from collections import defaultdict
from preprocess import Preprocessor
from database import Index, Doc, IndexEntry
import math
import json
from pathlib import Path
from nltk.corpus import wordnet as wn
from nltk.corpus import genesis
from utils import get_real_path


class QueryProcessor:
    """
        Class which contain methods to process the query and return the results
    """

    def __init__(self):
        self.prep = Preprocessor()
        self.genesis_ic = wn.ic(genesis, False, 0.0)

    def get_docs(self, query):
        """ Retrieve the mongodb objects of the query word that contains the inverted index list along with the tf of that word.
            idf is also calculated and stored.

            Args:
                query (list): The preprocessed search query as a list of words.

            Returns:
                dict: key is the query word and the value is an object with the word's idf and the inverted index list.

        """
        data = {}
        tot_docs = Doc.objects().count()
        for word in query:
            ind = Index.objects(key=word).first()
            if not ind:
                continue
            data[word] = {
                "idf": math.log(
                    tot_docs / len(ind.documents), 10
                ),  # calculate idf of the query word
                "docs": ind.documents,  # Documents which contain word
            }
        return data

    def jc_sim(self, sent, ref_words):
        """Calculate Similarity score between the query and a sentence of the document
        Args:
            sent(str) : Sentence from the document
            ref_words : Preprocessed Query
        Returns:
            int : Similarity score between the sentence and the query
        """
        sim = 0
        words = self.prep.preprocess(sent)
        if len(words) < 5:
            return 0
        for w in words:
            maxi = 0
            for w1 in wn.synsets(w):
                for t in ref_words:
                    for w2 in wn.synsets(t):
                        if (
                            w1._pos in ("n", "v", "a", "r")
                            and w2._pos in ("n", "v", "a", "r")
                            and w1._pos == w2._pos
                        ):
                            n = w1.jcn_similarity(
                                w2, self.genesis_ic
                            )  # calculate Jiang Conrath Similarity between two words
                            if w1 == w2 or n > 1:
                                maxi += 10
                            else:
                                maxi = max(maxi, n)
            sim += maxi
        return sim / max(len(ref_words), len(words))

    def fetch_top_n(self, query, n=5):
        """ Fetch the best n documents out of all based on the tf-idf score.

            Args:
                query (str): Pre-processed query
                n (int) : The number of relevant documents to be fetched

            Returns:
                list : The best n documents based on tf-idf score.

        """
        all_docs = self.get_docs(query)
        ranks = defaultdict(int)
        for word, data in all_docs.items():
            for d in data["docs"]:
                ranks[d.doc] += d.tf * data["idf"]
        ranks = sorted(ranks.items(), key=lambda kv: -kv[1])
        return list(ranks)[:n]

    def process_query(self, query):
        """  Computes and retrieves the result of the query

             Args:
                query (str): The search query given by the user.

             Returns:
                list : It contians the document paths and the best 5 sentences for the corresponding document .

        """
        query = self.prep.preprocess(query)
        ranks = self.fetch_top_n(query)
        ans = []
        for r in ranks:
            file_path = Path(r[0].file_path)
            # print(file_path.name,file_path.parent.parent.parent )
            new_path = file_path.with_suffix(".json")
            new_path = get_real_path(new_path)
            with open(new_path, "r") as f:
                data = set(json.load(f)["sentences"])
                sen = tuple((self.jc_sim(s, query), s) for s in data)
                best = tuple(sorted(sen, key=lambda x: -x[0]))[
                    :5
                ]  # Slice top five sentences
                ans.append((file_path, best))
        return ans

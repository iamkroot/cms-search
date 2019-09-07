from preprocess import Preprocessor
from database import Index, Doc, IndexEntry
import math

class QueryProcessor:
    """
        Class which contain methods to process the query and return the results
    """
    def __init__(self):
        self.prep = Preprocessor()

    def query_prep(self,query):
        q = self.prep.tokenize(query)
        q = self.prep.rem_stop(q)
        q = self.prep.lemmatize(q)
        return q


    def get_docs(self,query):
        docs = []
        idf = {}
        cnt = Doc.objects().count()
        for q in query:
            ind = Index.objects(key=q).first()
            if ind:
                docs.append(ind.documents)
                idf[q] = math.log(cnt/len(ind.documents),10)
        return docs,idf

    def process_query(self,query):
        query = self.query_prep(query)
        docs,idf = self.get_docs(query)
        for p in docs:
            for i in range(len(p)):
                print(p[i].doc.id, p[i].tf)
        print(idf)

if __name__ == "__main__":
    query = input("Enter a query: ")
    qp = QueryProcessor()
    qp.process_query(query)

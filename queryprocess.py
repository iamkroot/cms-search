from preprocess import Preprocessor
from database import Index, Doc, IndexEntry
import math
import json
from pathlib import Path
from nltk.corpus import wordnet as wn
from nltk.corpus import genesis

class QueryProcessor:
    """
        Class which contain methods to process the query and return the results
    """
    def __init__(self):
        self.prep = Preprocessor()
        self.genesis_ic=wn.ic(genesis, False, 0.0)

    def query_prep(self,query):
        q = self.prep.tokenize(query)
        q = self.prep.rem_stop(q)
        q = self.prep.lemmatize(q)
        return q


    def get_docs(self,query):
        docs = []
        nq = []
        idf = {}
        cnt = Doc.objects().count()
        for q in query:
            ind = Index.objects(key=q).first()
            if ind:
                docs.append(ind.documents)
                idf[q] = math.log(cnt/len(ind.documents),10)
                nq.append(q)
        return docs,idf,nq

    def jc_sim(self,s,ref_words):
        num=0
        words=self.prep.tokenize(s)
        words = self.prep.rem_stop(words)
        words = self.prep.lemmatize(words)
        l=max(len(ref_words),len(words))
        for w in words:
          maxi=0
          for w1 in wn.synsets(w):
            for t in ref_words:
              for w2 in wn.synsets(t):
                if w1._pos in ('n','v','a','r') and w2._pos in ('n','v','a','r') and w1._pos==w2._pos:
                  n=w1.jcn_similarity(w2,self.genesis_ic)
                  if w1==w2 or n>1:
                    maxi=maxi+10
                  else:
                    maxi=max(maxi,w1.jcn_similarity(w2,self.genesis_ic))
          num=num+maxi
        num=num/l
        return num

    def process_query(self,query):
        query = self.query_prep(query)
        docs,idf,query = self.get_docs(query)
        rank = {}
        for i in range(len(docs)):
            q = query[i]
            for d in docs[i]:
                if d.doc in rank.keys():
                    rank[d.doc] = rank[d.doc] + d.tf*idf[q]
                else:
                    rank[d.doc] = d.tf*idf[q]
        rank = sorted(rank.items(), key=lambda kv: -kv[1])
        if len(rank)>5:
            rank = rank[:5]
        ans=[]
        for r in rank:
            file_path = Path(r[0].file_path)
            # print(file_path.name,file_path.parent.parent.parent )
            new_path = file_path.with_suffix('.json')
            new_path = "data/" + str(new_path)
            with open(new_path,'r') as f:
                data = json.load(f)["sentences"]
                data = set(data)
                sen = []
                for s in data:
                    sen.append((self.jc_sim(s,query),s))
                best = sorted(sen, key=lambda x: -x[0])
                if len(best) > 5:
                    best=best[:5]
                ans.append((file_path.name,file_path.parent.parent.parent,best))
                # print("\n","\n")
        return ans


if __name__ == "__main__":
    query = input("Enter a query: ")
    qp = QueryProcessor()
    answer = qp.process_query(query)
    for ans in answer:
        print(ans[1],ans[0],'\n')
        for s in ans[2]:
            print(s[1])
        print('\n','\n')

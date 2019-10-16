from queryprocess import QueryProcessor
from database import connect as db_connect


def main():
    query = input("Enter a query: ")
    qp = QueryProcessor()
    answer = qp.process_query(query)
    for ans in answer:
        print(ans[0], "\n")
        for s in ans[1]:
            print(s[1], ".....", sep="")
        print("\n", "\n")


if __name__ == "__main__":
    db_connect()
    main()

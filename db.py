import chromadb
from chromadb.config import Settings

class DB:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(name="Articles")
        # print(len(self.collection.get(include=["documents"])["documents"]))
        

    def add(self, documents, metadatas, ids):
        self.collection.add(documents=documents, metadatas=metadatas, ids=ids)

    def query(self, query_texts, n_results):
        return self.collection.query(query_texts=query_texts, n_results=n_results)


if __name__ == "__main__":
    db = DB()
    # db.add_test_data()
    # results = db.query(query_texts=["Technology"], n_results=2)
    # print(results)
    print(len(db.collection.get(include=["documents"])["documents"]))
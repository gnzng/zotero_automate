import chromadb
from sentence_transformers import SentenceTransformer

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chromadb_data")

# Get existing collection
collection = client.get_collection(name="pdf_rag")

# Load open-source embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def search(query, top_k=5):
    query_embedding = embedder.encode([query])[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    return results["documents"][0], results["ids"][0]


docs, ids = search("Sum rules")
for doc, id_ in zip(docs, ids):
    print(f"ID: {id_}\nDocument: {doc}\n{'-'*40}")

import os
import pdfplumber
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()
ZOTERO_DB_PATH = os.getenv("ZOTERO_DB_PATH", "")
ZOTERO_STORAGE_PATH = os.path.join(os.path.dirname(ZOTERO_DB_PATH), "storage")


# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chromadb_data")

# Create or get collection
collection = client.get_or_create_collection(name="pdf_rag")

# Load open-source embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def extract_text_from_pdf(pdf_path):
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                texts.append(text)
    return texts


def add_pdf_to_chromadb(pdf_path):
    texts = extract_text_from_pdf(pdf_path)
    embeddings = embedder.encode(texts)
    ids = [f"{os.path.basename(pdf_path)}_page_{i}" for i in range(len(texts))]
    # Check which IDs already exist
    existing = collection.get(ids=ids)
    existing_ids = set(existing["ids"]) if existing and "ids" in existing else set()
    # Filter out already existing IDs
    new_indices = [i for i, id_ in enumerate(ids) if id_ not in existing_ids]
    if new_indices:
        new_embeddings = [embeddings[i] for i in new_indices]
        new_texts = [texts[i] for i in new_indices]
        new_ids = [ids[i] for i in new_indices]
        collection.add(embeddings=new_embeddings, documents=new_texts, ids=new_ids)


def query_rag(question, top_k=3):
    question_embedding = embedder.encode([question])[0]
    results = collection.query(query_embeddings=[question_embedding], n_results=top_k)
    return results["documents"][0]


# Add all PDFs directly from Zotero storage (no folder recursion)
for item in os.listdir(ZOTERO_STORAGE_PATH):
    if item.startswith('.'):
        continue
    item_folder = os.path.join(ZOTERO_STORAGE_PATH, item)
    if not os.path.isdir(item_folder):
        continue
    item_path = None
    for file in os.listdir(item_folder):
        if file.startswith('.'):
            continue
        potential_path = os.path.join(item_folder, file)
        if os.path.isfile(potential_path) and potential_path.lower().endswith(".pdf"):
            item_path = potential_path
            break
    if item_path is not None:
        print(f"Processing PDF: {item_path}...")
        try:
            add_pdf_to_chromadb(item_path)
        except Exception as e:
            print(f"Error processing {item_path}: {e}")

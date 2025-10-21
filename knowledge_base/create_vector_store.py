# knowledge_base/create_vector_store.py
import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

# Dummy documents
texts = [
    "User Alice accessed sensitive files",
    "User Bob performed unusual login attempts",
    "User Eve triggered multiple security alerts"
]

metadatas = [{"text": t} for t in texts]

# Initialize Ollama embeddings (replace 'llama3' with your local model)
embeddings = OllamaEmbeddings(model="llama3")

# Create FAISS vector store
vectorstore = FAISS.from_texts(texts, embedding=embeddings, metadatas=metadatas)

# Save index locally
index_path = "knowledge_base/faiss_index"
os.makedirs(index_path, exist_ok=True)
vectorstore.save_local(index_path)

print(f"✅ FAISS index saved locally at {index_path}")

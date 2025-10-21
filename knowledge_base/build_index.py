import os
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document

def build_index():
    docs_dir = "knowledge_base/recovery_docs"
    files = [os.path.join(docs_dir, f) for f in os.listdir(docs_dir) if f.endswith((".txt", ".md"))]

    documents = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
        documents.append(Document(page_content=content, metadata={"source": file}))

    print(f"📄 Loaded {len(documents)} documents.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    print(f"🔹 Split into {len(chunks)} text chunks.")

    embeddings = OpenAIEmbeddings()  # you can replace with OllamaEmbeddings() or HFEmbeddings()
    vectorstore = FAISS.from_documents(chunks, embedding=embeddings)

    with open("knowledge_base/vector_store.pkl", "wb") as f:
        pickle.dump(vectorstore, f)

    print("✅ FAISS index built and saved at 'knowledge_base/vector_store.pkl'")

if __name__ == "__main__":
    build_index()

from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling.chunking import HybridChunker
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

docs = [
    "./documents/eda_insights.md",
    "./documents/feature_importance.md",
    "./documents/fraud_patterns.md",
    "./documents/transaction_indicators.md"
]

# Load and chunk all documents at once
loader = DoclingLoader(
    file_path=docs,
    export_type=ExportType.DOC_CHUNKS,
    chunker=HybridChunker(tokenizer=EMBED_MODEL_ID)
)

chunks = loader.load()
print(f"✓ Loaded {len(chunks)} chunks")

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)

# Create vector store (one step!)
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
    collection_name="fraud_analysis_docs"
)

print("✓ Vector store created!")

# Test query
results = vectorstore.similarity_search("fraud patterns", k=3)
for i, result in enumerate(results, 1):
    print(f"\n{i}. {result.page_content[:150]}...")
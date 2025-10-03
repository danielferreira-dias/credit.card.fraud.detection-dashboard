from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_docling import DoclingLoader
from langchain_docling.loader import ExportType
from docling.chunking import HybridChunker
from langchain_huggingface import HuggingFaceEmbeddings
import os 
from dotenv import load_dotenv

load_dotenv()

docs = [
    "./documents/eda_insights.md",
    "./documents/feature_importance.md",
    "./documents/fraud_patterns.md",
    "./documents/transaction_indicators.md"
]

EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

if __name__ == "__main__":
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)
    
    # Load and chunk documents using Docling
    loader = DoclingLoader(
        file_path=docs,
        export_type=ExportType.DOC_CHUNKS,
        chunker=HybridChunker(tokenizer=EMBED_MODEL_ID)
    )
    
    documents = loader.load()
    print(f"Loaded {len(documents)} chunks from {len(docs)} documents")
    
    vectorstore = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
        index_name="fraud-analysis-docs",
        embedding_function=embeddings,
        semantic_configuration_name="my-semantic-config",  # Optional: for semantic search
    )
    
    # Add documents to the index
    vectorstore.add_documents(documents=documents)
    
    print(f"✓ Successfully indexed {len(documents)} chunks to Azure AI Search!")
    
    # Test similarity search
    while True:
        user_query = input()
        if user_query == "quit":
            print('Chat Finished')
            break
        # Perform hybrid search (vector + semantic)
        results = vectorstore.similarity_search(query="fraud detection patterns", k=5, search_type="hybrid")
        for i, result in enumerate(results, 1):
            print(f"\n{'='*60}")
            print(f"Result {i}:")
            print(f"Content: {result.page_content[:400]}...")
            print(f"Metadata: {result.metadata}")
            print(f"{'='*60}")

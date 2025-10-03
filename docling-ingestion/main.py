from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer
from docling.document_converter import DocumentConverter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from langchain.schema import Document  # ADDED: Need this for LangChain documents
import os
from dotenv import load_dotenv

load_dotenv()
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
docs = [
    "./documents/eda_insights.md",
    "./documents/feature_importance.md",
    "./documents/fraud_patterns.md",
    "./documents/transaction_indicators.md"
]

DATABASE_URL = os.getenv("DATABASE_URL_LOCAL")
CONNECTION_STRING = DATABASE_URL.replace("@postgres:", "@localhost:")
if not CONNECTION_STRING.startswith("postgresql+psycopg://"):
    CONNECTION_STRING = CONNECTION_STRING.replace("postgresql://", "postgresql+psycopg://")

COLLECTION_NAME = "fraud_analysis_docs"

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")

print(f"Connecting to: {CONNECTION_STRING.replace(os.getenv('POSTGRES_PASSWORD', 'postgres'), '***')}")
class DocumentTokenizer:
    def __init__(self, model_id: str, max_tokens: int):
        self.tokenizer = HuggingFaceTokenizer(
            tokenizer=AutoTokenizer.from_pretrained(model_id),
            max_tokens=max_tokens
        )
class DocumentChunker:
    def __init__(self, tokenizer: DocumentTokenizer):
        self.chunker = HybridChunker(
            tokenizer=tokenizer.tokenizer,
            merge_peers=True
        )
    
    def chunk_doc(self, document) -> list:
        chunk_iter = self.chunker.chunk(dl_doc=document)
        return list(chunk_iter)
    
    def contextualize(self, chunk):
        return self.chunker.contextualize(chunk=chunk)

def proccess_documents():
    # Initialize components
    tokenizer = DocumentTokenizer(model_id=EMBED_MODEL_ID, max_tokens=512)
    chunker = DocumentChunker(tokenizer=tokenizer)
    converter = DocumentConverter()

    # Initialize embeddings model
    # OPTION A: Azure OpenAI Embeddings
    #embeddings = AzureOpenAIEmbeddings(
    #    azure_deployment="text-embedding-3-small",  # your deployment name
    #    openai_api_key="your-api-key",
    #    azure_endpoint="your-endpoint",
    #    openai_api_version="2024-10-21"
    #)
    
    # Initialize embeddings model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # FIXED: Create list to store LangChain Document objects
    langchain_documents = []
    
    for doc_path in docs:
        print(f"\nProcessing: {doc_path}")
        
        # Convert document
        result = converter.convert(doc_path)
        doc = result.document
        
        # Chunk document
        chunks = chunker.chunk_doc(doc)
        print(f"Generated {len(chunks)} chunks")
        
        # Embed each chunk
        for i, chunk in enumerate(chunks):
            enriched_text = chunker.contextualize(chunk=chunk)
            
            # FIXED: Create LangChain Document object
            # (Chroma needs LangChain Document objects, not dicts)
            langchain_doc = Document(
                page_content=enriched_text,
                metadata={
                    "source": doc_path,
                    "chunk_index": i,
                    "chunk_id": f"{doc_path}_{i}",
                }
            )
            
            langchain_documents.append(langchain_doc)
            
            # Optional: Print for debugging
            if i == 0:  # Just print first chunk of each doc
                print(f"First chunk preview: {enriched_text}...")
    
    print(f"\n✓ Total chunks to store: {len(langchain_documents)}")

    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=CONNECTION_STRING,
        use_jsonb=True,  # Store metadata as JSONB for better querying
    )
    
    print("Storing documents in pgvector...")
    vectorstore.add_documents(langchain_documents)
    print("✓ All chunks stored in PostgreSQL!")
    
    return vectorstore

    # Now you can insert into your vector database
    # Example for different databases:
    
    # --- Azure AI Search ---
    # from azure.search.documents import SearchClient
    # from azure.core.credentials import AzureKeyCredential
    # 
    # search_client = SearchClient(
    #     endpoint="your-endpoint",
    #     index_name="your-index",
    #     credential=AzureKeyCredential("your-key")
    # )
    # 
    # for chunk in all_chunks_with_embeddings:
    #     search_client.upload_documents(documents=[{
    #         "chunk_id": chunk["id"],
    #         "content": chunk["text"],
    #         "content_vector": chunk["embedding"],
    #         "source": chunk["source"]
    #     }])

def query_vectorstore():
    """Query existing vectorstore"""
    print("\nConnecting to vectorstore...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)
    
    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=CONNECTION_STRING,
    )
    
    print("✓ Connected to pgvector database!")
    
    # Interactive query loop
    print("\n--- Vector Search Interface ---")
    print("Enter your query (or 'quit' to exit):")
    
    while True:
        user_query = input("\nQuery: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_query:
            continue
        
        try:
            results_with_scores = vectorstore.similarity_search_with_score(user_query, k=3)
            
            if not results_with_scores:
                print("No results found.")
                continue
            
            for i, (result, score) in enumerate(results_with_scores, 1):
                print(f"\n{'='*60}")
                print(f"Result {i} (Score: {score:.4f}):")
                print(f"Content: {result.page_content}...")
                print(f"Source: {result.metadata.get('source', 'Unknown')}")
                print(f"{'='*60}")
        except Exception as e:
            print(f"Error during search: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "query":
        # Run in query mode: python main.py query
        query_vectorstore()
    else:
        # Run in ingestion mode: python main.py
        proccess_documents()
        print("\n" + "="*60)
        print("Ingestion complete! Run 'python main.py query' to search.")
        print("="*60)

  
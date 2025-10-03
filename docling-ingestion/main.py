from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from transformers import AutoTokenizer
from docling.document_converter import DocumentConverter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma, PGVector
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

# Database connection string
CONNECTION_STRING = os.getenv("DATABASE_URL")
COLLECTION_NAME = "fraud_analysis_docs"


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

    vectorstore = PGVector(
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
        embeddings=embeddings,
        use_jsonb=True,  # Store metadata as JSONB for better querying
    )
    
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
                    # You can add more metadata from chunk.meta if needed
                }
            )
            
            langchain_documents.append(langchain_doc)
            
            # Optional: Print for debugging
            if i == 0:  # Just print first chunk of each doc
                print(f"First chunk preview: {enriched_text}...")
    
    print(f"\n✓ Total chunks to store: {len(langchain_documents)}")
    
     # Add to pgvector
    print("\nStoring in pgvector...")
    vectorstore.add_documents(langchain_documents)
    print("✓ All chunks stored in PostgreSQL!")

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
    
    # --- Pinecone ---
    # import pinecone
    # 
    # index = pinecone.Index("your-index-name")
    # vectors_to_upsert = [
    #     (chunk["id"], chunk["embedding"], {"text": chunk["text"], "source": chunk["source"]})
    #     for chunk in all_chunks_with_embeddings
    # ]
    # index.upsert(vectors=vectors_to_upsert)
    
    # --- ChromaDB ---
    # import chromadb
    # 
    # client = chromadb.Client()
    # collection = client.create_collection("fraud_docs")
    # collection.add(
    #     ids=[chunk["id"] for chunk in all_chunks_with_embeddings],
    #     embeddings=[chunk["embedding"] for chunk in all_chunks_with_embeddings],
    #     documents=[chunk["text"] for chunk in all_chunks_with_embeddings],
    #     metadatas=[{"source": chunk["source"]} for chunk in all_chunks_with_embeddings]
    # )

if __name__ == "__main__":
    # Initialize embeddings (same as when you created it)
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)
    
    # Connect to existing vectorstore
    vectorstore = PGVector(
        collection_name=COLLECTION_NAME,
        connection_string=CONNECTION_STRING,
        embeddings=embeddings,
    )
    
    print("✓ Connected to pgvector database!")
    
    print("✓ Vectorstore loaded successfully!")
    print(f"✓ Collection contains {vectorstore._collection.count()} documents\n")
    
    # Interactive query loop
    print("--- Testing retrieval ---")
    print("Enter your query (or 'quit' to exit):")
    
    while True:
        user_query = input("\nQuery: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_query:
            continue
        
        # FIXED: Use user_query variable, not 'query'
        results_with_scores = vectorstore.similarity_search_with_score(user_query, k=3)

        for i, (result, score) in enumerate(results_with_scores, 1):
            print(f"\nResult {i} (Score: {score:.4f}):")
            print(f"Content: {result.page_content}...")
            print(f"Source: {result.metadata.get('source', 'Unknown')}")

  
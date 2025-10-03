from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_huggingface import HuggingFaceEmbeddings
import os 
from dotenv import load_dotenv

load_dotenv()
INDEX_NAME = "fraud-analysis-docs"
EMBED_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"

if __name__ == "__main__":
    # Initialize embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL_ID)
    
    # Connect to existing index
    vectorstore = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
        index_name=INDEX_NAME,
        embedding_function=embeddings,
    )
    
    print("✓ Connected to Azure AI Search!")
    
    # Interactive query loop
    print("\n--- Fraud Detection Document Search ---")
    print("Enter your query (or 'quit' to exit):")
    
    while True:
        user_query = input("\nQuery: ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not user_query:
            continue
        
        # Perform hybrid search
        results = vectorstore.similarity_search( query=user_query, k=5, search_type="hybrid" )
        
        if not results:
            print("No results found.")
            continue
        
        for i, result in enumerate(results, 1):
            print(f"\n{'='*60}")
            print(f"Result {i}:")
            print(f"Content: {result.page_content}...")
            print(f"Source: {result.metadata.get('source', 'Unknown')}")
            print(f"{'='*60}")
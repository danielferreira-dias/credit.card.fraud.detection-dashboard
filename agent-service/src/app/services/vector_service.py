import os
from langchain_community.vectorstores.azuresearch import AzureSearch
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from infra.logging import get_agent_logger
import asyncio

logger = get_agent_logger("Vector Service Logger", "INFO")

class EmbeddingModel:
    def __init__(self, model_id : str):
        self.embeddings = HuggingFaceEmbeddings(model_name=model_id)

class AzureVectorService:
    def __init__(self, embedding_model : EmbeddingModel):
        # Connect to existing index
        self.embedding_model = embedding_model
        self.vectorstore = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_KEY"),
            index_name=os.getenv("INDEX_NAME"),
            embedding_function=embedding_model.embeddings,
        )
        logger.info('✓ Connected to Azure AI Search!')
    
    async def search_documents(self, user_query: str, k: int = 5):
        """Async vector similarity search"""
        results = await self.vectorstore.asimilarity_search( query=user_query, k=k )
        
        return [{
            'Content': result.page_content,
            'Source': result.metadata.get('source', 'Unknown'),
            'Metadata': result.metadata
        } for result in results]
    
    async def hybrid_search_documents(self, user_query: str, k: int = 5):
        """Async hybrid search (vector + keyword)"""
        try:
            results = await self.vectorstore.ahybrid_search( query=user_query, k=k )
        except AttributeError:
            # Fallback to regular similarity search if hybrid not available
            results = await self.vectorstore.asimilarity_search( query=user_query, k=k)
        
        return [{
            'Content': result.page_content,
            'Source': result.metadata.get('source', 'Unknown'),
            'Score': result.metadata.get('@search.score', None)
        } for result in results]
        
class PGVectorService:
    def __init__(self, embedding_model : EmbeddingModel):
        # Connect to existing index
        self.embedding_model = embedding_model
        self.vectorstore = PGVector(
            embeddings=embedding_model.embeddings,
            collection_name="fraud_analysis_docs",
            connection=os.getenv('DATABASE_URL'),
        )
        logger.info('✓ Connected to PGVector!')
    
    async def search_documents(self, user_query: str, k: int = 5):
        """Async vector similarity search"""
        results = await self.vectorstore.asimilarity_search( query=user_query, k=k )
        
        return [{
            'Content': result.page_content,
            'Source': result.metadata.get('source', 'Unknown'),
            'Metadata': result.metadata
        } for result in results]

# Usage example
async def main():
    embedding_model = EmbeddingModel( model_id="sentence-transformers/all-MiniLM-L6-v2" )
    service = AzureVectorService( embedding_model=embedding_model )
    
    # Vector search
    results = await service.search_documents("What are fraud patterns?")
    
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Content: {result['Content'][:200]}...")
        print(f"Source: {result['Source']}")

if __name__ == "__main__":
    asyncio.run(main())
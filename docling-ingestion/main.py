from docling.chunking import HierarchicalChunker
from docling.document_converter import DocumentConverter

# Convert your markdown file
converter = DocumentConverter()
result = converter.convert("./documents/feature_importance.md")
doc = result.document

# Apply hierarchical chunking
chunker = HierarchicalChunker()
chunks = list(chunker.chunk(doc))

# Extract text from chunks
all_chunks = []
for idx, chunk in enumerate(chunks):
    chunk_text = chunk.text
    all_chunks.append((f"chunk_{idx}", chunk_text))
"""
Check ChromaDB distance function and configuration
"""

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
import chromadb

load_dotenv()

# Initialize
embeddings = OpenAIEmbeddings(
    base_url=os.getenv("EMBEDDINGS_BASE_URL"),
    model=os.getenv("EMBEDDINGS_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder")
)

chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

print("Checking ChromaDB Configuration...")
print()

# Access underlying ChromaDB client
client = chromadb.PersistentClient(path=chroma_dir)
collections = client.list_collections()

print(f"Collections: {[c.name for c in collections]}")
print()

# Get the collection
collection = client.get_collection("rag_documents")

print(f"Collection: {collection.name}")
print(f"  Count: {collection.count()}")
print(f"  Metadata: {collection.metadata}")
print()

# Check distance function
# ChromaDB uses 'l2', 'cosine', or 'ip' (inner product)
print("Checking distance function...")

# Try to peek at results with distance
results = collection.query(
    query_texts=["attention mechanism"],
    n_results=5,
    include=["metadatas", "distances", "documents"]
)

print(f"\nQuery: 'attention mechanism'")
print(f"Distances returned: {results['distances'][0]}")
print(f"Number of dimensions: Should be 4096")
print()

# Check if using L2 or cosine
# Cosine similarity is normalized, L2 distance is not
# Cosine similarity: closer to 1 is more similar
# L2 distance: closer to 0 is more similar

print("Distance function analysis:")
if max(results['distances'][0]) < 2.0:
    print("  Likely using: COSINE similarity (distances are small)")
    print("  ChromaDB returns: 1 - cosine_similarity (lower is better)")
    print("  So ChromaDB distance 0.7260 = cosine similarity 0.2740")
else:
    print("  Likely using: L2 distance (Euclidean)")

print()
print("Note: ChromaDB's similarity_search_with_relevance_scores() converts:")
print("  relevance_score = 1 - distance")
print("  So distance=0.7260 becomes score=0.2740")
print()

# Test: Query with very specific attention paper content
print("Testing with specific attention paper query...")
specific_query = "transformer architecture self-attention multi-head scaled dot product"
results2 = collection.query(
    query_texts=[specific_query],
    n_results=10,
    include=["metadatas", "distances"]
)

print(f"\nQuery: '{specific_query}'")
for i, (dist, meta) in enumerate(zip(results2['distances'][0], results2['metadatas'][0])):
    source = meta.get('source', 'Unknown')
    if '\\' in source or '/' in source:
        source = source.split('\\')[-1].split('/')[-1]
    score = 1 - dist
    print(f"  {i+1}. {source}: distance={dist:.4f}, score={score:.4f}")

# Count chunks per document
print("\nChunk distribution in vector store:")
all_results = collection.get(include=["metadatas"])
doc_counts = {}
for meta in all_results['metadatas']:
    source = meta.get('source', 'Unknown')
    if '\\' in source or '/' in source:
        source = source.split('\\')[-1].split('/')[-1]
    doc_counts[source] = doc_counts.get(source, 0) + 1

for source, count in sorted(doc_counts.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / collection.count()) * 100
    print(f"  {source}: {count} chunks ({percentage:.1f}%)")

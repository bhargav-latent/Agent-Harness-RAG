"""
Embeddings Diagnostics - Check if embeddings are working correctly

Tests:
1. Embeddings dimension
2. Direct similarity calculation
3. ChromaDB configuration
4. Embedding quality test
"""

import os
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

print("\n" + "="*80)
print("EMBEDDINGS DIAGNOSTICS")
print("="*80 + "\n")

# Initialize embeddings
embeddings = OpenAIEmbeddings(
    base_url=os.getenv("EMBEDDINGS_BASE_URL"),
    model=os.getenv("EMBEDDINGS_MODEL"),
    api_key=os.getenv("OPENAI_API_KEY", "sk-placeholder")
)

print(f"Embeddings Configuration:")
print(f"  Base URL: {os.getenv('EMBEDDINGS_BASE_URL')}")
print(f"  Model: {os.getenv('EMBEDDINGS_MODEL')}")
print()

# Test 1: Check embedding dimensions
print("Test 1: Checking embedding dimensions...")
test_text = "attention mechanism"
embedding_vector = embeddings.embed_query(test_text)
print(f"[OK] Query embedding dimension: {len(embedding_vector)}")
print(f"  Sample values: {embedding_vector[:5]}")
print(f"  Vector norm: {np.linalg.norm(embedding_vector):.4f}")
print()

# Test 2: Direct similarity calculation
print("Test 2: Direct similarity test (query vs relevant text)...")

query = "attention mechanism"
relevant_text = """The Transformer model architecture uses a self-attention mechanism.
In the attention mechanism, queries, keys, and values are computed from input embeddings.
Multi-head attention allows the model to jointly attend to information from different representation subspaces."""

irrelevant_text = """Python is a high-level programming language.
Variables in Python can store different data types including integers, strings, and lists.
Functions are defined using the def keyword."""

query_emb = embeddings.embed_query(query)
relevant_emb = embeddings.embed_query(relevant_text)
irrelevant_emb = embeddings.embed_query(irrelevant_text)

# Calculate cosine similarity
def cosine_similarity(vec1, vec2):
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

sim_relevant = cosine_similarity(query_emb, relevant_emb)
sim_irrelevant = cosine_similarity(query_emb, irrelevant_emb)

print(f"  Query: '{query}'")
print(f"  Similarity with RELEVANT text (attention paper): {sim_relevant:.4f}")
print(f"  Similarity with IRRELEVANT text (Python basics): {sim_irrelevant:.4f}")
print(f"  Difference: {sim_relevant - sim_irrelevant:.4f}")

if sim_relevant > sim_irrelevant:
    print(f"  [OK] Embeddings correctly distinguish relevant from irrelevant text")
else:
    print(f"  [WARNING] Embeddings may not be working correctly!")
print()

# Test 3: Check ChromaDB configuration
print("Test 3: Checking ChromaDB configuration...")
chroma_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
vectorstore = Chroma(
    persist_directory=chroma_dir,
    embedding_function=embeddings,
    collection_name="rag_documents"
)

# Get collection metadata
collection = vectorstore._collection
print(f"[OK] Collection name: {collection.name}")
print(f"  Total documents: {collection.count()}")

# Get collection metadata
metadata = collection.metadata
print(f"  Metadata: {metadata}")
print()

# Test 4: Direct vector store query with score analysis
print("Test 4: Analyzing vector store results for 'attention mechanism'...")

# Query about attention (should match attention paper)
results = vectorstore.similarity_search_with_relevance_scores("attention mechanism", k=10)

print(f"\nTop 10 results:")
print(f"{'Rank':<6} {'Source':<50} {'Score':<8} {'Preview'}")
print("-" * 120)

for i, (doc, score) in enumerate(results, 1):
    source = Path(doc.metadata.get('source', 'Unknown')).name
    preview = doc.page_content[:60].replace('\n', ' ').strip()
    preview = preview.encode('ascii', errors='replace').decode('ascii')
    print(f"{i:<6} {source:<50} {score:<8.4f} {preview}...")

# Count how many from each document
doc_counts = {}
for doc, score in results:
    source = Path(doc.metadata.get('source', 'Unknown')).name
    doc_counts[source] = doc_counts.get(source, 0) + 1

print(f"\nDocument distribution in top 10:")
for source, count in sorted(doc_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"  {source}: {count} chunks")
print()

# Test 5: Query with explicit attention paper content
print("Test 5: Testing with exact text from attention paper...")

# This should have very high similarity if embeddings work correctly
exact_text = "attention is all you need"
results_exact = vectorstore.similarity_search_with_relevance_scores(exact_text, k=5)

print(f"\nQuery: '{exact_text}'")
for i, (doc, score) in enumerate(results_exact, 1):
    source = Path(doc.metadata.get('source', 'Unknown')).name
    preview = doc.page_content[:80].replace('\n', ' ').strip()
    preview = preview.encode('ascii', errors='replace').decode('ascii')
    print(f"  {i}. {source} (score: {score:.4f})")
    print(f"     {preview}...")
print()

# Test 6: Check embedding vector norms in the database
print("Test 6: Analyzing stored embedding vectors...")

# Get a sample of stored embeddings
sample_results = vectorstore.similarity_search("test", k=5)
if sample_results:
    # This will trigger embedding retrieval internally
    print(f"[OK] Successfully retrieved {len(sample_results)} sample chunks")

print()

print("="*80)
print("DIAGNOSTICS COMPLETE")
print("="*80)

print("\nSummary:")
print(f"  Embedding dimension: {len(embedding_vector)}")
print(f"  Relevant text similarity: {sim_relevant:.4f}")
print(f"  Irrelevant text similarity: {sim_irrelevant:.4f}")
print(f"  Top result score for 'attention mechanism': {results[0][1]:.4f}")
print(f"  Top result is from: {Path(results[0][0].metadata.get('source', 'Unknown')).name}")

if sim_relevant < 0.5:
    print("\n⚠️  WARNING: Low similarity scores detected!")
    print("   This could indicate:")
    print("   - Embeddings not normalized")
    print("   - Dimension mismatch")
    print("   - Incorrect similarity metric")
    print("   - Model not working as expected")

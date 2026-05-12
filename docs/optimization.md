# Performance Optimization Guide

## Overview

This document describes the performance optimizations applied to the PDF QA application to improve speed, memory usage, and overall efficiency.

## Key Optimizations

### 1. Embedding Model Optimization

The `SimpleSklearnEmbeddings` class has been optimized for better memory usage and performance:

- **Sparse Matrix Usage**: Using sparse matrices instead of dense arrays reduces memory footprint dramatically
- **Vocabulary Control**: Parameters `max_features`, `min_df`, and `max_df` limit vocabulary size and filter out rare/common terms
- **Sublinear TF Scaling**: Using `sublinear_tf=True` improves relevance by applying logarithmic scaling to term frequencies

### 2. Vector Store Enhancements

FAISS vector store operations have been optimized:

- **Better Chunking**: Using `RecursiveCharacterTextSplitter` with meaningful separators
- **Richer Metadata**: Adding detailed metadata to chunks for better source attribution
- **Error Recovery**: Implementing fallback methods for handling FAISS initialization errors

### 3. Caching System

Multi-level caching has been implemented:

- **LLM Model Caching**: Reusing LLM instances across requests
- **Query Result Caching**: Storing previous query results for immediate retrieval
- **Bounded Cache Size**: Preventing memory leaks by limiting cache size

### 4. Persistence Improvements

The persistence system has been enhanced:

- **Compression**: Using gzip to reduce disk usage
- **Atomic Writes**: Preventing data corruption during saves
- **Backup System**: Automatic backups with rotation
- **Error Recovery**: Ability to restore from backups

### 5. Performance Monitoring

Added comprehensive monitoring capabilities:

- **Timing Metrics**: Tracking processing time for each operation
- **Memory Tracking**: Optional memory usage monitoring with psutil
- **Detailed Logging**: Better structured logs with relevant metrics

## Configuration Options

### Memory Optimization

To tune memory usage, adjust these parameters in the `SimpleSklearnEmbeddings` class:

```python
embeddings = SimpleSklearnEmbeddings(
    max_features=10000,  # Increase for more vocabulary terms
    min_df=2,            # Ignore terms appearing in fewer documents
    max_df=0.85          # Ignore terms appearing in too many documents
)
```

### Retrieval Tuning

Adjust these parameters in `initialize_qa_chain()` to balance between speed and quality:

```python
retriever = vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 5,       # Number of chunks to retrieve
        "fetch_k": 10  # Initial candidates before filtering
    }
)
```

### Caching Configuration

Modify `MAX_CACHE_SIZE` to control memory usage for query caching.

## Memory Usage Analysis

Key components by memory usage:

1. **Vector Store**: Typically the largest memory consumer
   - Scales with document size and embedding dimension
   - For large documents, consider using smaller chunk sizes

2. **TF-IDF Vectorizer**: Second largest memory consumer
   - Memory usage scales with vocabulary size
   - Using sparse matrices significantly reduces memory needs

3. **LLM Models**: Memory usage depends on model size
   - Smaller models like "phi3:mini" use less memory than "mistral"

## Future Optimization Opportunities

1. **Database Backend**: Replace in-memory FAISS with PostgreSQL + pgvector
2. **Streaming Responses**: Implement streaming for faster time-to-first-token
3. **Worker Pool**: Implement multi-processing for parallel document processing
4. **Quantization**: Apply quantization to embeddings to reduce memory usage
5. **Batch Processing**: Implement batching for large document sets

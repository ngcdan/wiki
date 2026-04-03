# RAG Lab — Roadmap

## Module 1: Embeddings fundamentals

- [ ] Lý thuyết: Text → vector, không gian vector, cosine similarity, các embedding model
- [ ] Thực hành: Gọi OpenAI embedding API, tính similarity giữa các câu
- [ ] Output: `scripts/01_similarity_demo.py` + `src/embedder.py`
- [ ] Dependencies: `openai`, `python-dotenv`

## Module 2: Vector Store

- [ ] Lý thuyết: Vector database là gì, indexing (HNSW, IVF), ChromaDB architecture, persistent vs in-memory
- [ ] Thực hành: ChromaDB setup (persistent to disk), CRUD operations, similarity search
- [ ] Output: `scripts/02_vector_crud.py` + `src/vector_store.py`
- [ ] Dependencies: `chromadb`

## Module 3: Document loading & chunking

- [ ] Lý thuyết: Tại sao cần chunking, các chiến lược (fixed-size, recursive, semantic), overlap
- [ ] Thực hành: Đọc file MD/PDF/TXT, implement nhiều chunking strategies, so sánh
- [ ] Output: `src/loader.py` + `src/chunker.py`
- [ ] Dependencies: `pypdf`

## Module 4: Retrieval pipeline

- [ ] Lý thuyết: Retrieval pipeline end-to-end, retrieval metrics (precision, recall, MRR)
- [ ] Thực hành: Kết nối loader → chunker → embedder → vector store → search
- [ ] Output: `src/retriever.py`

## Module 5: Generation (RAG hoàn chỉnh)

- [ ] Lý thuyết: Prompt engineering cho RAG, context window management, hallucination
- [ ] Thực hành: Thêm LLM (Claude/OpenAI) để sinh câu trả lời từ retrieved chunks
- [ ] Output: `src/generator.py` + `src/rag.py` + `cli.py`
- [ ] Dependencies: `anthropic`, `click`

## Module 6: Evaluation & improvement

- [ ] Lý thuyết: RAG evaluation (relevance, faithfulness, answer correctness)
- [ ] Thực hành: Tạo eval dataset, đo retrieval quality, answer quality
- [ ] Output: `scripts/06_eval.py` + eval dataset
- [ ] Stretch goals: reranking, hybrid search

## Module 7: Local models

- [ ] Lý thuyết: Open-source models, Ollama, quantization
- [ ] Thực hành: Chuyển embedding + LLM sang Ollama, benchmark vs API
- [ ] Output: Cùng app chạy offline
- [ ] Dependencies: `ollama`

## Module 8: Advanced topics

- [ ] Chọn 1-2: Multi-modal RAG, agentic RAG, knowledge graphs, LangChain/LlamaIndex comparison

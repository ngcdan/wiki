# RAG Lab

Dự án học tập & nghiên cứu RAG (Retrieval-Augmented Generation) từ nền tảng.

## Mục tiêu

Hiểu sâu từng thành phần của RAG pipeline bằng cách tự build từ scratch (bottom-up), sau đó mở rộng sang local model và advanced topics.

## Kết quả cuối

RAG CLI app tổng quát — load bất kỳ tập tài liệu nào (PDF, MD, TXT), hỏi đáp bằng ngôn ngữ tự nhiên.

## Cấu trúc

- `notes/` — Ghi chú học tập theo module
- `lab/` — Python project
  - `src/` — Source code các components
  - `tests/` — Unit tests
  - `scripts/` — Demo/experiment scripts cho từng module

## Roadmap tóm tắt

1. Embeddings fundamentals
2. Vector Store (ChromaDB)
3. Document loading & chunking
4. Retrieval pipeline
5. Generation (RAG hoàn chỉnh + CLI)
6. Evaluation & improvement
7. Local models (Ollama)
8. Advanced topics

Chi tiết: xem [roadmap.md](roadmap.md)

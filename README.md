# RAG-Based-Researcher-Research-Analyst
🏙️ **Researcher Research Assistant**

Researchers and analysts often fail not due to lack of time, but because they **cannot read and process all research papers, news articles, and documents efficiently**.  
This AI-powered tool uses **RAG (Retrieval-Augmented Generation)** to make research effortless. Users can **input article URLs or upload documents** and ask questions to instantly retrieve relevant insights. Initially focused on the **real estate domain**, it can be extended to any field.

![product screenshot](resources/image.png)

---

## Features

### 🔹 URL-Based Research
- Load multiple article URLs.
- Extract content using **LangChain's UnstructuredURL Loader**.
- Split text, generate embeddings using **HuggingFace**, and store in **ChromaDB**.
- Ask questions via **Llama3 (Groq)** and receive answers with source URLs.

### 🔹 Document & File Upload Research
- Upload **PDFs, DOCX, TXT, CSV, and images**.
- Automatic text extraction and semantic indexing.
- Ask questions across your **private research repository**.

### 🔹 Smart AI Q&A
- Ask questions in natural language.
- Answers are **relevant, contextual, and include sources** for validation.

---

## Set-Up



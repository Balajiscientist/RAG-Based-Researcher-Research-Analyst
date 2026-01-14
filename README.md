# RAG-Based-Researcher-Research-Analyst
🏙️ **Researcher Research Assistant**

Researchers and analysts often fail not due to lack of skill, but because they **cannot read and process all research papers, news articles, and documents efficiently**.  
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

### 1. Install Dependencies

2. Create a .env file with your GROQ credentials as follows:
text
    GROQ_MODEL=MODEL_NAME_HERE
    GROQ_API_KEY=GROQ_API_KEY_HERE
3. Run the streamlit app by running the following command.
bash
    streamlit run main.py
### Usage/Examples The web app will open in your browser after the set-up is complete. - On the sidebar, you can input URLs directly. - Initiate the data loading and processing by clicking "Process URLs." - Observe the system as it performs text splitting, generates embedding vectors using HuggingFace's Embedding Model. - The embeddings will be stored in ChromaDB.
```bash
pip install -r requirements.txt


import os
from uuid import uuid4
from dotenv import load_dotenv
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_loaders import (
    UnstructuredURLLoader,
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredFileLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
import tempfile

load_dotenv()

# Constants
CHUNK_SIZE = 1000
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTORSTORE_DIR = Path(__file__).parent / "resources/vectorstore"
COLLECTION_NAME = "real_estate"

llm = None
vector_store = None


def initialize_components():
    global llm, vector_store

    if llm is None:
        llm = ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            temperature=0.9,
            max_tokens=500,
        )

    if vector_store is None:
        ef = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"trust_remote_code": True}
        )

        vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=ef,
            persist_directory=str(VECTORSTORE_DIR)
        )


def process_urls(urls):
    """
    This function scraps data from a url and stores it in a vector db
    :param urls: input urls
    :return:
    """
    yield "Initializing Components"
    initialize_components()

    yield "Resetting vector store...✅"
    vector_store.reset_collection()

    yield "Loading data...✅"
    loader = UnstructuredURLLoader(urls=urls)
    data = loader.load()

    yield "Splitting text into chunks...✅"
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=CHUNK_SIZE
    )
    docs = text_splitter.split_documents(data)

    yield "Add chunks to vector database...✅"
    uuids = [str(uuid4()) for _ in range(len(docs))]
    vector_store.add_documents(docs, ids=uuids)

    yield "Done adding docs to vector database...✅"


def process_documents(uploaded_files):
    """
    This function processes uploaded documents (PDF, DOCX, TXT, etc.) and stores them in a vector db
    :param uploaded_files: list of uploaded file objects from Streamlit
    :return: generator yielding status messages
    """
    yield "Initializing Components"
    initialize_components()

    yield "Resetting vector store...✅"
    vector_store.reset_collection()

    all_docs = []
    tmp_paths = []  # Keep track of temp files to clean up later
    
    # Process each uploaded file
    for uploaded_file in uploaded_files:
        file_extension = Path(uploaded_file.name).suffix.lower()
        
        # Save uploaded file temporarily
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension, mode='wb') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
                tmp_paths.append(tmp_path)
            
            yield f"Loading {uploaded_file.name}..."
            
            # Load document based on file type
            if file_extension == '.pdf':
                loader = PyPDFLoader(tmp_path)
            elif file_extension in ['.docx', '.doc']:
                loader = Docx2txtLoader(tmp_path)
            elif file_extension == '.txt':
                loader = TextLoader(tmp_path, encoding='utf-8')
            else:
                # Try unstructured loader for other file types (images, etc.)
                loader = UnstructuredFileLoader(tmp_path)
            
            docs = loader.load()
            if docs:
                all_docs.extend(docs)
                yield f"✅ Loaded {uploaded_file.name} ({len(docs)} pages/chunks)"
            else:
                yield f"⚠️ Warning: {uploaded_file.name} loaded but contains no content"
            
        except Exception as e:
            error_msg = f"❌ Error loading {uploaded_file.name}: {str(e)}"
            yield error_msg
            import traceback
            print(f"Full error for {uploaded_file.name}:")
            print(traceback.format_exc())
    
    # Clean up temporary files
    for tmp_path in tmp_paths:
        try:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        except Exception as e:
            print(f"Warning: Could not delete temp file {tmp_path}: {e}")
    
    if not all_docs:
        yield "❌ No documents were successfully loaded. Please check file formats and try again."
        return
    
    yield f"Splitting {len(all_docs)} document(s) into chunks...✅"
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=200
    )
    split_docs = text_splitter.split_documents(all_docs)
    yield f"Created {len(split_docs)} chunks from documents"

    yield "Adding chunks to vector database...✅"
    uuids = [str(uuid4()) for _ in range(len(split_docs))]
    vector_store.add_documents(split_docs, ids=uuids)

    yield f"✅ Done! Added {len(split_docs)} chunks to vector database. You can now ask questions."


def generate_answer(query):
    if vector_store is None:
        initialize_components()
    
    if vector_store is None:
        raise RuntimeError("Vector database is not initialized. Please process URLs or documents first.")

    # Build prompt up front so it can be reused
    prompt = ChatPromptTemplate.from_template(
        """
        You are a helpful research assistant.
        Answer the question using only the provided context.
        If the answer is not contained in the context, reply:
        "I don't have enough information to answer this question."

        Context:
        {context}

        Question: {question}

        Answer (concise):
        """
    )

    # Retrieve relevant docs
    retriever = vector_store.as_retriever()
    docs = retriever.invoke(query)

    # Combine doc texts for the prompt
    context_text = "\n\n".join(getattr(doc, "page_content", "") for doc in docs)

    # Run the chat model
    messages = prompt.format_messages(context=context_text, question=query)
    response = llm.invoke(messages)
    answer = getattr(response, "content", "") if response is not None else ""

    # Extract sources from doc metadata
    source_urls = set()
    for doc in docs:
        metadata = getattr(doc, "metadata", {}) if not isinstance(doc, dict) else doc.get("metadata", {})
        if metadata and "source" in metadata:
            source_urls.add(metadata["source"])
    sources = "\n".join(sorted(source_urls)) if source_urls else ""

    return answer, sources


if __name__ == "__main__":
    urls = [
        "https://www.cnbc.com/2024/12/21/how-the-federal-reserves-rate-policy-affects-mortgages.html",
        "https://www.cnbc.com/2024/12/20/why-mortgage-rates-jumped-despite-fed-interest-rate-cut.html"
    ]

    process_urls(urls)
    answer, sources = generate_answer("Tell me what was the 30 year fixed mortagate rate along with the date?")
    print(f"Answer: {answer}")
    print(f"Sources: {sources}")
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
import tempfile
import os
from pathlib import Path
from rag import process_urls, process_documents, generate_answer

app = FastAPI(
    title="RAG Research Assistant API",
    description="API for processing URLs/documents and querying with RAG",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class URLRequest(BaseModel):
    urls: List[str]


class QueryRequest(BaseModel):
    query: str


class URLResponse(BaseModel):
    success: bool
    message: str
    status_messages: List[str]


class QueryResponse(BaseModel):
    answer: str
    sources: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


# Helper class to mimic Streamlit's UploadedFile interface
class FileWrapper:
    def __init__(self, file: UploadFile, content: bytes):
        self.name = file.filename
        self._content = content
    
    def getvalue(self) -> bytes:
        """Synchronous method to get file content (mimics Streamlit's UploadedFile)"""
        return self._content


@app.get("/")
async def root():
    return {
        "message": "RAG Research Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "process_urls": "/api/process-urls",
            "process_documents": "/api/process-documents",
            "query": "/api/query",
            "docs": "/docs"
        }
    }


@app.post("/api/process-urls", response_model=URLResponse)
async def process_urls_endpoint(request: URLRequest):
    """
    Process URLs and store them in the vector database.
    
    - **urls**: List of URLs to process (at least one required)
    """
    if not request.urls or len(request.urls) == 0:
        raise HTTPException(status_code=400, detail="At least one URL is required")
    
    try:
        status_messages = []
        for status in process_urls(request.urls):
            status_messages.append(status)
        
        return URLResponse(
            success=True,
            message="URLs processed successfully",
            status_messages=status_messages
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing URLs: {str(e)}")


@app.post("/api/process-documents", response_model=URLResponse)
async def process_documents_endpoint(files: List[UploadFile] = File(...)):
    """
    Process uploaded documents and store them in the vector database.
    
    Supported formats: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG
    
    - **files**: List of files to upload (multipart/form-data)
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="At least one file is required")
    
    try:
        # Convert FastAPI UploadFile to FileWrapper (mimics Streamlit's UploadedFile)
        file_wrappers = []
        for file in files:
            content = await file.read()
            wrapper = FileWrapper(file, content)
            file_wrappers.append(wrapper)
        
        status_messages = []
        for status in process_documents(file_wrappers):
            status_messages.append(status)
        
        # Check if processing was successful
        success = any("Done!" in msg or "chunks to vector database" in msg for msg in status_messages)
        error_occurred = any("❌" in msg or "Error" in msg or "failed" in msg.lower() for msg in status_messages)
        
        if success and not error_occurred:
            return URLResponse(
                success=True,
                message="Documents processed successfully",
                status_messages=status_messages
            )
        else:
            error_msg = "Document processing failed. Check status_messages for details."
            return URLResponse(
                success=False,
                message=error_msg,
                status_messages=status_messages
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing documents: {str(e)}")


@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Query the vector database and get an answer with sources.
    
    - **query**: The question to ask
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        answer, sources = generate_answer(request.query)
        return QueryResponse(
            answer=answer,
            sources=sources
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=400,
            detail="Vector database is not initialized. Please process URLs or documents first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

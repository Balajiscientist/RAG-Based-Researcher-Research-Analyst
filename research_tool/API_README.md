# RAG Research Assistant API Documentation

This API provides endpoints for processing URLs/documents and querying with RAG (Retrieval-Augmented Generation).

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Running the API

```bash
# Using uvicorn directly
uvicorn api:app --reload --port 8000

# Or run the file directly
python api.py
```

The API will be available at `http://localhost:8000`

### Interactive API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### 1. Process URLs

**Endpoint**: `POST /api/process-urls`

**Description**: Process URLs and store them in the vector database.

**Request Body**:
```json
{
  "urls": [
    "https://example.com/article1",
    "https://example.com/article2"
  ]
}
```

**Response**:
```json
{
  "success": true,
  "message": "URLs processed successfully",
  "status_messages": [
    "Initializing Components",
    "Resetting vector store...✅",
    "Loading data...✅",
    ...
  ]
}
```

**Example (cURL)**:
```bash
curl -X POST "http://localhost:8000/api/process-urls" \
  -H "Content-Type: application/json" \
  -d '{"urls": ["https://www.cnbc.com/2024/12/21/how-the-federal-reserves-rate-policy-affects-mortgages.html"]}'
```

**Example (Python)**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/process-urls",
    json={
        "urls": [
            "https://www.cnbc.com/2024/12/21/how-the-federal-reserves-rate-policy-affects-mortgages.html"
        ]
    }
)
print(response.json())
```

---

### 2. Process Documents

**Endpoint**: `POST /api/process-documents`

**Description**: Process uploaded documents (PDF, DOCX, DOC, TXT, PNG, JPG, JPEG) and store them in the vector database.

**Request**: `multipart/form-data` with files

**Response**:
```json
{
  "success": true,
  "message": "Documents processed successfully",
  "status_messages": [
    "Initializing Components",
    "Resetting vector store...✅",
    "Loading document.pdf...",
    "✅ Loaded document.pdf (5 pages/chunks)",
    ...
  ]
}
```

**Example (cURL)**:
```bash
curl -X POST "http://localhost:8000/api/process-documents" \
  -F "files=@document1.pdf" \
  -F "files=@document2.docx"
```

**Example (Python)**:
```python
import requests

files = [
    ('files', ('document.pdf', open('document.pdf', 'rb'), 'application/pdf')),
    ('files', ('document.docx', open('document.docx', 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
]

response = requests.post(
    "http://localhost:8000/api/process-documents",
    files=files
)
print(response.json())
```

**Example (JavaScript/Fetch)**:
```javascript
const formData = new FormData();
formData.append('files', fileInput.files[0]);
formData.append('files', fileInput.files[1]);

const response = await fetch('http://localhost:8000/api/process-documents', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data);
```

---

### 3. Query

**Endpoint**: `POST /api/query`

**Description**: Query the vector database and get an answer with sources.

**Request Body**:
```json
{
  "query": "What was the 30 year fixed mortgage rate?"
}
```

**Response**:
```json
{
  "answer": "Based on the provided context...",
  "sources": "https://example.com/article1\nhttps://example.com/article2"
}
```

**Example (cURL)**:
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What was the 30 year fixed mortgage rate?"}'
```

**Example (Python)**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/query",
    json={"query": "What was the 30 year fixed mortgage rate?"}
)

data = response.json()
print(f"Answer: {data['answer']}")
print(f"Sources: {data['sources']}")
```

**Example (JavaScript/Fetch)**:
```javascript
const response = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'What was the 30 year fixed mortgage rate?'
  })
});

const data = await response.json();
console.log('Answer:', data.answer);
console.log('Sources:', data.sources);
```

---

### 4. Health Check

**Endpoint**: `GET /health`

**Description**: Check if the API is running.

**Response**:
```json
{
  "status": "healthy"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message here"
}
```

**Common Status Codes**:
- `400`: Bad Request (missing parameters, invalid input)
- `500`: Internal Server Error (processing errors)

---

## Workflow

1. **Process URLs or Documents**: First, call `/api/process-urls` or `/api/process-documents` to load data into the vector database.

2. **Query**: Then, call `/api/query` to ask questions about the processed content.

**Note**: You must process URLs or documents before querying. The vector database is reset each time you process new URLs or documents.

---

## CORS

CORS is enabled for all origins by default. In production, you should configure the `allow_origins` in `api.py` to specify your frontend domain.

---

## Environment Variables

Make sure you have a `.env` file with:

```env
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_API_KEY=your_api_key_here
```

---

## Frontend Integration Examples

### React Example

```jsx
// Process URLs
const processURLs = async (urls) => {
  const response = await fetch('http://localhost:8000/api/process-urls', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ urls })
  });
  return await response.json();
};

// Process Documents
const processDocuments = async (files) => {
  const formData = new FormData();
  files.forEach(file => formData.append('files', file));
  
  const response = await fetch('http://localhost:8000/api/process-documents', {
    method: 'POST',
    body: formData
  });
  return await response.json();
};

// Query
const query = async (question) => {
  const response = await fetch('http://localhost:8000/api/query', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: question })
  });
  return await response.json();
};
```

### Vue.js Example

```javascript
// In your Vue component
export default {
  methods: {
    async processURLs(urls) {
      const response = await this.$http.post('/api/process-urls', { urls });
      return response.data;
    },
    
    async processDocuments(files) {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      
      const response = await this.$http.post('/api/process-documents', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data;
    },
    
    async query(question) {
      const response = await this.$http.post('/api/query', { query: question });
      return response.data;
    }
  }
}
```

---

## Notes

- The vector database persists between API calls (stored in `resources/vectorstore/`)
- Processing new URLs or documents will reset the vector database
- Supported file formats: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG
- The API uses the same RAG backend as the Streamlit app

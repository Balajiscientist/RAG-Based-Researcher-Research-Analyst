"""
Example script showing how to use the RAG Research Assistant API
"""
import requests
import json

BASE_URL = "http://localhost:8000"


def process_urls_example():
    """Example: Process URLs"""
    print("=" * 50)
    print("Example 1: Processing URLs")
    print("=" * 50)
    
    urls = [
        "https://www.cnbc.com/2024/12/21/how-the-federal-reserves-rate-policy-affects-mortgages.html",
        "https://www.cnbc.com/2024/12/20/why-mortgage-rates-jumped-despite-fed-interest-rate-cut.html"
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/process-urls",
        json={"urls": urls}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success: {data['success']}")
        print(f"Message: {data['message']}")
        print("\nStatus Messages:")
        for msg in data['status_messages']:
            print(f"  - {msg}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())


def process_documents_example():
    """Example: Process documents"""
    print("\n" + "=" * 50)
    print("Example 2: Processing Documents")
    print("=" * 50)
    
    # Note: Replace with actual file paths
    files = [
        ('files', ('document.pdf', open('document.pdf', 'rb'), 'application/pdf'))
    ]
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/process-documents",
            files=files
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data['success']}")
            print(f"Message: {data['message']}")
            print("\nStatus Messages:")
            for msg in data['status_messages']:
                print(f"  - {msg}")
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
    except FileNotFoundError:
        print("Note: document.pdf not found. Skipping document processing example.")
    finally:
        # Close file if opened
        if 'files' in locals():
            for _, file_tuple in files:
                if hasattr(file_tuple[1], 'close'):
                    file_tuple[1].close()


def query_example():
    """Example: Query the RAG system"""
    print("\n" + "=" * 50)
    print("Example 3: Querying")
    print("=" * 50)
    
    query = "What was the 30 year fixed mortgage rate?"
    
    response = requests.post(
        f"{BASE_URL}/api/query",
        json={"query": query}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Query: {query}")
        print(f"\nAnswer:\n{data['answer']}")
        if data['sources']:
            print(f"\nSources:\n{data['sources']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())


def health_check_example():
    """Example: Health check"""
    print("\n" + "=" * 50)
    print("Example 4: Health Check")
    print("=" * 50)
    
    response = requests.get(f"{BASE_URL}/health")
    
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Error: {response.status_code}")


if __name__ == "__main__":
    print("RAG Research Assistant API Examples")
    print("Make sure the API is running at http://localhost:8000\n")
    
    # Health check first
    try:
        health_check_example()
        
        # Process URLs
        process_urls_example()
        
        # Query
        query_example()
        
        # Process documents (commented out - requires actual files)
        # process_documents_example()
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the API.")
        print("Make sure the API is running:")
        print("  uvicorn api:app --reload --port 8000")
    except Exception as e:
        print(f"\nError: {e}")

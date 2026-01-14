import streamlit as st
from rag import process_urls, process_documents, generate_answer

st.title("Researcher Research Assistant")

# Initialize session state
if 'docs_processed' not in st.session_state:
    st.session_state.docs_processed = False
if 'urls_processed' not in st.session_state:
    st.session_state.urls_processed = False

# Create tabs
tab1, tab2 = st.tabs(["Tab 1", "Tab 2"])

# Tab 1: URL Processing
with tab1:
    st.header("Links - Click Here")
    
    url1 = st.text_input("URL 1", key="url1")
    url2 = st.text_input("URL 2", key="url2")
    url3 = st.text_input("URL 3", key="url3")
    
    placeholder1 = st.empty()
    
    process_url_button = st.button("Process URLs", key="process_urls")
    if process_url_button:
        urls = [url for url in (url1, url2, url3) if url != '']
        if len(urls) == 0:
            placeholder1.error("You must provide at least one valid URL")
        else:
            for status in process_urls(urls):
                placeholder1.text(status)
            placeholder1.success("URLs processed successfully!")
            st.session_state.urls_processed = True
            st.session_state.docs_processed = False  # Reset docs flag
    
    st.divider()
    
    query1 = st.text_input("Ask questions to your Topic", placeholder="Type here", key="query1")
    if query1:
        try:
            answer, sources = generate_answer(query1)
            st.header("Answer:")
            st.write(answer)
            
            if sources:
                st.subheader("Source Links:")
                for source in sources.split("\n"):
                    if source.strip():
                        st.write(f"• {source}")
        except RuntimeError as e:
            st.error("You must process URLs first")

# Tab 2: Document Upload
with tab2:
    st.header("Upload your PDFs (or) DOC, etc")
    
    uploaded_files = st.file_uploader(
        "Choose files",
        type=['pdf', 'docx', 'doc', 'txt', 'png', 'jpg', 'jpeg'],
        accept_multiple_files=True,
        key="file_uploader"
    )
    
    placeholder2 = st.empty()
    
    if uploaded_files:
        st.write(f"**{len(uploaded_files)} file(s) uploaded:**")
        for file in uploaded_files:
            st.write(f"• {file.name}")
    
    process_docs_button = st.button("Process Documents", key="process_docs")
    if process_docs_button:
        if not uploaded_files:
            placeholder2.error("Please upload at least one document")
        else:
            status_messages = []
            status_container = placeholder2.container()
            success = False
            error_occurred = False
            
            for status in process_documents(uploaded_files):
                status_messages.append(status)
                status_container.text(status)
                if "Done!" in status or "chunks to vector database" in status:
                    success = True
                if "❌" in status or "Error" in status or "failed" in status.lower():
                    error_occurred = True
            
            # Display final status
            if success and not error_occurred:
                placeholder2.success("✅ Documents processed successfully! You can now ask questions.")
                st.session_state.docs_processed = True
                st.session_state.urls_processed = False  # Reset URLs flag
            else:
                # Show all error messages
                error_text = "\n".join([msg for msg in status_messages if "❌" in msg or "Error" in msg or "failed" in msg.lower() or "No documents" in msg])
                if error_text:
                    placeholder2.error(f"❌ Processing failed:\n\n{error_text}")
                else:
                    placeholder2.error("❌ Document processing failed. Please check the status messages above.")
    
    st.divider()
    
    query2 = st.text_input("Type Question", placeholder="Type Question", key="query2")
    if query2:
        try:
            with st.spinner("Searching documents and generating answer..."):
                answer, sources = generate_answer(query2)
            st.header("Answer:")
            st.write(answer)
            
            if sources:
                st.subheader("Source Links:")
                for source in sources.split("\n"):
                    if source.strip():
                        st.write(f"• {source}")
        except RuntimeError as e:
            if not st.session_state.docs_processed:
                st.error("You must process documents first. Please upload and process documents before asking questions.")
            else:
                st.error(f"Error: {str(e)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

'''
=== DOC STRING ===

App for handling both PDF uploads and chat queries related to the PDF content. Here's a summary of what you already have and how it fits with the updated HTML page:

Existing Routes
/ Route (Home Page): Method: GET, POST
Purpose: Handles file uploads. Saves the PDF file, processes it, splits it into chunks, and stores them in a Chroma vector store.

/ai Route: Method: POST
Purpose: This seems to be set up to handle general queries using the cached_llm, but it is not used in the updated HTML. It might be a legacy route or used for other purposes.

/ask_pdf Route: Method: POST
Purpose: Handles queries about the uploaded PDF. It loads the vector store, creates a retrieval chain, and returns the response based on the query.
'''

from flask import Flask, request, render_template, jsonify, session
from langchain_community.llms import Ollama
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import PDFPlumberLoader
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain.prompts import ChatPromptTemplate
import os
import uuid
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Ensure that the secret key is set correctly
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# A dictionary to hold vector stores for each session
vector_stores = {}

# Initialize embedding and other components
cached_llm = Ollama(model="llama3.1")
embedding = FastEmbedEmbeddings()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    length_function=len,
    is_separator_regex=False
)

system_prompt = (
    "Use the given context to directly answer the question. "
    "If you don't know the answer, say you don't know. "
    "Use three sentences maximum and keep the answer concise. "
    "Context: {context}"
    "Don't reply with 'in this part of the text..' or 'based on this passage...', just give reply trying to be exhaustive about answering the question"
    "Also avoid short replies, always enrich the reply"
)

@app.route("/", methods=["GET", "POST"])
def home():
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())  # Generate a unique session ID

    user_id = session['user_id']
    
    if request.method == "POST":
        file = request.files.get("file")
        if file:
            file_name = file.filename
            save_file = os.path.join("pdf", file_name)
            file.save(save_file)
            
            # Process the PDF
            try:
                loader = PDFPlumberLoader(save_file)
                docs = loader.load_and_split()
                chunks = text_splitter.split_documents(docs)
                
                # Initialize a new vector store for this session
                vector_store = Chroma.from_documents(
                    documents=chunks, embedding=embedding
                )
                
                # Store this vector store in the global dictionary using user_id as the key
                vector_stores[user_id] = vector_store

                return render_template(
                    "upload.html",
                    status="Successfully Uploaded",
                    filename=file_name,
                    doc_len=len(docs),
                    chunks=len(chunks)
                )
            except Exception as e:
                return render_template("upload.html", status=f"Error processing PDF: {str(e)}"), 500

        return render_template("upload.html", status="No file provided"), 400

    return render_template("upload.html")

@app.route("/ask_pdf", methods=["POST"])
def askPDFPost():
    user_id = session.get('user_id')

    if not user_id or user_id not in vector_stores:
        return jsonify({"error": "No vector store found. Please upload a PDF first."}), 400

    vector_store = vector_stores[user_id]  # Retrieve the vector store for this session
    json_content = request.json
    query = json_content.get("query")

    try:
        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={"k": 10, "score_threshold": 0.3},
        )

        # Create prompt and chain
        prompt = ChatPromptTemplate.from_messages(
            [("system", system_prompt), ("human", "{input}")]
        )
        question_answer_chain = create_stuff_documents_chain(llm=cached_llm, prompt=prompt)
        chain = create_retrieval_chain(retriever=retriever, combine_docs_chain=question_answer_chain)

        # Get the result
        result = chain.invoke({"input": query})

        print(result)

        # Process sources
        sources = []
        if 'context' in result:
            seen_sources = set()
            for doc in result["context"]:
                source_info = {"source": doc.metadata.get("source", "unknown"), "page_content": doc.page_content[:500]}  # Truncate content for brevity
                if source_info["source"] not in seen_sources:
                    sources.append(source_info)
                    seen_sources.add(source_info["source"])

        return jsonify({"answer": result.get("answer", "No answer found"), "sources": sources})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/reset", methods=["POST"])
def reset_session():
    session.clear()
    return jsonify({"message": "Session reset successfully"})

def start_app():
    app.run(host="0.0.0.0", port=8080, debug=True)

if __name__ == "__main__":
    start_app()
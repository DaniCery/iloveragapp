# PDF Chatbot App

A web application built with Flask for uploading PDF files and interacting with them through a chat interface. Users can upload a PDF, which is processed and stored. Once uploaded, users can query the content of the PDF, and the system will provide relevant answers based on the content.


<img width="743" alt="Schermata 2024-08-18 alle 18 32 30" src="https://github.com/user-attachments/assets/36656aef-03cd-4dd4-a088-90fe3c9e23a0">


<img width="637" alt="Schermata 2024-08-18 alle 18 33 06" src="https://github.com/user-attachments/assets/c69adf1e-5736-4096-911a-1548b9b60839">


## Features

#### Document Processing and Vector Store

The app allows users to upload PDF documents. It processes these PDFs by splitting the text into chunks and then creates a vector store using Chroma with embeddings provided by FastEmbedEmbeddings. This vector store holds the document representations that can be used for retrieval.

#### Retrieval Mechanism

When a user submits a query, the app uses the vector store to retrieve relevant chunks of text based on similarity to the query. This is done with the help of the retriever from the vector store.

#### Generation of Responses

The `create_stuff_documents_chain` function creates a chain that uses the retrieved documents along with a language model (LLM) to generate a response. This LLM is `cached_llm` in your code, which is an instance of Ollama.

#### Combining Retrieval and Generation

The RAG approach typically combines retrieval (fetching relevant information from a knowledge base) with generation (creating a coherent answer). Your application combines these elements by first retrieving relevant chunks from the vector store and then using the LLM to generate a concise answer based on those chunks.

#### Session Management

The app manages user sessions with unique IDs, storing vector stores per session to handle multiple users independently.

#### Interaction Flow

The interaction flow involves uploading a PDF, which gets indexed and stored. Users can then ask questions related to the content of the uploaded PDF, and the app retrieves and generates answers based on the document's content.


## Process

1. **Upload PDF:**
   - **Action**: Use the file upload form on the home page to select and submit a PDF file.
   - **Server Handling**:
     - The `/` route (POST method) handles the file upload.
     - The file is saved on the server, and `PDFPlumberLoader` is used to extract text from the PDF.
     - The extracted text is split into chunks using `RecursiveCharacterTextSplitter`. This step breaks down the text into manageable pieces for easier processing.
     - Chunks are embedded into vectors using `FastEmbedEmbeddings`.
     - These vectors are stored in a `Chroma` vector store. The vector store is a database optimized for storing and retrieving high-dimensional vectors, making it ideal for similarity searches.
     - The vector store is persisted, ensuring that the data is saved and can be accessed in future queries.

2. **Ask General Queries:**
   - **Action**: Submit a general query unrelated to the uploaded PDF.
   - **Server Handling**:
     - The `/ai` route (POST method) receives the query.
     - It uses the `cached_llm` (Ollama model) to generate a response based on the query.
     - The response from the LLM is returned as JSON, containing the answer.

3. **Query the PDF:**
   - **Action**: Submit a query related to the content of the uploaded PDF using the chat interface.
   - **JavaScript Handling**:
     - The chat interface sends a POST request with the query to the `/ask_pdf` endpoint.
   - **Server Handling**:
     - **Loading the Vector Store**: The `/ask_pdf` route loads the `Chroma` vector store from the persisted directory.
     - **Creating the Retriever**: A retriever is created from the vector store using similarity search. This retriever can search the vector store based on a similarity score threshold, which helps in finding relevant chunks of text related to the query.
     - **Constructing the Retrieval Chain**: The `create_retrieval_chain` function is used to combine the retriever with a document chain that uses the `cached_llm` and the `raw_prompt`. This chain processes the query, retrieves relevant documents, and generates a response.
     - **Processing the Query**: The query is processed by the chain, which searches through the vector store, retrieves relevant chunks, and formulates an answer based on these chunks and the prompt template.
     - **Returning Results**: The response includes the generated answer and the details of the relevant documents (sources), including where in the document the information was found.

4. **Display Results:**
   - **JavaScript Handling**:
     - JavaScript handles form submission, sends the query to the server, and updates the HTML with the response.
   - **User Interface**:
     - The results, including the answer and relevant sources, are dynamically displayed on the page. The response includes:
       - **Answer**: The response generated based on the PDF content.
       - **Sources**: Information about where in the document the answer was found, providing context for the response.

### Summary of Key Components

- **Vector Store (`Chroma`)**: A database that stores embedded text vectors. It enables efficient similarity searches to find relevant content based on the query.
- **Retriever**: A component that uses similarity search to find and retrieve relevant text chunks from the vector store.
- **Retrieval Chain**: Combines the retriever with a language model to process queries, retrieve relevant documents, and generate responses.
- **Prompt Template**: Defines how the query and context are formatted for the language model.


## Technologies

- **Flask:** Web framework for building the application.
- **langchain:** For handling language models, document processing, and embeddings.
- **Chroma:** For managing and querying document embeddings.
- **Tailwind CSS:** For styling the web interface.

## Installation

### Prerequisites

Ensure you have Python 3.8 or higher installed.

### Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/pdf-chatbot-app.git
    cd pdf-chatbot-app
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Create necessary directories:**

    ```bash
    mkdir -p pdf db
    ```

## Configuration

The application uses environment variables and configuration settings:

- **`upload_folder`**: Directory for storing uploaded PDF files.
- **`folder_path`**: Directory for persisting the vector store.

Ensure these directories exist or are created automatically by the application.

## Running the Application

To start the Flask application, run:

```bash
python app.py

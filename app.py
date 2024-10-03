from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from weaviate import Client as WeaviateClient
from weaviate.auth import AuthApiKey
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Weaviate
from langchain.prompts import ChatPromptTemplate
from langchain import HuggingFaceHub
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
import os

app = Flask(__name__)
CORS(app)  # Enable CORS to allow cross-origin requests from frontend

# Configuration
WEAVIATE_API_KEY = "Pwo1Z1f5nGu8Dr7WBYuyhJnsoRB9zqia2MvU"
WEAVIATE_CLUSTER = "https://plhuojq8s8shipvo15pisq.c0.europe-west3.gcp.weaviate.cloud"
UPLOAD_FOLDER = 'uploads'  # Folder to store uploaded files
ALLOWED_EXTENSIONS = {'pdf'}  # Allowed file extensions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Weaviate client
client = WeaviateClient(
    WEAVIATE_CLUSTER,
    auth_client_secret=AuthApiKey(WEAVIATE_API_KEY)
)

# Load PDF and prepare the vector store
def initialize_vector_store(pdf_path):
    loader = PyPDFLoader(pdf_path, extract_images=True)
    pages = loader.load()

    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    docs = text_splitter.split_documents(pages)

    # Create embeddings
    embedding_model_name = "sentence-transformers/all-mpnet-base-v2"
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

    # Initialize the vector database
    vector_db = Weaviate.from_documents(docs, embeddings, client=client, by_text=False)
    return vector_db

# Initialize vector store with the PDF file
vector_db = None

# Create a prompt template
template = """You are an assistant for question-answering tasks.
Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know.
Use ten sentences maximum and keep the answer concise.
Question: {question}
Context: {context}
Answer:
"""

prompt = ChatPromptTemplate.from_template(template)

# Load HuggingFace model
huggingfacehub_api_token = "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"  # Replace with your actual token
model = HuggingFaceHub(
    huggingfacehub_api_token=huggingfacehub_api_token,
    repo_id="mistralai/Mistral-7B-Instruct-v0.3",
    model_kwargs={"temperature": 1, "max_length": 180}
)

output_parser = StrOutputParser()
retriever = None

# Define the RAG chain
rag_chain = None

@app.route('/ask', methods=['POST'])
def ask():
    global rag_chain, retriever

    data = request.get_json()
    print("Received data:", data)
    question = data.get('question')

    if not question:
        return jsonify({'error': 'Question is required'}), 400

    if retriever is None:
        return jsonify({'error': 'No vector store initialized. Please upload a PDF file first.'}), 400

    try:
        print("Received question:", question)
        answer = rag_chain.invoke({"context": retriever, "question": question})
        print("Generated answer:", answer)

        return jsonify({'answer': answer})

    except Exception as e:
        print("Error in processing question:", str(e))
        return jsonify({'error': 'An error occurred while processing the question'}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    global vector_db, retriever, rag_chain

    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Only PDF files are allowed.'}), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Initialize vector store with the uploaded PDF file
        vector_db = initialize_vector_store(filepath)
        retriever = vector_db.as_retriever()

        # Define the RAG chain again with the new retriever
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | model
            | output_parser
        )

        return jsonify({'message': 'File uploaded successfully and vector store initialized.'})

    except Exception as e:
        print("Error in processing file upload:", str(e))
        return jsonify({'error': 'An error occurred during file upload'}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    app.run(debug=True)

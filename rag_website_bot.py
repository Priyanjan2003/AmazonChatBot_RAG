import os
from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import PyPDFLoader
from flask import Flask, request, jsonify,send_from_directory
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS



# Set your OpenAI API Key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# 1. Load Website Data
urls = ["https://www.amazon.in"]  
web_loader = WebBaseLoader(urls)
web_docs = web_loader.load()
# pdf_path = "./data/4semresult.pdf"  
# loader = PyPDFLoader(pdf_path)
pdf_loader = PyPDFLoader("./data/Details.pdf")
pdf_docs = pdf_loader.load()
all_docs = web_docs + pdf_docs


# 2. Split Documents
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_docs = splitter.split_documents(all_docs)

# 3. Create Embeddings and Vector Store
embedding = OpenAIEmbeddings()
vectordb = Chroma.from_documents(split_docs, embedding, persist_directory="./web_db") #./pdf_db
vectordb.persist()

faiss_db = FAISS.from_documents(all_docs, embedding)
faiss_db.save_local("db")

# 4. Create Retriever and QA Chain
retriever = vectordb.as_retriever(search_kwargs={"k": 3})
llm = ChatOpenAI(temperature=0.2)
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

# 5. Ask Questions in Terminal
# while True:
#     query = input("\nAsk a question (or type 'exit'): ")
#     if query.lower() == "exit":
#         break
#     response = rag_chain(query)
#     print("\nAnswer:", response["result"])

app = Flask(__name__, static_folder="frontend", static_url_path="")

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    query = data.get("question", "")
    if not query:
        return jsonify({"answer": "Please enter a question."})

    #
    try:
        result = rag_chain(query)
        return jsonify({"answer": result["result"]})
    except Exception as e:
        print("❌ RAG Error:", e)
        return jsonify({"answer": "Error occurred while generating response."})

if __name__ == "__main__":
    print("🚀  Starting Flask app on http://127.0.0.1:5000 …")
    app.run(debug=True)
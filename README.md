# 🚀 Chatbot RAG with NeMo Guardrails  

This project is a **Retrieval-Augmented Generation (RAG) chatbot** that uses **LangChain, OpenAI, ChromaDB, and NeMo Guardrails** to answer questions based on predefined documents. It ensures the chatbot does **not** answer questions outside the given knowledge base.

---

## 📌 **Features**
✅ **Retrieves answers from documents (`.md` files)**  
✅ **Uses NeMo Guardrails to restrict responses**  
✅ **Embeds and indexes documents using ChromaDB**  
✅ **Uses OpenAI LLM for response generation**  
✅ **Prevents answering out-of-context questions**  

---

## 🛠 **Installation & Setup**
Follow these steps to set up and run the chatbot.

### **1️⃣ Clone the Project**
```sh
git clone <your-repo-url>
cd chatbot_ks_v2
```

### **2️⃣ Create a Virtual Environment (`.venv`)**
```sh
python -m venv .venv
```

### **3️⃣ Activate the Virtual Environment**
#### **Windows (CMD / PowerShell)**
```sh
.venv\Scripts\activate
```
#### **Mac/Linux (Terminal)**
```sh
source .venv/bin/activate
```

### **4️⃣ Install Dependencies**
```sh
pip install --upgrade pip
pip install langchain openai chromadb nemoguardrails python-dotenv
```

### **5️⃣ Set Up API Keys**
Create a **`.env`** file in the root directory and add:
```
OPENAI_API_KEY=your_openai_api_key
```

---

## 📂 **Project Structure**
```
chatbot_ks_v2/
│── data/
│   ├── embeddings.py  # Handles document indexing
│── models/
│   ├── generator.py  # Generates responses
│── utils/
│   ├── response_formatter.py  # Formats bot responses
│── chatbot/
│   ├── main.py  # Main chatbot script
│── content_files/
│   ├── order.md
│   ├── customer.md
│   ├── product.md
│   ├── default.md
│── nemo_guardrails/
│   ├── colang_rules.co  # Guardrails rules
│── nemo_config.yaml  # Configuration file
│── .env  # API key storage
│── requirements.txt  # List of dependencies
│── README.md  # Project guide
```

---

## 🚀 **Running the Project**
### **1️⃣ Start the Chatbot**
```sh
python chatbot/main.py
```

### **2️⃣ Test Queries**
Try these prompts in the chatbot:
```
User: Where is my order?
Bot: (Response from order.md)

User: What are the product features?
Bot: (Response from product.md)

User: How can I reset my password?
Bot: (Response from customer.md)

User: What is the capital of France?
Bot: "I'm sorry, but I can only answer order, product, or customer-related questions."
```

---

## 📜 **How It Works**
1. **User Input** → The chatbot receives a user question.
2. **NeMo Guardrails Routing** → Determines if the query is related to **order, product, customer, or general**.
3. **Document Retrieval** → Fetches the relevant document (`order.md`, `product.md`, etc.).
4. **Response Generation** → Passes the document content to **OpenAI LLM** to generate a response.
5. **Filtering** → If the query is **out of scope**, the bot **rejects it** instead of answering.

---

## ✅ **Key Features**
✔ **Document-based retrieval** with ChromaDB  
✔ **NeMo Guardrails** to restrict responses  
✔ **FastAPI-ready** structure (can be expanded later)  
✔ **Secure API key handling** using `.env`  

---

## ⚡ **Next Steps**
- ✅ Fine-tune the `.co` file for stricter rules.  
- ✅ Expand `content_files/` with more documents.  
- ✅ Deploy as a web service using **FastAPI**.  

---

## ❓ **Troubleshooting**
### **Error: "Module Not Found"**
Run:
```sh
pip install -r requirements.txt
```

### **Error: "Invalid API Key"**
- Check if **`.env`** has the correct API key.
- Ensure **`.venv`** is activated before running the script.

---

## 📝 **License**
PRIVATE Liscence

---

🚀 **Happy Coding!** 🚀  
```

---

### 📌 What This README Includes
✔ Project Overview  
✔ Step-by-Step Setup (Virtual Environment, API Keys, Dependencies)  
✔ Project Structure Explanation  
✔ How to Run the Project  
✔ How the Chatbot Works  
✔ Troubleshooting Tips  



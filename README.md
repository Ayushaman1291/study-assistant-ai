# 📚 Study Assistant AI

An AI-powered study assistant that lets you upload any PDF document and have an intelligent conversation about it.

🔗 **Live Demo:** [Coming Soon]

---

## ✨ Features

- 📄 **PDF Upload** — Upload any PDF document instantly
- 💬 **Intelligent Q&A** — Ask questions and get accurate answers from the document
- 📋 **Auto Summary** — Generate a structured summary of the document in one click
- 💡 **Suggested Questions** — Get AI-generated study questions based on the document
- ⬇️ **Download Chat** — Export your conversation as a text file
- 🧠 **Context-aware** — Remembers previous questions in the conversation

---

## 🛠️ Tech Stack

- **Python** — Core language
- **Streamlit** — Web application framework
- **Groq API** — LLM inference (Llama 3.3 70B)
- **PyPDF2** — PDF text extraction
- **python-dotenv** — Environment variable management

---

## 🚀 Run Locally

git clone https://github.com/Ayushaman1291/study-assistant-ai.git
cd study-assistant-ai
pip install -r requirements.txt

Create a .env file and add your Groq API key


Then run:
streamlit run app.py

---

## 💡 How It Works

1. Upload any PDF from the sidebar
2. The app extracts all text from the document
3. Your questions + document content are sent to Llama 3.3 70B via Groq
4. The model answers based strictly on the document content
5. Chat history is maintained for follow-up questions

---

## 📁 Project Structure

study-assistant-ai/
├── app.py
├── requirements.txt
├── .gitignore
└── README.md

---

## 👤 Author

**Ayush Aman**
B.Tech — Artificial Intelligence & Data Science
[GitHub](https://github.com/Ayushaman1291)
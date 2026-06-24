import streamlit as st
from groq import Groq
import PyPDF2
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text, len(reader.pages)

def ask_question(context, question, chat_history):
    messages = [
        {
            "role": "system",
            "content": """You are a helpful study assistant. Answer questions based on the document provided. 
If the answer is not in the document, say 'This information is not available in the uploaded document.'
Be clear, concise and helpful."""
        }
    ]
    for msg in chat_history[-4:]:
        messages.append(msg)
    messages.append({
        "role": "user",
        "content": f"Document content:\n{context[:4000]}\n\nQuestion: {question}"
    })
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        max_tokens=1024,
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_summary(context):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful study assistant. Summarize documents clearly and concisely."},
            {"role": "user", "content": f"Please provide a structured summary of this document with: 1) Main topic, 2) Key points (bullet points), 3) Conclusion.\n\nDocument:\n{context[:4000]}"}
        ],
        max_tokens=1024,
        temperature=0.5
    )
    return response.choices[0].message.content

def generate_suggested_questions(context):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful study assistant."},
            {"role": "user", "content": f"Based on this document, generate exactly 4 interesting study questions a student might ask. Return only the questions, one per line, no numbering or bullets.\n\nDocument:\n{context[:3000]}"}
        ],
        max_tokens=300,
        temperature=0.8
    )
    questions = response.choices[0].message.content.strip().split('\n')
    return [q.strip() for q in questions if q.strip()][:4]

def generate_quiz(context, num_questions=5):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a helpful study assistant that creates multiple choice questions."},
            {"role": "user", "content": f"""Based on this document, generate {num_questions} multiple choice questions.

For each question follow this EXACT format:
Q: [question]
A) [option]
B) [option]
C) [option]
D) [option]
Answer: [correct letter]

Document:
{context[:4000]}"""}
        ],
        max_tokens=2000,
        temperature=0.7
    )
    return response.choices[0].message.content

def parse_quiz(quiz_text):
    questions = []
    blocks = quiz_text.strip().split('\n\n')
    for block in blocks:
        lines = [l.strip() for l in block.strip().split('\n') if l.strip()]
        if len(lines) >= 6:
            question = lines[0].replace('Q:', '').strip()
            options = {}
            answer = None
            for line in lines[1:]:
                if line.startswith('A)'):
                    options['A'] = line[2:].strip()
                elif line.startswith('B)'):
                    options['B'] = line[2:].strip()
                elif line.startswith('C)'):
                    options['C'] = line[2:].strip()
                elif line.startswith('D)'):
                    options['D'] = line[2:].strip()
                elif line.startswith('Answer:'):
                    answer = line.replace('Answer:', '').strip()
            if question and len(options) == 4 and answer:
                questions.append({
                    'question': question,
                    'options': options,
                    'answer': answer
                })
    return questions

def format_chat_for_download(messages, pdf_name):
    output = f"Study Assistant — Chat Export\n"
    output += f"Document: {pdf_name}\n"
    output += f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    output += "="*50 + "\n\n"
    for msg in messages:
        role = "You" if msg["role"] == "user" else "Assistant"
        output += f"{role}:\n{msg['content']}\n\n{'-'*30}\n\n"
    return output

# --- UI ---
st.set_page_config(page_title="Study Assistant", page_icon="📚", layout="wide")
st.title("📚 Study Assistant")
st.markdown("Upload any PDF document and ask questions about it.")
st.divider()

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "suggested_questions" not in st.session_state:
    st.session_state.suggested_questions = []
if "quiz_questions" not in st.session_state:
    st.session_state.quiz_questions = []
if "quiz_answers" not in st.session_state:
    st.session_state.quiz_answers = {}
if "quiz_submitted" not in st.session_state:
    st.session_state.quiz_submitted = False

# Sidebar
with st.sidebar:
    st.header("📄 Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file:
        if uploaded_file.name != st.session_state.pdf_name:
            with st.spinner("Reading document..."):
                st.session_state.pdf_text, num_pages = extract_text_from_pdf(uploaded_file)
                st.session_state.pdf_name = uploaded_file.name
                st.session_state.messages = []
                st.session_state.summary = ""
                st.session_state.suggested_questions = []
                st.session_state.quiz_questions = []
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False

        reader = PyPDF2.PdfReader(uploaded_file)
        st.success("✅ Document loaded!")
        st.info(f"📖 Pages: {len(reader.pages)}")
        st.info(f"📝 Characters: {len(st.session_state.pdf_text):,}")

        st.divider()

        if st.button("📋 Generate Summary", use_container_width=True):
            with st.spinner("Summarizing document..."):
                st.session_state.summary = generate_summary(st.session_state.pdf_text)

        if st.button("💡 Suggest Questions", use_container_width=True):
            with st.spinner("Generating questions..."):
                st.session_state.suggested_questions = generate_suggested_questions(st.session_state.pdf_text)

        if st.button("🧠 Generate Quiz", use_container_width=True):
            with st.spinner("Generating quiz..."):
                quiz_text = generate_quiz(st.session_state.pdf_text)
                st.session_state.quiz_questions = parse_quiz(quiz_text)
                st.session_state.quiz_answers = {}
                st.session_state.quiz_submitted = False

        st.divider()

        if st.session_state.messages:
            chat_export = format_chat_for_download(
                st.session_state.messages,
                st.session_state.pdf_name
            )
            st.download_button(
                label="⬇️ Download Chat",
                data=chat_export,
                file_name=f"chat_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )

        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.summary = ""
            st.session_state.suggested_questions = []
            st.session_state.quiz_questions = []
            st.session_state.quiz_answers = {}
            st.session_state.quiz_submitted = False
            st.rerun()

    st.divider()
    st.markdown("**Powered by**")
    st.markdown("🦙 Llama 3.3 via Groq")

# Main area
if st.session_state.pdf_text:

    if st.session_state.summary:
        with st.expander("📋 Document Summary", expanded=True):
            st.markdown(st.session_state.summary)
        st.divider()

    if st.session_state.suggested_questions:
        st.subheader("💡 Suggested Questions")
        cols = st.columns(2)
        for i, question in enumerate(st.session_state.suggested_questions):
            with cols[i % 2]:
                if st.button(question, use_container_width=True, key=f"sq_{i}"):
                    st.session_state.messages.append({"role": "user", "content": question})
                    with st.spinner("Thinking..."):
                        answer = ask_question(
                            st.session_state.pdf_text,
                            question,
                            st.session_state.messages[:-1]
                        )
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    st.rerun()
        st.divider()

    if st.session_state.quiz_questions:
        st.subheader("🧠 Quiz")
        with st.form("quiz_form"):
            for i, q in enumerate(st.session_state.quiz_questions):
                st.markdown(f"**Q{i+1}. {q['question']}**")
                options = [f"{k}) {v}" for k, v in q['options'].items()]
                st.radio(
                    f"Select answer for Q{i+1}",
                    options,
                    key=f"q_{i}",
                    label_visibility="collapsed"
                )
                st.markdown("")
            submitted = st.form_submit_button("Submit Quiz", use_container_width=True)

        if submitted:
            score = 0
            st.subheader("📊 Results")
            for i, q in enumerate(st.session_state.quiz_questions):
                user_answer = st.session_state.get(f"q_{i}", "")
                correct = q['answer']
                user_letter = user_answer[0] if user_answer else ""
                if user_letter == correct:
                    score += 1
                    st.success(f"✅ Q{i+1}: Correct!")
                else:
                    st.error(f"❌ Q{i+1}: Wrong — Correct answer: {correct}) {q['options'][correct]}")
            st.divider()
            st.metric("Your Score", f"{score}/{len(st.session_state.quiz_questions)}")
            if score == len(st.session_state.quiz_questions):
                st.balloons()
        st.divider()

    st.subheader(f"💬 Chat about: {st.session_state.pdf_name}")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    question = st.chat_input("Ask anything about the document...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_question(
                    st.session_state.pdf_text,
                    question,
                    st.session_state.messages[:-1]
                )
            st.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📤 **Step 1**\nUpload a PDF from the sidebar")
    with col2:
        st.info("💬 **Step 2**\nAsk any question about the document")
    with col3:
        st.info("🤖 **Step 3**\nGet instant AI-powered answers")
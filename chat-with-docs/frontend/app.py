import streamlit as st
import requests

st.set_page_config(page_title="Pro RAG Chat", layout="wide")
st.title("Professional RAG Chat (Tiny LLaMA + FAISS)")

BACKEND_URL = "http://127.0.0.1:8000"

# -----------------------
# SESSION STATE
# -----------------------
if "query_input" not in st.session_state:
    st.session_state.query_input = ""
if "eli5" not in st.session_state:
    st.session_state.eli5 = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------
# SIDEBAR FAQ + History + About
# -----------------------
faq_list = [
    {"q": "What is RAG?", "a": "RAG (Retrieval-Augmented Generation) combines document retrieval with LLM generation for precise answers."},
    {"q": "How to upload PDFs?", "a": "Use the 'Upload PDFs' section to select and process multiple PDFs for AI to reference."},
    {"q": "How does Tiny LLaMA work?", "a": "Tiny LLaMA is a smaller, efficient LLaMA model for fast on-device question answering."},
    {"q": "Can AI answer without PDFs?", "a": "Yes, the model can attempt general answers even without uploaded PDFs."},
]

with st.sidebar:
    st.header("FAQ")
    with st.expander("Click FAQ to view questions"):
        for item in faq_list:
            with st.expander(item["q"]):
                st.write(item["a"])

    st.markdown("---")
    st.header("Past Questions")
    if st.session_state.messages:
        # Walk through messages in order (user -> assistant)
        for idx in range(0, len(st.session_state.messages), 2):
            user_msg = st.session_state.messages[idx]
            if user_msg["role"] != "user":
                continue
            answer_msg = st.session_state.messages[idx + 1] if idx + 1 < len(st.session_state.messages) else None
            answer_text = answer_msg["content"] if answer_msg else "No answer yet."
            with st.expander(user_msg["content"]):
                st.markdown(f"**Answer:** {answer_text}")

    st.button("Clear History", on_click=lambda: st.session_state.messages.clear())

    st.markdown("---")
    st.header("About This App")
    st.markdown(
        """
        <div style='background-color:#F8F9F9;padding:10px;border-radius:8px;'>
        <p>This web application allows users to upload PDFs and interact with a Tiny LLaMA model enhanced by FAISS for document retrieval.</p>
        <p>Ask questions and get answers with highlighted references from your documents.  
        The app also supports general knowledge queries even without uploaded files.</p>
        <p>Professional design with expandable PDF highlights, chat history, and FAQ for a seamless experience.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# -----------------------
# FILE UPLOAD
# -----------------------
st.subheader("Upload PDFs")
uploaded_files = st.file_uploader(
    "Select one or more PDFs", type=["pdf"], accept_multiple_files=True
)

# Wider button columns for better look
col1, col2, col3 = st.columns([2, 6, 2])
with col1:
    process_btn = st.button("Process Files", use_container_width=True)
with col3:
    clear_btn = st.button("Clear Uploaded Files", use_container_width=True)

if process_btn and uploaded_files:
    files_to_send = [("files", (f.name, f, "application/pdf")) for f in uploaded_files]
    with st.spinner("Uploading and indexing..."):
        res = requests.post(f"{BACKEND_URL}/upload", files=files_to_send, timeout=300)
    if res.ok:
        st.success("Files uploaded and indexed!")
    else:
        st.error(res.text)

if clear_btn:
    requests.post(f"{BACKEND_URL}/clear_uploads")
    st.session_state.query_input = ""
    st.rerun()

# -----------------------
# QUERY INPUT
# -----------------------
st.subheader("Ask a Question")
st.session_state.query_input = st.text_input(
    "Type your question here", value=st.session_state.query_input
)
st.session_state.eli5 = st.checkbox(
    "Explain Like I'm 5", value=st.session_state.eli5
)

if st.button("Ask") and st.session_state.query_input.strip():
    st.session_state.messages.append({"role": "user", "content": st.session_state.query_input})
    with st.spinner("Thinking..."):
        try:
            res = requests.get(
                f"{BACKEND_URL}/ask",
                params={"query": st.session_state.query_input, "eli5": st.session_state.eli5},
                timeout=300
            )
            if res.ok:
                data = res.json()
                answer = data.get("answer", "")

                # Fix non-PDF answers that may come as dict with 'text'
                
                if isinstance(answer, dict):
                    # Only take the text field, ignore query
                    answer = answer.get("text", "")

                elif isinstance(answer, list):
                    # If backend returns a list of dicts, join their text fields
                    texts = [a.get("text", "") if isinstance(a, dict) else str(a) for a in answer]
                    answer = " ".join(texts)


                # Handle greetings if no PDFs
                greetings = ["hello", "hi", "how are you", "thank you", "thanks"]
                if not data.get("highlighted_pdfs") and any(word in st.session_state.query_input.lower() for word in greetings):
                    answer = "Hello! How can I assist you today?"

                st.session_state.messages.append({"role": "assistant", "content": answer})

                # --- Answer Card ---
                st.markdown(
                    f"""
                    <div style='background-color:#ECF0F1;padding:15px;border-radius:10px;margin-bottom:15px;'>
                        <h3 style='color:#2C3E50;'>Answer</h3>
                        <p style='color:#34495E;'>{answer}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # --- Highlighted PDFs ---
                highlighted = data.get("highlighted_pdfs", [])
                colors = ["#D6EAF8", "#AED6F1"]
                if highlighted:
                    st.markdown("<h3 style='color:#1F618D;margin-bottom:10px;'>Highlighted PDFs</h3>", unsafe_allow_html=True)
                    for idx, pdf in enumerate(highlighted):
                        name = pdf.get("name", "Unnamed PDF")
                        chunks = pdf.get("chunks", [])
                        color = colors[idx % len(colors)]
                        with st.expander(name):
                            for chunk in chunks:
                                st.markdown(
                                    f"<div style='background-color:{color};padding:8px;border-radius:6px;margin-bottom:5px;'>{chunk}</div>",
                                    unsafe_allow_html=True
                                )

            else:
                st.error(res.text)
        except Exception as e:
            st.error(f"Backend error: {e}")

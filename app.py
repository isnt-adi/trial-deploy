import streamlit as st
from backend.system import initialize_qa_chain
from design import apply_custom_styles

# --- Page Config ---
st.set_page_config(page_title="K-Gabay", layout="wide")

# --- Apply Custom Design ---
apply_custom_styles()

# --- Title ---
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.jfif", width=900)

# --- Sidebar ---
with st.sidebar:
    st.subheader("📄 Uploaded PDFs")
    uploaded_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if uploaded_files:
        st.subheader("Files:")
        for file in uploaded_files:
            st.write(f"- {file.name}")
    else:
        st.info("No files uploaded yet.")

# --- QA Chain Initialization ---
if uploaded_files and "qa_chain" not in st.session_state:
    try:
        qa_chain = initialize_qa_chain(uploaded_files[0])
        st.session_state.qa_chain = qa_chain
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hi there! Ask me anything about the PDF!"}
            ]
    except Exception as e:
        st.error(f"Failed to process PDF: {e}")

# --- Initialize Message History ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Upload a PDF to start chatting!"}
    ]

# --- Chat Display ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    if "qa_chain" in st.session_state:
        try:
            with st.spinner("Thinking..."):
                response = st.session_state.qa_chain.run(prompt)
        except Exception as e:
            response = f"❌ Error: {e}"
    else:
        response = "⚠️ No PDF processed yet."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
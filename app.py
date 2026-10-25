"""Optional Streamlit interface; the FastAPI service also serves a built-in HTML UI."""
import httpx
import streamlit as st
from service.config import settings

st.set_page_config(page_title="Local RAG + Laya", page_icon="🧠", layout="wide")
st.title("Local RAG + Laya + Ollama + n8n")
st.caption("Demo only; all HVAC documents are fictional. No appointments are ever booked.")

mode = st.radio("Execution", ["Through n8n + Mailpit", "Direct FastAPI"], horizontal=True)
message = st.text_area("Customer message", "What is included in routine AC maintenance?", height=130)
token = st.text_input("Workflow token (from .env)", value=settings.workflow_token, type="password")
if st.button("Run", type="primary"):
    endpoint = "/api/via-n8n" if mode.startswith("Through") else "/api/process"
    try:
        with st.spinner("Running local pipeline..."):
            with httpx.Client(timeout=190.0) as client:
                response = client.post("http://127.0.0.1:8003" + endpoint,
                    headers={"X-Demo-Token":token}, json={"message":message})
                response.raise_for_status()
                data = response.json()
        st.subheader(data.get("status","unknown"))
        st.write(data.get("answer"))
        st.caption("Sources: " + ", ".join(data.get("sources",[])))
        st.json(data)
    except Exception as exc:
        st.error(str(exc))

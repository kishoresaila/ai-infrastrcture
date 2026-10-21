"""Streamlit UI: one tab per assistant."""
import json
import os

import httpx
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="AI Infrastructure Assistant", page_icon="🛠️", layout="wide")


def stream_answer(question: str, mode: str):
    """Render tokens live; return (full_text, sources)."""
    box, text, sources = st.empty(), "", []
    try:
        with httpx.stream("POST", f"{API}/ask/stream", json={"question": question, "mode": mode}, timeout=600) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                d = json.loads(line)
                if "sources" in d:
                    sources = d["sources"]
                elif "token" in d:
                    text += d["token"]
                    box.markdown(text + "▌")
        box.markdown(text)
    except Exception as e:
        st.error(f"Backend error: {e}")
    if sources:
        st.caption("📚 Sources: " + ", ".join(sources))
    return text, sources


def ask_tab(mode: str, label: str, placeholder: str, height: int = 100, key: str = ""):
    q = st.text_area(label, placeholder=placeholder, height=height, key=f"{mode}_{key}_in")
    if st.button("Ask", key=f"{mode}_{key}_btn", type="primary") and q.strip():
        with st.spinner("Searching docs and thinking..."):
            stream_answer(q, mode)


# ---- sidebar
with st.sidebar:
    st.title("🛠️ Infra Assistant")
    try:
        h = httpx.get(f"{API}/health", timeout=5).json()
        st.write(f"Ollama: **{h['ollama']}**  \nQdrant: **{h['qdrant']}**")
        if h["models"]:
            st.caption("Models: " + ", ".join(h["models"]))
    except Exception:
        st.error("API unreachable")
    if st.button("📥 Re-index documents"):
        with st.spinner("Indexing..."):
            try:
                st.success(httpx.post(f"{API}/ingest", timeout=1800).json())
            except Exception as e:
                st.error(e)

tabs = st.tabs(["💬 Chat", "🐧 Linux", "☸️ Kubernetes", "💾 Storage", "🐳 Docker",
                "⌨️ Commands", "📄 Log Analyzer", "🧮 Calculator"])

with tabs[0]:
    ask_tab("chat", "Ask anything", "How do I fix CrashLoopBackOff?")
with tabs[1]:
    ask_tab("linux", "Paste an error or symptom", "No space left on device")
with tabs[2]:
    ask_tab("kubernetes", "Pod status / question", "Pod STATUS is CrashLoopBackOff")
with tabs[3]:
    ask_tab("storage", "Storage question", "How do I extend an LVM logical volume with XFS?")
with tabs[4]:
    ask_tab("docker", "Docker problem", "Container restarting continuously")
with tabs[5]:
    ask_tab("command", "What do you want to do?", "Create user kishore")
with tabs[6]:
    ask_tab("logs", "Paste log lines", "Failed to start docker.service", height=250)

with tabs[7]:
    st.subheader("Storage Calculator (exact maths, no LLM)")
    c1, c2, c3 = st.columns(3)
    users = c1.number_input("Users", 1, 100000, 100)
    gb = c2.number_input("GB per user", 0.1, 100000.0, 5.0)
    raid = c3.selectbox("RAID", ["RAID0", "RAID1", "RAID5", "RAID6", "RAID10"], index=2)
    c4, c5, c6 = st.columns(3)
    disk = c4.number_input("Disk size (GB)", 1, 100000, 1000)
    growth = c5.number_input("Growth %", 0, 500, 20)
    spares = c6.number_input("Hot spares", 0, 10, 1)
    if st.button("Calculate", type="primary"):
        r = httpx.post(f"{API}/calculator", json={
            "users": users, "gb_per_user": gb, "raid": raid,
            "disk_size_gb": disk, "growth_percent": growth, "hot_spares": spares}, timeout=30)
        if r.status_code == 200:
            d = r.json()
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Needed (with growth)", f"{d['required_with_growth_gb']:,} GB")
            m2.metric("Disks required", d["disks_required"])
            m3.metric("Raw capacity", f"{d['raw_capacity_gb']:,} GB")
            m4.metric("Usable capacity", f"{d['usable_capacity_gb']:,} GB")
            st.caption(f"Fault tolerance: {d['fault_tolerance']} · Total with spares: {d['total_disks_with_spares']} disks")
            with st.expander("Raw JSON"):
                st.json(d)
        else:
            st.error(r.text)

"""Streamlit UI for the AI Infrastructure Assistant."""
import json
import os
import time

import httpx
import pandas as pd
import streamlit as st

API = os.getenv("API_URL", "http://localhost:8000")
st.set_page_config(page_title="AI Infrastructure Assistant", page_icon="🛠️", layout="wide")

CSS = """
<style>
#MainMenu, footer, header[data-testid="stHeader"] {visibility: hidden; height: 0;}
.block-container {padding-top: 1.6rem; max-width: 1180px;}

.hero {
  background: linear-gradient(135deg, #0f766e 0%, #1d4ed8 55%, #6d28d9 100%);
  border-radius: 18px; padding: 26px 32px; margin-bottom: 18px;
  box-shadow: 0 10px 30px rgba(29,78,216,.25);
}
.hero h1 {margin: 0; font-size: 2rem; color: #fff; letter-spacing: -.5px;}
.hero p  {margin: 6px 0 14px; color: #dbeafe; font-size: 1.02rem;}
.badge {display:inline-block; padding: 3px 12px; margin: 0 6px 4px 0; border-radius: 999px;
        background: rgba(255,255,255,.16); color:#fff; font-size:.8rem; border:1px solid rgba(255,255,255,.25);}

.tab-head h3 {margin: 6px 0 2px; font-size: 1.25rem;}
.tab-head p  {margin: 0 0 10px; color:#94a3b8; font-size:.93rem;}

.answer {background:#111a2e; border:1px solid #1f2d4a; border-left:4px solid #2dd4bf;
         border-radius: 12px; padding: 6px 22px 14px; margin-top: 10px;}
.chip {display:inline-block; padding:3px 11px; margin:4px 6px 0 0; border-radius:8px;
       background:#0f2a2a; color:#5eead4; border:1px solid #134e4a; font-size:.8rem;
       font-family: ui-monospace, Consolas, monospace;}
.meta {color:#64748b; font-size:.8rem; margin-top:6px;}

.pill {display:inline-block; padding:2px 10px; border-radius:999px; font-size:.78rem; font-weight:600;}
.pill.ok   {background:#052e2b; color:#2dd4bf; border:1px solid #115e59;}
.pill.down {background:#3b0d0d; color:#f87171; border:1px solid #7f1d1d;}

.card {background:#111a2e; border:1px solid #1f2d4a; border-radius:14px; padding:16px 18px;}
.card .lbl {color:#94a3b8; font-size:.8rem; text-transform:uppercase; letter-spacing:.06em;}
.card .val {font-size:1.7rem; font-weight:700; color:#e6edf7; margin-top:2px;}
.card .sub {color:#64748b; font-size:.8rem;}

.bar {height:16px; border-radius:8px; background:#1e293b; overflow:hidden; display:flex; margin-top:6px;}
.bar .use {background:linear-gradient(90deg,#14b8a6,#2dd4bf);}
.bar .ovh {background:#6d28d9;}

div[data-baseweb="tab-list"] {gap: 4px; flex-wrap: wrap;}
button[data-baseweb="tab"] {border-radius: 10px 10px 0 0; padding: 8px 14px;}
.stButton > button {border-radius: 10px;}
textarea {font-family: ui-monospace, Consolas, monospace !important;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ------------------------------------------------------------------ helpers
@st.cache_data(ttl=10)
def get_health():
    try:
        return httpx.get(f"{API}/health", timeout=5).json()
    except Exception:
        return None


def pill(label: str, ok: bool) -> str:
    return f"<span class='pill {'ok' if ok else 'down'}'>{'●' if ok else '○'} {label}</span>"


def stream_answer(question: str, mode: str):
    """Stream tokens into the page. Returns (text, sources, seconds)."""
    box, text, sources, start = st.empty(), "", [], time.time()
    try:
        with httpx.stream("POST", f"{API}/ask/stream",
                          json={"question": question, "mode": mode}, timeout=600) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if not line:
                    continue
                d = json.loads(line)
                if "sources" in d:
                    sources = d["sources"]
                elif "token" in d:
                    text += d["token"]
                    box.markdown(text + " ▌")
    except Exception as e:
        text = f"⚠️ Backend error: {e}"
    box.empty()
    return text, sources, time.time() - start


def render_answer(text: str, sources: list, secs: float, mode: str):
    st.markdown("<div class='answer'>", unsafe_allow_html=True)
    st.markdown(text)
    st.markdown("</div>", unsafe_allow_html=True)
    if sources:
        chips = "".join(f"<span class='chip'>📄 {s}</span>" for s in sources)
        st.markdown(f"<div>{chips}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='meta'>No matching documents - answered from general knowledge.</div>",
                    unsafe_allow_html=True)
    c1, c2, _ = st.columns([1, 1, 6])
    c1.download_button("⬇ Save", text, file_name=f"{mode}_answer.md", key=f"dl_{mode}")
    st.markdown(f"<div class='meta'>Generated in {secs:.1f}s · local model · private</div>",
                unsafe_allow_html=True)


def ask_tab(mode: str, title: str, desc: str, placeholder: str, examples: list[str], height: int = 110):
    qkey, akey, rkey = f"{mode}_q", f"{mode}_ans", f"{mode}_run"
    st.markdown(f"<div class='tab-head'><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)

    def use_example(q: str):
        st.session_state[qkey] = q
        st.session_state[rkey] = True

    st.caption("Try an example")
    cols = st.columns(len(examples))
    for i, ex in enumerate(examples):
        cols[i].button(ex, key=f"{mode}_ex{i}", on_click=use_example, args=(ex,), use_container_width=True)

    q = st.text_area("Your question", key=qkey, placeholder=placeholder, height=height,
                     label_visibility="collapsed")
    b1, b2, _ = st.columns([1, 1, 6])
    ask = b1.button("Ask  ➜", key=f"{mode}_go", type="primary")
    if b2.button("Clear", key=f"{mode}_clear"):
        st.session_state.pop(akey, None)
        st.rerun()

    if (ask or st.session_state.pop(rkey, False)) and q.strip():
        with st.spinner("Searching your docs and thinking..."):
            text, sources, secs = stream_answer(q, mode)
        st.session_state[akey] = (text, sources, secs)
        st.rerun()

    if akey in st.session_state:
        render_answer(*st.session_state[akey], mode)


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("### 🛠️ Infra Assistant")
    h = get_health()
    if h:
        st.markdown(pill("API", True) + " " + pill("Ollama", h["ollama"] == "ok") + " "
                    + pill("Qdrant", h["qdrant"] == "ok"), unsafe_allow_html=True)
        if h["models"]:
            st.caption("Models loaded")
            for m in h["models"]:
                st.code(m, language=None)
    else:
        st.markdown(pill("API unreachable", False), unsafe_allow_html=True)

    st.divider()
    st.caption("Knowledge base")
    if st.button("📥 Re-index documents", use_container_width=True):
        with st.spinner("Chunking and embedding..."):
            try:
                res = httpx.post(f"{API}/ingest", timeout=1800).json()
                st.success(f"Indexed {res['files']} files · {res['chunks']} chunks")
            except Exception as e:
                st.error(e)
    st.divider()
    st.caption("Everything runs locally: Ollama + Qdrant + FastAPI. Your data never leaves this machine.")

# ------------------------------------------------------------------ hero
st.markdown("""
<div class='hero'>
  <h1>AI Infrastructure Assistant</h1>
  <p>Troubleshoot Linux, Docker, Kubernetes and Storage with answers grounded in your own documentation.</p>
  <span class='badge'>RAG</span><span class='badge'>Local LLM</span>
  <span class='badge'>Qdrant vector search</span><span class='badge'>100% private</span>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["💬 Chat", "🐧 Linux", "☸️ Kubernetes", "💾 Storage", "🐳 Docker",
                "⌨️ Commands", "📄 Logs", "🧮 Calculator"])

with tabs[0]:
    ask_tab("chat", "Ask anything infrastructure",
            "Get an explanation, root cause, commands and references.",
            "How do I fix CrashLoopBackOff?",
            ["Why is my pod pending?", "Explain Docker networking", "What is RAID 10?"])
with tabs[1]:
    ask_tab("linux", "Linux Troubleshooter",
            "Paste an error or symptom - get causes, checks and fixes.",
            "No space left on device",
            ["No space left on device", "SSH connection refused", "Explain journalctl"])
with tabs[2]:
    ask_tab("kubernetes", "Kubernetes Assistant",
            "Meaning, causes, logs/describe commands and the fix.",
            "Pod STATUS is CrashLoopBackOff",
            ["CrashLoopBackOff", "Pod stuck in Pending", "ImagePullBackOff"])
with tabs[3]:
    ask_tab("storage", "Storage Assistant",
            "LVM, RAID, filesystems, NFS, iSCSI, multipath, SAN/NAS.",
            "How do I extend an LVM logical volume with XFS?",
            ["LVM extension", "NFS vs SMB", "iSCSI login process", "Explain Multipath"])
with tabs[4]:
    ask_tab("docker", "Docker Assistant",
            "Diagnose crashing containers, networking and restart policies.",
            "Container restarting continuously",
            ["Container restarting continuously", "Explain Docker networking"])
with tabs[5]:
    ask_tab("command", "Command Generator",
            "Describe a task in plain English - get the exact commands.",
            "Create user kishore",
            ["Create user kishore", "Open port 8080 in firewall", "Find files larger than 1GB"])
with tabs[6]:
    ask_tab("logs", "Log Analyzer",
            "Paste log lines - get what happened, root cause and fix.",
            "Failed to start docker.service",
            ["Failed to start docker.service"], height=240)

# ------------------------------------------------------------------ calculator
with tabs[7]:
    st.markdown("<div class='tab-head'><h3>Storage Calculator</h3>"
                "<p>Exact RAID sizing in code - no AI guesswork.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    users = c1.number_input("Users", 1, 100000, 100)
    gb = c2.number_input("GB per user", 0.1, 100000.0, 5.0)
    raid = c3.selectbox("RAID level", ["RAID0", "RAID1", "RAID5", "RAID6", "RAID10"], index=2)
    c4, c5, c6 = st.columns(3)
    disk = c4.number_input("Disk size (GB)", 1, 100000, 1000)
    growth = c5.number_input("Growth buffer %", 0, 500, 20)
    spares = c6.number_input("Hot spares", 0, 10, 1)

    if st.button("Calculate", type="primary"):
        def calc(level):
            return httpx.post(f"{API}/calculator", json={
                "users": users, "gb_per_user": gb, "raid": level, "disk_size_gb": disk,
                "growth_percent": growth, "hot_spares": spares}, timeout=30)
        r = calc(raid)
        if r.status_code != 200:
            st.error(r.text)
        else:
            d = r.json()
            cards = [("Needed (with growth)", f"{d['required_with_growth_gb']:,.0f} GB", f"{users} users × {gb} GB"),
                     ("Disks required", f"{d['disks_required']}", f"+{d['hot_spares']} hot spare"),
                     ("Raw capacity", f"{d['raw_capacity_gb']:,.0f} GB", f"{d['disks_required']} × {disk} GB"),
                     ("Usable capacity", f"{d['usable_capacity_gb']:,.0f} GB", f"Tolerates {d['fault_tolerance']}")]
            for col, (lbl, val, sub) in zip(st.columns(4), cards):
                col.markdown(f"<div class='card'><div class='lbl'>{lbl}</div>"
                             f"<div class='val'>{val}</div><div class='sub'>{sub}</div></div>",
                             unsafe_allow_html=True)

            eff = d["usable_capacity_gb"] / d["raw_capacity_gb"] * 100
            st.markdown(f"<div class='meta' style='margin-top:14px'>Space efficiency: "
                        f"<b>{eff:.0f}% usable</b> / {100 - eff:.0f}% redundancy overhead</div>"
                        f"<div class='bar'><div class='use' style='width:{eff}%'></div>"
                        f"<div class='ovh' style='width:{100 - eff}%'></div></div>", unsafe_allow_html=True)

            st.markdown("#### Compare all RAID levels for this workload")
            rows = []
            for lvl in ["RAID0", "RAID1", "RAID5", "RAID6", "RAID10"]:
                x = calc(lvl).json()
                rows.append({"RAID": lvl, "Disks": x["disks_required"],
                             "Usable (GB)": int(x["usable_capacity_gb"]),
                             "Efficiency %": round(x["usable_capacity_gb"] / x["raw_capacity_gb"] * 100),
                             "Fault tolerance": x["fault_tolerance"]})
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

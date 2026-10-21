import { useCallback, useEffect, useRef, useState } from "react";
import { RefreshCw } from "lucide-react";
import Sidebar from "./components/Sidebar.jsx";
import Chat from "./components/Chat.jsx";
import Calculator from "./components/Calculator.jsx";
import Documents from "./components/Documents.jsx";
import { MODES } from "./modes.js";
import { getHealth, ingest, streamAsk } from "./api.js";

let uid = 0;
const nid = () => `${Date.now()}-${uid++}`;

export default function App() {
  const [active, setActive] = useState("chat");
  const [convs, setConvs] = useState({});
  const [busy, setBusy] = useState(null); // mode id currently streaming
  const [health, setHealth] = useState(null);
  const [toast, setToast] = useState("");
  const [indexing, setIndexing] = useState(false);
  const abortRef = useRef(null);
  const mode = MODES.find((m) => m.id === active);

  // poll service health
  useEffect(() => {
    let alive = true;
    const tick = () => getHealth().then((h) => alive && setHealth(h)).catch(() => alive && setHealth(null));
    tick();
    const t = setInterval(tick, 15000);
    return () => { alive = false; clearInterval(t); };
  }, []);

  const patchLast = useCallback((id, fn) => {
    setConvs((c) => {
      const list = [...(c[id] || [])];
      if (list.length === 0) return c; // conversation was cleared mid-stream
      list[list.length - 1] = fn(list[list.length - 1]);
      return { ...c, [id]: list };
    });
  }, []);

  const send = async (text) => {
    const id = active;
    const t0 = performance.now();
    setConvs((c) => ({
      ...c,
      [id]: [...(c[id] || []),
        { id: nid(), role: "user", text },
        { id: nid(), role: "assistant", text: "", sources: [], streaming: true }],
    }));
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    setBusy(id);
    try {
      for await (const ev of streamAsk(text, id, ctrl.signal)) {
        if (ev.sources) patchLast(id, (m) => ({ ...m, sources: ev.sources }));
        if (ev.token) patchLast(id, (m) => ({ ...m, text: m.text + ev.token }));
      }
    } catch (e) {
      if (e.name !== "AbortError") {
        patchLast(id, (m) => ({
          ...m,
          text: (m.text ? m.text + "\n\n" : "") +
            `**Could not reach the assistant.** ${e.message}. Check that the backend, Ollama and Qdrant containers are running.`,
        }));
      }
    } finally {
      patchLast(id, (m) => ({ ...m, streaming: false, secs: (performance.now() - t0) / 1000 }));
      setBusy(null);
    }
  };

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(""), 4000);
  };

  const reindex = async () => {
    setIndexing(true);
    try {
      const r = await ingest();
      setToast(`Indexed ${r.files} files · ${r.chunks} chunks` + (r.errors?.length ? ` · ${r.errors.length} failed` : ""));
    } catch {
      setToast("Indexing failed. Is Ollama running with nomic-embed-text?");
    } finally {
      setIndexing(false);
      setTimeout(() => setToast(""), 4000);
    }
  };

  const ok = (v) => v === "ok";

  return (
    <div className="app">
      <Sidebar active={active} onSelect={setActive} health={health} />
      <main className="main">
        <header className="topbar">
          <div>
            <h1>{mode.label}</h1>
          </div>
          <div className="top-right">
            <span className={`pill ${health ? "ok" : "down"}`}><i />API</span>
            <span className={`pill ${ok(health?.ollama) ? "ok" : "down"}`}><i />Ollama</span>
            <span className={`pill ${ok(health?.qdrant) ? "ok" : "down"}`}><i />Qdrant</span>
            <button className="outline" onClick={reindex} disabled={indexing}>
              <RefreshCw size={14} className={indexing ? "spin" : ""} />
              {indexing ? "Indexing..." : "Re-index docs"}
            </button>
          </div>
        </header>

        {mode.id === "calculator" ? (
          <Calculator />
        ) : mode.id === "documents" ? (
          <Documents onToast={showToast} />
        ) : (
          <Chat
            key={mode.id}
            mode={mode}
            messages={convs[mode.id] || []}
            busy={busy === mode.id}
            onSend={send}
            onStop={() => abortRef.current?.abort()}
            onClear={() => setConvs((c) => ({ ...c, [mode.id]: [] }))}
          />
        )}
        {toast && <div className="toast">{toast}</div>}
      </main>
    </div>
  );
}

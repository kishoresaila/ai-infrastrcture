import { useEffect, useRef, useState } from "react";
import { ArrowUp, Square, Copy, Check, FileText, Trash2 } from "lucide-react";
import Markdown from "./Markdown.jsx";

function Assistant({ m }) {
  const [copied, setCopied] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(m.text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch { /* ignore */ }
  };

  return (
    <div className="msg assistant">
      <div className="avatar">AI</div>
      <div className="bubble">
        {m.text ? <Markdown text={m.text} /> : <div className="typing"><i /><i /><i /></div>}
        {m.streaming && m.text && <span className="cursor" />}

        {!m.streaming && (
          <div className="msg-foot">
            {m.sources?.length > 0 ? (
              <div className="sources">
                {m.sources.map((s) => (
                  <span key={s} className="chip"><FileText size={12} /> {s}</span>
                ))}
              </div>
            ) : (
              <span className="muted">No matching docs: answered from general knowledge</span>
            )}
            <div className="foot-actions">
              {m.secs != null && <span className="muted">{m.secs.toFixed(1)}s</span>}
              <button className="ghost-btn" onClick={copy}>
                {copied ? <Check size={14} /> : <Copy size={14} />}
                {copied ? "Copied" : "Copy"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function Chat({ mode, messages, busy, onSend, onStop, onClear }) {
  const [text, setText] = useState("");
  const endRef = useRef(null);
  const taRef = useRef(null);

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);
  useEffect(() => { setText(""); taRef.current?.focus(); }, [mode.id]);

  // auto-grow textarea
  useEffect(() => {
    const el = taRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = Math.min(el.scrollHeight, 220) + "px";
  }, [text]);

  const submit = (q = text) => {
    const v = q.trim();
    if (!v || busy) return;
    onSend(v);
    setText("");
  };

  const onKey = (e) => {
    if (e.key !== "Enter") return;
    // Enter sends (single-line modes); Ctrl/Cmd+Enter always sends; Shift+Enter = new line
    if ((e.ctrlKey || e.metaKey) || (!e.shiftKey && !mode.tall)) {
      e.preventDefault();
      submit();
    }
  };

  const empty = messages.length === 0;

  return (
    <div className="chat">
      <div className="scroll">
        {empty ? (
          <div className="empty">
            <div className="empty-icon"><mode.icon size={26} /></div>
            <h2>{mode.title}</h2>
            <p>{mode.desc}</p>
            <div className="examples">
              {mode.examples.map((ex) => (
                <button key={ex} className="example" onClick={() => submit(ex)}>{ex}</button>
              ))}
            </div>
          </div>
        ) : (
          <div className="thread">
            {messages.map((m) =>
              m.role === "user" ? (
                <div key={m.id} className="msg user"><div className="bubble user-bubble">{m.text}</div></div>
              ) : (
                <Assistant key={m.id} m={m} />
              )
            )}
            <div ref={endRef} />
          </div>
        )}
      </div>

      <div className="composer-wrap">
        <div className="composer">
          <textarea
            ref={taRef}
            value={text}
            rows={mode.tall ? 4 : 1}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={onKey}
            placeholder={mode.placeholder}
          />
          <div className="composer-actions">
            {!empty && (
              <button className="ghost-btn" onClick={onClear} title="Clear conversation">
                <Trash2 size={14} /> Clear
              </button>
            )}
            <span className="hint">{mode.tall ? "Ctrl+Enter to send" : "Enter to send · Shift+Enter for new line"}</span>
            {busy ? (
              <button className="send stop" onClick={onStop} aria-label="Stop"><Square size={14} fill="currentColor" /></button>
            ) : (
              <button className="send" onClick={() => submit()} disabled={!text.trim()} aria-label="Send">
                <ArrowUp size={18} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

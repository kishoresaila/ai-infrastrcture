import { useCallback, useEffect, useRef, useState } from "react";
import { CheckCircle2, FileText, Loader2, Trash2, UploadCloud, X, XCircle } from "lucide-react";
import { deleteDoc, listDocs, uploadDocs } from "../api.js";

const DEFAULT_CATS = ["linux", "docker", "kubernetes", "storage", "devops"];
const DEFAULT_EXT = [".docx", ".md", ".pdf", ".txt"];

const kb = (n) => (n == null ? "-" : n < 1024 * 1024 ? `${(n / 1024).toFixed(0)} KB` : `${(n / 1024 / 1024).toFixed(1)} MB`);

export default function Documents({ onToast }) {
  const [info, setInfo] = useState({ documents: [], categories: DEFAULT_CATS, allowed: DEFAULT_EXT, max_mb: 20 });
  const [loadErr, setLoadErr] = useState("");
  const [category, setCategory] = useState("linux");
  const [staged, setStaged] = useState([]);
  const [drag, setDrag] = useState(false);
  const [busy, setBusy] = useState(false);
  const [results, setResults] = useState([]);
  const inputRef = useRef(null);

  const refresh = useCallback(async () => {
    try {
      setInfo(await listDocs());
      setLoadErr("");
    } catch (e) {
      setLoadErr(e.message);
    }
  }, []);
  useEffect(() => { refresh(); }, [refresh]);

  const stage = (fileList) => {
    const incoming = Array.from(fileList);
    setResults([]);
    setStaged((cur) => {
      const seen = new Set(cur.map((f) => f.name + f.size));
      return [...cur, ...incoming.filter((f) => !seen.has(f.name + f.size))];
    });
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDrag(false);
    stage(e.dataTransfer.files);
  };

  const upload = async () => {
    setBusy(true);
    setResults([]);
    try {
      const res = await uploadDocs(staged, category);
      setResults(res.results);
      const ok = res.results.filter((r) => r.ok);
      if (ok.length) onToast?.(`Indexed ${ok.length} file${ok.length > 1 ? "s" : ""} · ${ok.reduce((a, r) => a + r.chunks, 0)} chunks`);
      setStaged(staged.filter((f) => !ok.some((r) => r.name === f.name)));
      await refresh();
    } catch (e) {
      setResults([{ name: "Upload", ok: false, error: e.message }]);
    } finally {
      setBusy(false);
    }
  };

  const remove = async (d) => {
    if (!window.confirm(`Delete ${d.name} from ${d.category}? It will no longer be used in answers.`)) return;
    try {
      await deleteDoc(d.category, d.name);
      onToast?.(`Deleted ${d.name}`);
      refresh();
    } catch (e) {
      onToast?.(e.message);
    }
  };

  const grouped = info.categories
    .map((c) => ({ c, items: info.documents.filter((d) => d.category === c) }))
    .filter((g) => g.items.length);
  const extList = info.allowed.join("  ");

  return (
    <div className="scroll">
      <div className="calc">
        <div className="panel">
          <div className="up-head">
            <div>
              <b>Upload documents</b>
              <p className="muted small">Files are saved, split into chunks and indexed immediately.</p>
            </div>
            <label className="field inline">
              <span>Category</span>
              <select value={category} onChange={(e) => setCategory(e.target.value)}>
                {info.categories.map((c) => <option key={c}>{c}</option>)}
              </select>
            </label>
          </div>

          <div
            className={`dropzone ${drag ? "drag" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
            onDragLeave={() => setDrag(false)}
            onDrop={onDrop}
            onClick={() => inputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && inputRef.current?.click()}
          >
            <UploadCloud size={30} />
            <div><b>Drag &amp; drop files here</b> or click to browse</div>
            <small>{extList} · up to {info.max_mb} MB each</small>
            <input
              ref={inputRef} type="file" multiple hidden accept={info.allowed.join(",")}
              onChange={(e) => { stage(e.target.files); e.target.value = ""; }}
            />
          </div>

          {staged.length > 0 && (
            <>
              <ul className="filelist">
                {staged.map((f) => (
                  <li key={f.name + f.size}>
                    <FileText size={16} />
                    <span className="fname">{f.name}</span>
                    <span className="muted small">{kb(f.size)}</span>
                    <button className="ghost-btn" onClick={() => setStaged(staged.filter((x) => x !== f))} aria-label={`Remove ${f.name}`}>
                      <X size={14} />
                    </button>
                  </li>
                ))}
              </ul>
              <button className="primary" onClick={upload} disabled={busy}>
                {busy ? <><Loader2 size={15} className="spin" /> Indexing... this can take a minute</> :
                  `Upload & index ${staged.length} file${staged.length > 1 ? "s" : ""} to "${category}"`}
              </button>
            </>
          )}

          {results.length > 0 && (
            <ul className="results">
              {results.map((r, i) => (
                <li key={i} className={r.ok ? "good" : "fail"}>
                  {r.ok ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                  <b>{r.name}</b>
                  <span>{r.ok ? `${r.chunks} chunks indexed` : r.error}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="panel">
          <b>Indexed documents</b>
          <span className="muted small"> · {info.documents.length} file{info.documents.length === 1 ? "" : "s"}</span>
          {loadErr && <div className="error">{loadErr}. Is the backend running?</div>}
          {!loadErr && grouped.length === 0 && (
            <p className="muted">Nothing indexed yet. Upload a file above, or use "Re-index docs" to index the documents folder.</p>
          )}
          {grouped.map(({ c, items }) => (
            <div key={c} className="doc-group">
              <div className="doc-cat">{c}</div>
              {items.map((d) => (
                <div key={d.name} className="doc-row">
                  <FileText size={16} />
                  <span className="fname">{d.name}</span>
                  <span className="muted small">{d.chunks} chunks · {kb(d.size)}</span>
                  <button className="ghost-btn danger" onClick={() => remove(d)} aria-label={`Delete ${d.name}`}>
                    <Trash2 size={15} />
                  </button>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

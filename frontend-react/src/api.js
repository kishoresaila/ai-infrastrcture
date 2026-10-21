const json = { "Content-Type": "application/json" };

export async function getHealth() {
  const r = await fetch("/api/health");
  if (!r.ok) throw new Error("health failed");
  return r.json();
}

export async function ingest() {
  const r = await fetch("/api/ingest", { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function calculate(payload) {
  const r = await fetch("/api/calculator", {
    method: "POST",
    headers: json,
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || "Calculation failed");
  return r.json();
}

/** Async generator over the NDJSON stream: yields {sources} then {token}... */
export async function* streamAsk(question, mode, signal) {
  const r = await fetch("/api/ask/stream", {
    method: "POST",
    headers: json,
    body: JSON.stringify({ question, mode }),
    signal,
  });
  if (!r.ok) throw new Error(`Server returned ${r.status}`);
  const reader = r.body.getReader();
  const dec = new TextDecoder();
  let buf = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += dec.decode(value, { stream: true });
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (line) yield JSON.parse(line);
    }
  }
}

export async function listDocs() {
  const r = await fetch("/api/documents");
  if (!r.ok) throw new Error("Could not load documents");
  return r.json();
}

export async function uploadDocs(files, category) {
  const fd = new FormData();
  fd.append("category", category);
  files.forEach((f) => fd.append("files", f));
  const r = await fetch("/api/documents/upload", { method: "POST", body: fd });
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || `Upload failed (${r.status})`);
  return r.json();
}

export async function deleteDoc(category, name) {
  const r = await fetch(`/api/documents/${encodeURIComponent(category)}/${encodeURIComponent(name)}`, { method: "DELETE" });
  if (!r.ok) throw new Error("Delete failed");
  return r.json();
}

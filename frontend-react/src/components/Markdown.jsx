import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Check, Copy } from "lucide-react";

function CodeBlock({ children }) {
  const [copied, setCopied] = useState(false);
  // react-markdown renders <pre><code className="language-x">text</code></pre>
  const code = children?.props ?? {};
  const text = String(code.children ?? "").replace(/\n$/, "");
  const lang = /language-(\w+)/.exec(code.className || "")?.[1] || "shell";

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      /* clipboard unavailable (non-https) - ignore */
    }
  };

  return (
    <div className="codeblock">
      <div className="codeblock-bar">
        <span>{lang}</span>
        <button onClick={copy} className="ghost-btn" aria-label="Copy code">
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre><code>{text}</code></pre>
    </div>
  );
}

export default function Markdown({ text }) {
  return (
    <div className="md">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={{ pre: CodeBlock }}>
        {text}
      </ReactMarkdown>
    </div>
  );
}

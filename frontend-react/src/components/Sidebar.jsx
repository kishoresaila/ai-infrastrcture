import { ShieldCheck, TerminalSquare } from "lucide-react";
import { MODES } from "../modes.js";

export default function Sidebar({ active, onSelect, health }) {
  const groups = ["Assistants", "Tools", "Knowledge"];
  const model = health?.models?.find((m) => !m.startsWith("nomic"));

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="logo"><TerminalSquare size={18} color="#fff" /></div>
        <div>
          <div className="brand-name">InfraAssist</div>
          <div className="brand-sub">AI Infrastructure Assistant</div>
        </div>
      </div>

      <nav>
        {groups.map((g) => (
          <div key={g} className="nav-group">
            <div className="nav-label">{g}</div>
            {MODES.filter((m) => m.group === g).map((m) => {
              const Icon = m.icon;
              return (
                <button
                  key={m.id}
                  className={`nav-item ${active === m.id ? "active" : ""}`}
                  onClick={() => onSelect(m.id)}
                >
                  <Icon size={17} />
                  <span>{m.label}</span>
                </button>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="side-foot">
        <ShieldCheck size={15} />
        <div>
          <b>Runs 100% locally</b>
          <div>{model ? model : "Ollama + Qdrant"}</div>
        </div>
      </div>
    </aside>
  );
}

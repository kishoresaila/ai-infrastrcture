import { useState } from "react";
import { calculate } from "../api.js";

const LEVELS = ["RAID0", "RAID1", "RAID5", "RAID6", "RAID10"];
const fmt = (n) => Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 });

function Field({ label, children }) {
  return <label className="field"><span>{label}</span>{children}</label>;
}

export default function Calculator() {
  const [f, setF] = useState({
    users: 100, gb_per_user: 5, raid: "RAID5", disk_size_gb: 1000, growth_percent: 20, hot_spares: 1,
  });
  const [res, setRes] = useState(null);
  const [rows, setRows] = useState([]);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (k) => (e) => setF({ ...f, [k]: k === "raid" ? e.target.value : Number(e.target.value) });

  const run = async (e) => {
    e.preventDefault();
    setErr(""); setLoading(true);
    try {
      const [main, ...all] = await Promise.all([f.raid, ...LEVELS].map((raid) => calculate({ ...f, raid })));
      setRes(main);
      setRows(all);
    } catch (ex) {
      setErr(ex.message);
    } finally {
      setLoading(false);
    }
  };

  const eff = res ? (res.usable_capacity_gb / res.raw_capacity_gb) * 100 : 0;

  return (
    <div className="scroll">
      <div className="calc">
        <form className="panel" onSubmit={run}>
          <div className="grid3">
            <Field label="Users"><input type="number" min="1" value={f.users} onChange={set("users")} /></Field>
            <Field label="GB per user"><input type="number" min="0.1" step="any" value={f.gb_per_user} onChange={set("gb_per_user")} /></Field>
            <Field label="RAID level">
              <select value={f.raid} onChange={set("raid")}>{LEVELS.map((l) => <option key={l}>{l}</option>)}</select>
            </Field>
            <Field label="Disk size (GB)"><input type="number" min="1" value={f.disk_size_gb} onChange={set("disk_size_gb")} /></Field>
            <Field label="Growth buffer (%)"><input type="number" min="0" value={f.growth_percent} onChange={set("growth_percent")} /></Field>
            <Field label="Hot spares"><input type="number" min="0" value={f.hot_spares} onChange={set("hot_spares")} /></Field>
          </div>
          <button className="primary" disabled={loading}>{loading ? "Calculating..." : "Calculate"}</button>
          {err && <div className="error">{err}</div>}
        </form>

        {res && (
          <>
            <div className="cards">
              <div className="stat"><span>Needed (with growth)</span><b>{fmt(res.required_with_growth_gb)} GB</b><small>{res.users} users × {res.gb_per_user} GB</small></div>
              <div className="stat"><span>Disks required</span><b>{res.disks_required}</b><small>+ {res.hot_spares} hot spare</small></div>
              <div className="stat"><span>Raw capacity</span><b>{fmt(res.raw_capacity_gb)} GB</b><small>{res.disks_required} × {fmt(res.disk_size_gb)} GB</small></div>
              <div className="stat accent"><span>Usable capacity</span><b>{fmt(res.usable_capacity_gb)} GB</b><small>Tolerates {res.fault_tolerance}</small></div>
            </div>

            <div className="panel">
              <div className="eff-head"><b>Space efficiency</b><span>{eff.toFixed(0)}% usable · {(100 - eff).toFixed(0)}% redundancy</span></div>
              <div className="bar"><div className="use" style={{ width: `${eff}%` }} /><div className="ovh" style={{ width: `${100 - eff}%` }} /></div>
            </div>

            <div className="panel">
              <b>Compare all RAID levels for this workload</b>
              <table>
                <thead><tr><th>RAID</th><th>Disks</th><th>Usable (GB)</th><th>Efficiency</th><th>Fault tolerance</th></tr></thead>
                <tbody>
                  {rows.map((r) => (
                    <tr key={r.raid_level} className={r.raid_level === res.raid_level ? "sel" : ""}>
                      <td><b>{r.raid_level}</b></td>
                      <td>{r.disks_required}</td>
                      <td>{fmt(r.usable_capacity_gb)}</td>
                      <td>{((r.usable_capacity_gb / r.raw_capacity_gb) * 100).toFixed(0)}%</td>
                      <td>{r.fault_tolerance}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

/* frontend/app.js
   Hooks UI to backend endpoints:
     - POST /process_all
     - POST /build_index
     - GET  /files
     - POST /chat  (message/top_k)
     - GET  /download/:id
*/

const logEl = document.getElementById("log");
const filesEl = document.getElementById("files");
const chatMessages = document.getElementById("chat-messages");
const input = document.getElementById("chat-input");
const topkSelect = document.getElementById("topk");

// small helpers
function now() { return new Date().toLocaleTimeString(); }
function log(msg) { logEl.textContent = `[${now()}] ${msg}\n\n` + logEl.textContent; }
function addMsg(text, who='bot') {
  const d = document.createElement("div");
  d.className = `msg ${who}`;
  d.innerHTML = text.replace(/\n/g, "<br>");
  chatMessages.appendChild(d);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
function pulse(el) { el.style.transform = 'scale(0.98)'; setTimeout(()=>el.style.transform='',180); }

// network
async function apiPost(path, body) {
  try {
    const res = await fetch(path, {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(body||{})
    });
    const text = await res.text();
    let json = null;
    try { json = JSON.parse(text); } catch(e) {}
    log(`${path} → ${res.status}`);
    if (json) log(JSON.stringify(json, null, 2));
    else log(text.slice(0, 400));
    return {ok: res.ok, status: res.status, json, text};
  } catch (e) {
    log(`ERROR ${path}: ${e}`);
    return {ok:false, error:e};
  }
}

async function apiGet(path) {
  try {
    const res = await fetch(path);
    const json = await res.json().catch(()=>null);
    log(`${path} → ${res.status}`);
    if (json) log(JSON.stringify(json, null, 2));
    return {ok: res.ok, status: res.status, json};
  } catch (e) {
    log(`ERROR ${path}: ${e}`);
    return {ok:false, error:e};
  }
}

// UI actions
document.getElementById("btn-process").onclick = async (e) => {
  pulse(e.target);
  log("-> /process_all");
  const r = await apiPost("/process_all", {});
  if (!r.ok) log("process_all failed; check server logs.");
  else log("process_all completed.");
};

document.getElementById("btn-build").onclick = async (e) => {
  pulse(e.target);
  log("-> /build_index (this may take some time)");
  const r = await apiPost("/build_index", {});
  if (r.ok) log("Index built.");
  else log("Index build failed.");
};

document.getElementById("btn-list").onclick = async (e) => {
  pulse(e.target);
  const r = await apiGet("/files");
  filesEl.innerHTML = "";
  if (!r.ok || !r.json) { filesEl.textContent = "No file data or server error — check log."; return; }
  if (!r.json.files || r.json.files.length === 0) { filesEl.textContent = "No files indexed."; return; }
  r.json.files.forEach(f => {
    const div = document.createElement("div");
    div.className = "file";
    div.innerHTML = `<strong>${f.id} — ${f.filename}</strong><br>${f.department} / ${f.year}<br><a href="/download/${f.id}" target="_blank">Download</a>`;
    filesEl.appendChild(div);
  });
  log("Updated file list.");
};

// CHAT: call your /chat endpoint
document.getElementById("btn-send").onclick = async (e) => {
  const q = input.value?.trim();
  if (!q) { addMsg("Type a question first...", "user"); return; }
  pulse(e.target);
  addMsg(q, "user");
  input.value = "";
  addMsg("Thinking... (searching index)", "bot");

  const top_k = parseInt(topkSelect.value || "5", 10);
  const r = await apiPost("/chat", {message: q, top_k});
  // remove the temporary "Thinking..." (last bot msg)
  const last = chatMessages.querySelectorAll(".msg.bot");
  if (last && last.length) last[last.length-1].remove();

  if (!r.ok) {
    addMsg("Server error while chatting. Check logs.", "bot");
    return;
  }
  const answer = r.json?.answer || r.text || "No answer.";
  addMsg(answer, "bot");

  // show hits (if provided)
  if (r.json && r.json.hits && r.json.hits.length) {
    const hitsHtml = r.json.hits.map(h => {
      return `<div style="margin:6px 0;padding:8px;background:#071022;border-radius:6px">
                <div><strong>${h.filename}</strong> — ${h.department} / ${h.year} (score: ${h.score?.toFixed(3)})</div>
                <div style="margin-top:6px;color:var(--muted);font-size:13px">${(h.snippet||'').slice(0,300).replace(/\n/g,' ')}</div>
                <div style="margin-top:6px"><a href="/download/${h.file_id}" target="_blank">Download</a></div>
              </div>`;
    }).join("");
    addMsg(`<strong>Top matches:</strong><br>${hitsHtml}`, "bot");
  }
};

// keyboard: Enter to send
input.addEventListener("keydown", (e) => { if (e.key === "Enter") { document.getElementById("btn-send").click(); } });

// convenience: initial file list
document.getElementById("btn-list").click();

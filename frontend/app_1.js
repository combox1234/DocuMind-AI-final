const log = (s) => {
  const el = document.getElementById("log");
  el.textContent = (new Date()).toLocaleTimeString() + " — " + s + "\n\n" + el.textContent;
};

async function post(path, body) {
  try {
    const res = await fetch(path, {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body||{})});
    const text = await res.text();
    log(`${path} -> ${res.status}\n${text}`);
    return {ok: res.ok, status: res.status, text};
  } catch(e) {
    log(`ERROR calling ${path}: ${e}`);
    return {ok:false, error:e};
  }
}

async function get(path) {
  try {
    const res = await fetch(path);
    const json = await res.json().catch(()=>null);
    const txt = json ? JSON.stringify(json, null, 2) : await res.text();
    log(`${path} -> ${res.status}\n${txt}`);
    return {ok: res.ok, status: res.status, json, text: txt};
  } catch(e) {
    log(`ERROR calling ${path}: ${e}`);
    return {ok:false, error:e};
  }
}

document.getElementById("btn-process").onclick = async () => {
  log("Sending POST /process_all ...");
  await post("/process_all");
};

document.getElementById("btn-build").onclick = async () => {
  log("Sending POST /build_index ... (may take a while)");
  await post("/build_index");
};

document.getElementById("btn-list").onclick = async () => {
  const r = await get("/files");
  const filesDiv = document.getElementById("files");
  filesDiv.innerHTML = "";
  if (r.json && r.json.files) {
    r.json.files.forEach(f => {
      const d = document.createElement("div");
      d.className = "file";
      d.innerHTML = `<strong>${f.id} — ${f.filename}</strong><br>${f.department} / ${f.year}<br><a href="/download/${f.id}" target="_blank">Download</a>`;
      filesDiv.appendChild(d);
    });
  } else {
    filesDiv.textContent = "No files (or /files returned non-json). Check log.";
  }
};

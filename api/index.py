import json
import os
import queue
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from core.business_profile import BusinessProfile
from core.memory import Memory
from core.orchestrator import Orchestrator
from agents.sales_agent import SalesAgent
from agents.operations_agent import OperationsAgent
from agents.marketing_agent import MarketingAgent

app = FastAPI(title="AI Operating System")

_yaml_profile = None


def get_yaml_profile():
    global _yaml_profile
    if _yaml_profile is None:
        _yaml_profile = BusinessProfile.load(str(ROOT / "config" / "business_profile.yaml"))
    return _yaml_profile


def build_orchestrator(profile):
    memory = Memory()
    orch = Orchestrator(profile, memory)
    orch.register_agent("sales", SalesAgent(profile, memory))
    orch.register_agent("operations", OperationsAgent(profile, memory))
    orch.register_agent("marketing", MarketingAgent(profile, memory))
    return orch


HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI OS</title>
<script src="https://cdn.jsdelivr.net/npm/marked@4/marked.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --bg:#0d0d0f;--surface:#16161a;--surface2:#1e1e24;
  --border:#2a2a35;--text:#e4e4ef;--muted:#6b7280;
  --accent:#6366f1;--accent2:#818cf8;
  --sales:#3b82f6;--ops:#10b981;--mktg:#a855f7;
  --user:#1e3a5f;
}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;overflow:hidden}
.sidebar{width:270px;min-width:270px;background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;padding:20px 16px;gap:20px;overflow-y:auto}
.logo{display:flex;align-items:center;gap:8px;font-size:17px;font-weight:700}
.logo-icon{width:32px;height:32px;background:var(--accent);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px}
.biz-industry{font-size:11px;color:var(--accent2);text-transform:uppercase;letter-spacing:.5px;margin-top:10px;padding-left:4px}
.section-title{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:8px;font-weight:600}
.agent-row{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:8px;font-size:13px;background:var(--surface2);margin-bottom:4px}
.dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.d-s{background:var(--sales)}.d-o{background:var(--ops)}.d-m{background:var(--mktg)}
.agent-desc{font-size:11px;color:var(--muted);margin-top:1px}
.chip{display:block;width:100%;text-align:left;padding:8px 10px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--muted);font-size:12px;cursor:pointer;margin-bottom:4px;transition:all .15s;font-family:inherit;line-height:1.4}
.chip:hover{border-color:var(--accent);color:var(--text);background:rgba(99,102,241,.08)}
.main{flex:1;display:flex;flex-direction:column;min-width:0;overflow:hidden}
.chat-header{padding:14px 24px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;background:var(--surface);flex-shrink:0}
.chat-header h1{font-size:15px;font-weight:600}
.header-right{display:flex;align-items:center;gap:12px}
.live{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--ops)}
.live::before{content:'';display:block;width:6px;height:6px;border-radius:50%;background:var(--ops);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.gear-btn{background:none;border:1px solid var(--border);border-radius:8px;color:var(--muted);cursor:pointer;padding:6px 10px;font-size:13px;transition:all .15s;font-family:inherit}
.gear-btn:hover{border-color:var(--accent);color:var(--text)}
.messages{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:16px}
.messages::-webkit-scrollbar{width:4px}
.messages::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px}
.welcome{margin:auto;text-align:center;max-width:400px}
.welcome-icon{font-size:40px;margin-bottom:16px}
.welcome h2{font-size:22px;font-weight:700;margin-bottom:8px}
.welcome p{font-size:14px;color:var(--muted);line-height:1.6}
.msg{display:flex;flex-direction:column;gap:5px}
.msg.user{align-self:flex-end;max-width:75%}
.msg.agent{align-self:flex-start;max-width:85%}
.bubble{padding:12px 16px;border-radius:16px;font-size:14px;line-height:1.65}
.msg.user .bubble{background:var(--user);color:#fff;border-bottom-right-radius:4px}
.msg.agent .bubble{background:var(--surface);border-bottom-left-radius:4px;border:1px solid var(--border)}
.agent-tag{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--muted)}
.badge{padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}
.b-sales{background:rgba(59,130,246,.15);color:var(--sales)}
.b-operations{background:rgba(16,185,129,.15);color:var(--ops)}
.b-marketing{background:rgba(168,85,247,.15);color:var(--mktg)}
.typing-bubble{display:flex;gap:4px;align-items:center;padding:14px 18px;background:var(--surface);border-radius:16px;border-bottom-left-radius:4px;border:1px solid var(--border)}
.typing-bubble span{width:6px;height:6px;border-radius:50%;background:var(--muted);animation:bop 1.2s infinite}
.typing-bubble span:nth-child(2){animation-delay:.2s}
.typing-bubble span:nth-child(3){animation-delay:.4s}
@keyframes bop{0%,80%,100%{transform:translateY(0)}40%{transform:translateY(-5px)}}
.input-wrap{padding:16px 24px;border-top:1px solid var(--border);display:flex;gap:10px;background:var(--surface);flex-shrink:0}
textarea{flex:1;background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:11px 14px;color:var(--text);font-size:14px;font-family:inherit;resize:none;outline:none;line-height:1.5;min-height:46px;max-height:180px;transition:border-color .15s}
textarea:focus{border-color:var(--accent)}
textarea::placeholder{color:var(--muted)}
.send{background:var(--accent);border:none;border-radius:12px;padding:11px 20px;color:#fff;font-size:13px;font-weight:600;cursor:pointer;transition:opacity .15s;align-self:flex-end;font-family:inherit;white-space:nowrap}
.send:hover{opacity:.85}.send:disabled{opacity:.4;cursor:not-allowed}
.bubble h2{font-size:15px;margin:10px 0 5px}.bubble h3{font-size:14px;margin:8px 0 4px}
.bubble p{margin:7px 0}.bubble ul,.bubble ol{padding-left:18px;margin:7px 0}.bubble li{margin:3px 0}
.bubble table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px}
.bubble th,.bubble td{border:1px solid var(--border);padding:6px 10px;text-align:left}
.bubble th{background:rgba(255,255,255,.05);font-weight:600}
.bubble code{background:rgba(255,255,255,.07);padding:1px 5px;border-radius:4px;font-family:monospace;font-size:12px}
.bubble pre{background:rgba(255,255,255,.05);padding:12px;border-radius:8px;overflow-x:auto;margin:8px 0}
.bubble pre code{background:transparent;padding:0}
.bubble strong{color:#fff}.bubble em{color:var(--accent2)}
.bubble a{color:var(--accent2);text-decoration:none}.bubble a:hover{text-decoration:underline}
.bubble blockquote{border-left:3px solid var(--accent);padding-left:12px;color:var(--muted);margin:8px 0}
.bubble hr{border:none;border-top:1px solid var(--border);margin:10px 0}
/* Modal */
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:200;display:flex;align-items:center;justify-content:center}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:16px;width:560px;max-width:95vw;max-height:90vh;display:flex;flex-direction:column;overflow:hidden;z-index:201}
.modal-hdr{padding:18px 22px 14px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.modal-hdr h2{font-size:16px;font-weight:700}
.xbtn{background:none;border:none;color:var(--muted);font-size:22px;cursor:pointer;line-height:1;padding:0 4px}
.xbtn:hover{color:var(--text)}
.tabs{display:flex;border-bottom:1px solid var(--border);flex-shrink:0}
.tbtn{flex:1;padding:10px;background:none;border:none;border-bottom:2px solid transparent;color:var(--muted);font-size:13px;font-family:inherit;cursor:pointer;transition:all .15s}
.tbtn.on{color:var(--accent2);border-bottom-color:var(--accent)}
.mbody{padding:20px 22px;overflow-y:auto;flex:1}
.panel{display:none}.panel.on{display:block}
.fg{margin-bottom:14px}
.fg label{display:block;font-size:11px;font-weight:600;color:var(--muted);margin-bottom:5px;text-transform:uppercase;letter-spacing:.5px}
.fg input,.fg select,.fg textarea{width:100%;background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:9px 12px;color:var(--text);font-size:13px;font-family:inherit;outline:none;transition:border-color .15s}
.fg input:focus,.fg select,.fg textarea:focus{border-color:var(--accent)}
.fg textarea{resize:vertical;min-height:80px}
.urlrow{display:flex;gap:8px}
.urlrow input{flex:1}
.fbtn{background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:9px 14px;color:var(--muted);font-size:12px;font-family:inherit;cursor:pointer;white-space:nowrap;transition:all .15s}
.fbtn:hover{border-color:var(--accent);color:var(--text)}.fbtn:disabled{opacity:.5;cursor:not-allowed}
.mfooter{padding:14px 22px;border-top:1px solid var(--border);display:flex;gap:10px;justify-content:flex-end;flex-shrink:0}
.btn2{background:none;border:1px solid var(--border);border-radius:8px;padding:8px 16px;color:var(--muted);font-size:13px;font-family:inherit;cursor:pointer;transition:all .15s}
.btn2:hover{border-color:var(--accent2);color:var(--text)}
.btn1{background:var(--accent);border:none;border-radius:8px;padding:8px 18px;color:#fff;font-size:13px;font-weight:600;font-family:inherit;cursor:pointer;transition:opacity .15s}
.btn1:hover{opacity:.85}
.hint{font-size:11px;color:var(--muted);margin-top:4px;line-height:1.4}
@media(max-width:680px){.sidebar{display:none}.msg.user{max-width:90%}.msg.agent{max-width:95%}}
</style>
</head>
<body>

<div class="sidebar">
  <div>
    <div class="logo"><div class="logo-icon">&#9889;</div><div>AI OS</div></div>
    <div class="biz-industry" id="biz-label">No context set</div>
  </div>
  <div>
    <div class="section-title">Agents</div>
    <div class="agent-row"><div class="dot d-s"></div><div><div>Sales</div><div class="agent-desc">Proposals &middot; Leads &middot; Pipeline</div></div></div>
    <div class="agent-row"><div class="dot d-o"></div><div><div>Operations</div><div class="agent-desc">Onboarding &middot; Reports &middot; KPIs</div></div></div>
    <div class="agent-row"><div class="dot d-m"></div><div><div>Marketing</div><div class="agent-desc">Content &middot; Campaigns &middot; Calendar</div></div></div>
  </div>
  <div>
    <div class="section-title">Quick Tasks</div>
    <button class="chip" onclick="fill(this)">Get pipeline summary for this month</button>
    <button class="chip" onclick="fill(this)">Generate executive weekly report &mdash; MRR, churn rate, NPS</button>
    <button class="chip" onclick="fill(this)">Create a proposal for Jane Smith at CloudOps Ltd &mdash; pain points: manual reporting, team coordination</button>
    <button class="chip" onclick="fill(this)">Onboard Alex Johnson at RetailFlow (alex@retailflow.com), 25-person team, standard plan</button>
    <button class="chip" onclick="fill(this)">Create a LinkedIn post about eliminating status meetings</button>
    <button class="chip" onclick="fill(this)">Flag customers at risk of churning &mdash; medium threshold</button>
  </div>
</div>

<div class="main">
  <div class="chat-header">
    <h1>AI Operating System</h1>
    <div class="header-right">
      <span class="live">Claude &middot; Live</span>
      <button class="gear-btn" onclick="openModal()">&#9881; Business Context</button>
    </div>
  </div>
  <div class="messages" id="msgs">
    <div class="welcome" id="welcome">
      <div class="welcome-icon">&#9889;</div>
      <h2>What can I help you with?</h2>
      <p>Type any sales, operations, or marketing task.<br>Click <strong>&#9881; Business Context</strong> to personalize outputs to your company.</p>
    </div>
  </div>
  <div class="input-wrap">
    <textarea id="inp" placeholder="Describe a task&hellip; (Enter to send, Shift+Enter for new line)" rows="1"
      onkeydown="onKey(event)" oninput="autosize(this)"></textarea>
    <button class="send" id="sendbtn" onclick="send()">Send &rarr;</button>
  </div>
</div>

<!-- Modal -->
<div id="overlay" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:200;align-items:center;justify-content:center">
  <div class="modal">
    <div class="modal-hdr">
      <h2>Business Context</h2>
      <button class="xbtn" onclick="closeModal()">&#215;</button>
    </div>
    <div class="tabs">
      <button class="tbtn on" id="tab-profile-btn" onclick="showTab('profile')">Company Profile</button>
      <button class="tbtn" id="tab-docs-btn" onclick="showTab('docs')">Documents &amp; Website</button>
    </div>
    <div class="mbody">
      <div class="panel on" id="panel-profile">
        <div class="fg"><label>Business Name</label><input id="f-name" type="text" placeholder="e.g. Acme Corp"></div>
        <div class="fg"><label>Industry</label><input id="f-industry" type="text" placeholder="e.g. B2B SaaS, E-commerce"></div>
        <div class="fg"><label>Description</label><textarea id="f-desc" placeholder="What does your company do?"></textarea></div>
        <div class="fg"><label>Brand Tone</label>
          <select id="f-tone">
            <option value="professional">Professional</option>
            <option value="friendly">Friendly &amp; Approachable</option>
            <option value="authoritative">Authoritative</option>
            <option value="conversational">Conversational</option>
            <option value="bold">Bold &amp; Direct</option>
          </select>
        </div>
        <div class="fg"><label>Target Customers</label><input id="f-target" type="text" placeholder="e.g. Mid-market SaaS companies, 50-500 employees"></div>
        <div class="fg"><label>Value Proposition</label><textarea id="f-value" placeholder="What unique value do you deliver?"></textarea></div>
      </div>
      <div class="panel" id="panel-docs">
        <div class="fg">
          <label>Fetch from Website URL</label>
          <div class="urlrow">
            <input id="f-url" type="url" placeholder="https://yourcompany.com/about">
            <button class="fbtn" id="fbtn" onclick="fetchUrl()">Fetch</button>
          </div>
          <div class="hint">Fetches the page text and appends it below.</div>
        </div>
        <div class="fg">
          <label>Documents / Notes</label>
          <textarea id="f-docs" style="min-height:180px" placeholder="Paste docs, case studies, FAQs, pitch decks&hellip; Agents will use this to personalize outputs."></textarea>
        </div>
      </div>
    </div>
    <div class="mfooter">
      <button class="btn2" onclick="clearCtx()">Clear All</button>
      <button class="btn1" onclick="saveCtx()">Save Context</button>
    </div>
  </div>
</div>

<script>
marked.setOptions({gfm:true, breaks:true});

var busy = false;
var CTX = 'ai_os_ctx';

function getCtx() {
  try { return JSON.parse(localStorage.getItem(CTX) || '{}'); } catch(e) { return {}; }
}

function saveCtx() {
  var c = {
    name: document.getElementById('f-name').value.trim(),
    industry: document.getElementById('f-industry').value.trim(),
    description: document.getElementById('f-desc').value.trim(),
    tone: document.getElementById('f-tone').value,
    target_customers: document.getElementById('f-target').value.trim(),
    value_proposition: document.getElementById('f-value').value.trim(),
    extra_context: document.getElementById('f-docs').value.trim()
  };
  localStorage.setItem(CTX, JSON.stringify(c));
  updateLabel();
  closeModal();
}

function clearCtx() {
  localStorage.removeItem(CTX);
  fillModal({});
  updateLabel();
}

function updateLabel() {
  var c = getCtx();
  document.getElementById('biz-label').textContent = c.name || c.industry || 'No context set';
}

function openModal() {
  fillModal(getCtx());
  showTab('profile');
  document.getElementById('overlay').style.display = 'flex';
}

function closeModal() {
  document.getElementById('overlay').style.display = 'none';
}

function fillModal(c) {
  document.getElementById('f-name').value = c.name || '';
  document.getElementById('f-industry').value = c.industry || '';
  document.getElementById('f-desc').value = c.description || '';
  document.getElementById('f-tone').value = c.tone || 'professional';
  document.getElementById('f-target').value = c.target_customers || '';
  document.getElementById('f-value').value = c.value_proposition || '';
  document.getElementById('f-docs').value = c.extra_context || '';
}

function showTab(name) {
  document.getElementById('panel-profile').className = 'panel' + (name === 'profile' ? ' on' : '');
  document.getElementById('panel-docs').className = 'panel' + (name === 'docs' ? ' on' : '');
  document.getElementById('tab-profile-btn').className = 'tbtn' + (name === 'profile' ? ' on' : '');
  document.getElementById('tab-docs-btn').className = 'tbtn' + (name === 'docs' ? ' on' : '');
}

document.getElementById('overlay').onclick = function(e) {
  if (e.target === this) closeModal();
};

function fill(el) {
  document.getElementById('inp').value = el.textContent.trim();
  document.getElementById('inp').focus();
}

function autosize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 180) + 'px';
}

function onKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function scrollBottom() {
  var c = document.getElementById('msgs');
  c.scrollTop = c.scrollHeight;
}

function addMsg(role, html, agent) {
  var w = document.getElementById('welcome');
  if (w) w.parentNode.removeChild(w);
  var c = document.getElementById('msgs');
  var d = document.createElement('div');
  d.className = 'msg ' + role;
  if (role === 'agent' && agent) {
    var t = document.createElement('div');
    t.className = 'agent-tag';
    t.innerHTML = '<span class="badge b-' + agent + '">' + agent + '</span> Agent';
    d.appendChild(t);
  }
  var b = document.createElement('div');
  b.className = 'bubble';
  b.innerHTML = role === 'agent' ? marked.parse(html) : escHtml(html);
  d.appendChild(b);
  c.appendChild(d);
  scrollBottom();
  return b;
}

function showTyping() {
  var c = document.getElementById('msgs');
  var d = document.createElement('div');
  d.id = 'typing'; d.className = 'msg agent';
  d.innerHTML = '<div class="typing-bubble"><span></span><span></span><span></span></div>';
  c.appendChild(d);
  scrollBottom();
}

function rmTyping() {
  var t = document.getElementById('typing');
  if (t) t.parentNode.removeChild(t);
}

async function fetchUrl() {
  var url = document.getElementById('f-url').value.trim();
  if (!url) { alert('Enter a URL first.'); return; }
  var btn = document.getElementById('fbtn');
  btn.disabled = true; btn.textContent = 'Fetching...';
  try {
    var r = await fetch('/api/fetch-website', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url: url})
    });
    var d = await r.json();
    if (d.error) { alert('Error: ' + d.error); return; }
    var ta = document.getElementById('f-docs');
    ta.value = (ta.value ? ta.value + '\\n\\n---\\n\\n' : '') + d.text;
  } catch(e) {
    alert('Fetch error: ' + e.message);
  } finally {
    btn.disabled = false; btn.textContent = 'Fetch';
  }
}

async function send() {
  if (busy) return;
  var inp = document.getElementById('inp');
  var task = inp.value.trim();
  if (!task) return;
  busy = true;
  document.getElementById('sendbtn').disabled = true;
  inp.value = ''; inp.style.height = 'auto';
  addMsg('user', task, null);
  showTyping();

  try {
    var r = await fetch('/api/run', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({task: task, context: getCtx()})
    });
    var d = await r.json();
    rmTyping();
    if (d.error) {
      addMsg('agent', '**Error:** ' + escHtml(d.error), null);
    } else {
      addMsg('agent', d.result, d.agent);
    }
  } catch(e) {
    rmTyping();
    addMsg('agent', '**Error:** ' + escHtml(e.message), null);
  } finally {
    busy = false;
    document.getElementById('sendbtn').disabled = false;
    document.getElementById('inp').focus();
  }
}

updateLabel();
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(HTML)


@app.post("/api/run")
async def run_task(request: Request):
    body = await request.json()
    task = (body.get("task") or "").strip()
    if not task:
        return JSONResponse({"error": "No task provided."}, status_code=400)
    if not os.getenv("ANTHROPIC_API_KEY"):
        return JSONResponse({"error": "ANTHROPIC_API_KEY not set on server."}, status_code=500)
    try:
        biz_ctx = body.get("context") or {}
        if any(biz_ctx.get(k) for k in ("name", "description", "industry", "extra_context")):
            profile = BusinessProfile.from_dict(biz_ctx)
        else:
            profile = get_yaml_profile()
        orch = build_orchestrator(profile)
        agent_name, refined_task = orch.route(task)
        result = orch._agents[agent_name].run(refined_task)
        return {"result": result, "agent": agent_name, "task": task}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.post("/api/fetch-website")
async def fetch_website(request: Request):
    body = await request.json()
    url = (body.get("url") or "").strip()
    if not url:
        return JSONResponse({"error": "No URL provided."}, status_code=400)
    try:
        import httpx, re
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return {"text": text[:4000], "url": url}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/api/stream")
async def stream_task(request: Request, task: str = "", context: str = "{}"):
    """SSE streaming endpoint — kept for future use."""
    if not task.strip():
        return JSONResponse({"error": "No task provided."}, status_code=400)
    if not os.getenv("ANTHROPIC_API_KEY"):
        return JSONResponse({"error": "ANTHROPIC_API_KEY not set."}, status_code=500)

    try:
        biz_ctx = json.loads(context)
    except Exception:
        biz_ctx = {}

    def generate():
        q = queue.Queue()

        def run():
            try:
                if any(biz_ctx.get(k) for k in ("name", "description", "industry", "extra_context")):
                    profile = BusinessProfile.from_dict(biz_ctx)
                else:
                    profile = get_yaml_profile()
                orch = build_orchestrator(profile)
                agent_name, refined_task = orch.route(task)
                q.put("data: " + json.dumps({"type": "agent", "agent": agent_name}) + "\n\n")
                for chunk in orch._agents[agent_name].run_stream(refined_task):
                    q.put("data: " + json.dumps({"type": "chunk", "text": chunk}) + "\n\n")
                q.put("data: " + json.dumps({"type": "done"}) + "\n\n")
            except Exception as exc:
                q.put("data: " + json.dumps({"type": "error", "text": str(exc)}) + "\n\n")
            finally:
                q.put(None)

        threading.Thread(target=run, daemon=True).start()
        while True:
            item = q.get()
            if item is None:
                break
            yield item

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": "claude-sonnet-4-6", "agents": ["sales", "operations", "marketing"]}


@app.get("/api/profile")
async def profile_info():
    p = get_yaml_profile()
    return {"name": p.name, "industry": p.industry, "channels": p.content_channels, "kpis": p.kpi_metrics}

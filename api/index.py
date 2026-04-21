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

_yaml_profile: BusinessProfile | None = None


def get_yaml_profile() -> BusinessProfile:
    global _yaml_profile
    if _yaml_profile is None:
        _yaml_profile = BusinessProfile.load(str(ROOT / "config" / "business_profile.yaml"))
    return _yaml_profile


def build_orchestrator(profile: BusinessProfile) -> Orchestrator:
    memory = Memory()
    orch = Orchestrator(profile, memory)
    orch.register_agent("sales", SalesAgent(profile, memory))
    orch.register_agent("operations", OperationsAgent(profile, memory))
    orch.register_agent("marketing", MarketingAgent(profile, memory))
    return orch


# ── HTML ──────────────────────────────────────────────────────────────────────

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI OS</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
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

/* Sidebar */
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

/* Main */
.main{flex:1;display:flex;flex-direction:column;min-width:0;overflow:hidden}
.chat-header{padding:14px 24px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;background:var(--surface);flex-shrink:0}
.chat-header h1{font-size:15px;font-weight:600}
.header-right{display:flex;align-items:center;gap:12px}
.live{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--ops)}
.live::before{content:'';display:block;width:6px;height:6px;border-radius:50%;background:var(--ops);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}

/* Gear button */
.gear-btn{background:none;border:1px solid var(--border);border-radius:8px;color:var(--muted);cursor:pointer;padding:6px 10px;font-size:13px;transition:all .15s;font-family:inherit}
.gear-btn:hover{border-color:var(--accent);color:var(--text)}
.ctx-badge{display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--ops);margin-left:4px;vertical-align:middle}

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

/* Markdown */
.bubble h2{font-size:15px;margin:10px 0 5px}.bubble h3{font-size:14px;margin:8px 0 4px}
.bubble p{margin:7px 0}.bubble ul,.bubble ol{padding-left:18px;margin:7px 0}.bubble li{margin:3px 0}
.bubble table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px}
.bubble th,.bubble td{border:1px solid var(--border);padding:6px 10px;text-align:left}
.bubble th{background:rgba(255,255,255,.05);font-weight:600}
.bubble code{background:rgba(255,255,255,.07);padding:1px 5px;border-radius:4px;font-family:monospace;font-size:12px}
.bubble pre{background:rgba(255,255,255,.05);padding:12px;border-radius:8px;overflow-x:auto;margin:8px 0}
.bubble pre code{background:transparent;padding:0}
.bubble blockquote{border-left:3px solid var(--accent);padding-left:12px;color:var(--muted);margin:8px 0}
.bubble strong{color:#fff}.bubble em{color:var(--accent2)}
.bubble a{color:var(--accent2);text-decoration:none}.bubble a:hover{text-decoration:underline}
.bubble hr{border:none;border-top:1px solid var(--border);margin:10px 0}

/* Modal */
.modal-backdrop{display:none;position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:100;align-items:center;justify-content:center}
.modal-backdrop.open{display:flex}
.modal{background:var(--surface);border:1px solid var(--border);border-radius:16px;width:560px;max-width:95vw;max-height:90vh;display:flex;flex-direction:column;overflow:hidden}
.modal-header{padding:20px 24px 16px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;flex-shrink:0}
.modal-header h2{font-size:16px;font-weight:700}
.close-btn{background:none;border:none;color:var(--muted);font-size:20px;cursor:pointer;line-height:1;padding:2px 6px;border-radius:4px}
.close-btn:hover{color:var(--text);background:var(--surface2)}
.modal-tabs{display:flex;border-bottom:1px solid var(--border);flex-shrink:0}
.tab-btn{flex:1;padding:11px;background:none;border:none;color:var(--muted);font-size:13px;font-family:inherit;cursor:pointer;border-bottom:2px solid transparent;transition:all .15s}
.tab-btn.active{color:var(--accent2);border-bottom-color:var(--accent)}
.tab-btn:hover:not(.active){color:var(--text)}
.modal-body{padding:20px 24px;overflow-y:auto;flex:1}
.tab-panel{display:none}.tab-panel.active{display:block}
.form-group{margin-bottom:14px}
.form-group label{display:block;font-size:12px;font-weight:600;color:var(--muted);margin-bottom:6px;text-transform:uppercase;letter-spacing:.5px}
.form-group input,.form-group textarea,.form-group select{width:100%;background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:9px 12px;color:var(--text);font-size:13px;font-family:inherit;outline:none;transition:border-color .15s}
.form-group input:focus,.form-group textarea:focus,.form-group select:focus{border-color:var(--accent)}
.form-group textarea{resize:vertical;min-height:90px}
.url-row{display:flex;gap:8px}
.url-row input{flex:1}
.fetch-btn{background:var(--surface2);border:1px solid var(--border);border-radius:8px;padding:9px 14px;color:var(--muted);font-size:12px;font-family:inherit;cursor:pointer;white-space:nowrap;transition:all .15s}
.fetch-btn:hover{border-color:var(--accent);color:var(--text)}.fetch-btn:disabled{opacity:.5;cursor:not-allowed}
.modal-footer{padding:16px 24px;border-top:1px solid var(--border);display:flex;gap:10px;justify-content:flex-end;flex-shrink:0}
.btn-secondary{background:none;border:1px solid var(--border);border-radius:8px;padding:9px 18px;color:var(--muted);font-size:13px;font-family:inherit;cursor:pointer;transition:all .15s}
.btn-secondary:hover{border-color:var(--accent2);color:var(--text)}
.btn-primary{background:var(--accent);border:none;border-radius:8px;padding:9px 20px;color:#fff;font-size:13px;font-weight:600;font-family:inherit;cursor:pointer;transition:opacity .15s}
.btn-primary:hover{opacity:.85}
.hint{font-size:11px;color:var(--muted);margin-top:5px;line-height:1.4}

@media(max-width:680px){.sidebar{display:none}.msg.user{max-width:90%}.msg.agent{max-width:95%}}
</style>
</head>
<body>

<div class="sidebar">
  <div>
    <div class="logo">
      <div class="logo-icon">⚡</div>
      <div><div>AI OS</div></div>
    </div>
    <div class="biz-industry" id="sidebar-industry">Loading...</div>
  </div>
  <div>
    <div class="section-title">Agents</div>
    <div class="agent-row"><div class="dot d-s"></div><div><div>Sales</div><div class="agent-desc">Proposals · Leads · Pipeline</div></div></div>
    <div class="agent-row"><div class="dot d-o"></div><div><div>Operations</div><div class="agent-desc">Onboarding · Reports · KPIs</div></div></div>
    <div class="agent-row"><div class="dot d-m"></div><div><div>Marketing</div><div class="agent-desc">Content · Campaigns · Calendar</div></div></div>
  </div>
  <div>
    <div class="section-title">Quick Tasks</div>
    <button class="chip" onclick="fill(this)">Get pipeline summary for this month</button>
    <button class="chip" onclick="fill(this)">Generate executive weekly report — MRR, churn rate, NPS</button>
    <button class="chip" onclick="fill(this)">Create a proposal for Jane Smith at CloudOps Ltd — pain points: manual reporting, team coordination</button>
    <button class="chip" onclick="fill(this)">Onboard Alex Johnson at RetailFlow (alex@retailflow.com), 25-person team, standard plan</button>
    <button class="chip" onclick="fill(this)">Create a LinkedIn post about eliminating status meetings with project visibility tools</button>
    <button class="chip" onclick="fill(this)">Flag customers at risk of churning — medium threshold</button>
  </div>
</div>

<div class="main">
  <div class="chat-header">
    <h1>AI Operating System</h1>
    <div class="header-right">
      <span class="live">Claude Live</span>
      <button class="gear-btn" onclick="openModal()">⚙ Business Context<span id="ctx-dot" class="ctx-badge" style="display:none"></span></button>
    </div>
  </div>
  <div class="messages" id="msgs">
    <div class="welcome" id="welcome">
      <div class="welcome-icon">⚡</div>
      <h2>What can I help you with?</h2>
      <p>Type any sales, operations, or marketing task in plain English.<br>Set your business context (⚙ button) so agents personalize every output to your company.</p>
    </div>
  </div>
  <div class="input-wrap">
    <textarea id="inp" placeholder="Describe a task… (Enter to send, Shift+Enter for new line)" rows="1"
      onkeydown="onKey(event)" oninput="resize(this)"></textarea>
    <button class="send" id="btn" onclick="send()">Send →</button>
  </div>
</div>

<!-- Business Context Modal -->
<div class="modal-backdrop" id="modal">
  <div class="modal">
    <div class="modal-header">
      <h2>Business Context</h2>
      <button class="close-btn" onclick="closeModal()">×</button>
    </div>
    <div class="modal-tabs">
      <button class="tab-btn active" onclick="switchTab('profile',this)">Company Profile</button>
      <button class="tab-btn" onclick="switchTab('docs',this)">Documents & Website</button>
    </div>
    <div class="modal-body">
      <div class="tab-panel active" id="tab-profile">
        <div class="form-group">
          <label>Business Name</label>
          <input id="f-name" type="text" placeholder="e.g. Acme Corp">
        </div>
        <div class="form-group">
          <label>Industry</label>
          <input id="f-industry" type="text" placeholder="e.g. B2B SaaS, E-commerce, Consulting">
        </div>
        <div class="form-group">
          <label>Description</label>
          <textarea id="f-description" placeholder="What does your company do?"></textarea>
        </div>
        <div class="form-group">
          <label>Brand Tone</label>
          <select id="f-tone">
            <option value="professional">Professional</option>
            <option value="friendly">Friendly & Approachable</option>
            <option value="authoritative">Authoritative</option>
            <option value="conversational">Conversational</option>
            <option value="bold">Bold & Direct</option>
          </select>
        </div>
        <div class="form-group">
          <label>Target Customers</label>
          <input id="f-target" type="text" placeholder="e.g. Mid-market SaaS companies, 50-500 employees">
        </div>
        <div class="form-group">
          <label>Value Proposition</label>
          <textarea id="f-value" placeholder="What unique value do you deliver?"></textarea>
        </div>
      </div>

      <div class="tab-panel" id="tab-docs">
        <div class="form-group">
          <label>Fetch from Website URL</label>
          <div class="url-row">
            <input id="f-url" type="url" placeholder="https://yourcompany.com/about">
            <button class="fetch-btn" id="fetch-btn" onclick="fetchUrl()">Fetch</button>
          </div>
          <div class="hint">Fetches the page text and appends it to the context below.</div>
        </div>
        <div class="form-group">
          <label>Paste Documents / Notes</label>
          <textarea id="f-docs" style="min-height:200px" placeholder="Paste any documents, case studies, product descriptions, FAQs, pitch decks, or other context here. Agents will use this to personalize all outputs."></textarea>
        </div>
      </div>
    </div>
    <div class="modal-footer">
      <button class="btn-secondary" onclick="clearContext()">Clear All</button>
      <button class="btn-primary" onclick="saveContext()">Save Context</button>
    </div>
  </div>
</div>

<script>
marked.setOptions({gfm:true,breaks:true});
let busy=false;

// ── Business context ──────────────────────────────────────────────────────────
const CTX_KEY='ai_os_biz_context';

function getBizContext(){
  try{ return JSON.parse(localStorage.getItem(CTX_KEY)||'{}'); }catch(e){ return {}; }
}

function loadContextIntoModal(){
  const c=getBizContext();
  document.getElementById('f-name').value=c.name||'';
  document.getElementById('f-industry').value=c.industry||'';
  document.getElementById('f-description').value=c.description||'';
  document.getElementById('f-tone').value=c.tone||'professional';
  document.getElementById('f-target').value=c.target_customers||'';
  document.getElementById('f-value').value=c.value_proposition||'';
  document.getElementById('f-docs').value=c.extra_context||'';
}

function saveContext(){
  const c={
    name:document.getElementById('f-name').value.trim(),
    industry:document.getElementById('f-industry').value.trim(),
    description:document.getElementById('f-description').value.trim(),
    tone:document.getElementById('f-tone').value,
    target_customers:document.getElementById('f-target').value.trim(),
    value_proposition:document.getElementById('f-value').value.trim(),
    extra_context:document.getElementById('f-docs').value.trim(),
  };
  localStorage.setItem(CTX_KEY,JSON.stringify(c));
  updateSidebarName();
  updateCtxBadge();
  closeModal();
}

function clearContext(){
  localStorage.removeItem(CTX_KEY);
  loadContextIntoModal();
  updateSidebarName();
  updateCtxBadge();
}

function updateSidebarName(){
  const c=getBizContext();
  document.getElementById('sidebar-industry').textContent=c.industry||c.name||'No business context set';
}

function updateCtxBadge(){
  const c=getBizContext();
  const has=!!(c.name||c.description||c.extra_context);
  document.getElementById('ctx-dot').style.display=has?'':'none';
}

// ── Modal ─────────────────────────────────────────────────────────────────────
function openModal(){ loadContextIntoModal(); document.getElementById('modal').classList.add('open'); }
function closeModal(){ document.getElementById('modal').classList.remove('open'); }
document.getElementById('modal').addEventListener('click',function(e){ if(e.target===this)closeModal(); });

function switchTab(id,btn){
  document.querySelectorAll('.tab-panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById('tab-'+id).classList.add('active');
  btn.classList.add('active');
}

async function fetchUrl(){
  const url=document.getElementById('f-url').value.trim();
  if(!url){alert('Enter a URL first.');return;}
  const btn=document.getElementById('fetch-btn');
  btn.disabled=true;btn.textContent='Fetching...';
  try{
    const r=await fetch('/api/fetch-website',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url})});
    const d=await r.json();
    if(d.error){alert('Fetch failed: '+d.error);return;}
    const ta=document.getElementById('f-docs');
    ta.value=(ta.value?ta.value+'\n\n---\n\n':'')+d.text;
  }catch(e){alert('Fetch error: '+e.message);}
  finally{btn.disabled=false;btn.textContent='Fetch';}
}

// ── Chat ──────────────────────────────────────────────────────────────────────
function fill(el){ document.getElementById('inp').value=el.textContent.trim(); document.getElementById('inp').focus(); }
function resize(el){ el.style.height='auto'; el.style.height=Math.min(el.scrollHeight,180)+'px'; }
function onKey(e){ if(e.key==='Enter'&&!e.shiftKey){e.preventDefault();send();} }

function scrollBottom(){ const c=document.getElementById('msgs'); c.scrollTop=c.scrollHeight; }

function addMsg(role,html,agent){
  const w=document.getElementById('welcome');if(w)w.remove();
  const c=document.getElementById('msgs');
  const d=document.createElement('div');d.className='msg '+role;
  if(role==='agent'&&agent){
    const t=document.createElement('div');t.className='agent-tag';
    t.innerHTML=`<span class="badge b-${agent}">${agent}</span> Agent`;
    d.appendChild(t);
  }
  const b=document.createElement('div');b.className='bubble';
  b.innerHTML=role==='agent'?marked.parse(html):escHtml(html);
  d.appendChild(b);c.appendChild(d);scrollBottom();
  return b;
}

function escHtml(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function showTyping(){
  const c=document.getElementById('msgs');
  const d=document.createElement('div');d.id='typing';d.className='msg agent';
  d.innerHTML='<div class="typing-bubble"><span></span><span></span><span></span></div>';
  c.appendChild(d);scrollBottom();
}
function rmTyping(){ const t=document.getElementById('typing');if(t)t.remove(); }

async function send(){
  if(busy)return;
  const inp=document.getElementById('inp');
  const task=inp.value.trim();if(!task)return;
  busy=true;document.getElementById('btn').disabled=true;
  inp.value='';inp.style.height='auto';
  addMsg('user',task);showTyping();

  const ctx=JSON.stringify(getBizContext());
  const url='/api/stream?task='+encodeURIComponent(task)+'&context='+encodeURIComponent(ctx);
  const es=new EventSource(url);
  let bubble=null;let agentName=null;let fullText='';

  es.onmessage=function(e){
    let msg;try{msg=JSON.parse(e.data);}catch{return;}
    if(msg.type==='agent'){
      agentName=msg.agent;rmTyping();
      const w=document.getElementById('welcome');if(w)w.remove();
      const c=document.getElementById('msgs');
      const d=document.createElement('div');d.className='msg agent';
      const tag=document.createElement('div');tag.className='agent-tag';
      tag.innerHTML=`<span class="badge b-${agentName}">${agentName}</span> Agent`;
      d.appendChild(tag);
      bubble=document.createElement('div');bubble.className='bubble';bubble.textContent='...';
      d.appendChild(bubble);c.appendChild(d);scrollBottom();
    } else if(msg.type==='chunk'){
      fullText+=msg.text;
      if(bubble){bubble.innerHTML=marked.parse(fullText);scrollBottom();}
    } else if(msg.type==='done'){
      es.close();busy=false;document.getElementById('btn').disabled=false;
      document.getElementById('inp').focus();
    } else if(msg.type==='error'){
      rmTyping();es.close();
      if(bubble){bubble.innerHTML=marked.parse('**Error:** '+escHtml(msg.text));}
      else addMsg('agent','**Error:** '+escHtml(msg.text),null);
      busy=false;document.getElementById('btn').disabled=false;
    }
  };

  es.onerror=function(){
    es.close();rmTyping();
    if(!bubble)addMsg('agent','**Connection error.** Check server logs.',null);
    busy=false;document.getElementById('btn').disabled=false;
  };
}

// Init
updateSidebarName();updateCtxBadge();
</script>
</body>
</html>"""


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(HTML)


@app.get("/api/stream")
async def stream_task(request: Request, task: str = "", context: str = "{}"):
    if not task.strip():
        return JSONResponse({"error": "No task provided."}, status_code=400)

    if not os.getenv("ANTHROPIC_API_KEY"):
        return JSONResponse({"error": "ANTHROPIC_API_KEY not configured."}, status_code=500)

    try:
        biz_ctx = json.loads(context)
    except Exception:
        biz_ctx = {}

    def generate():
        q: queue.Queue = queue.Queue()

        def run():
            try:
                if any(biz_ctx.get(k) for k in ("name", "description", "industry", "extra_context")):
                    profile = BusinessProfile.from_dict(biz_ctx)
                else:
                    profile = get_yaml_profile()

                orch = build_orchestrator(profile)
                agent_name, refined_task = orch.route(task)

                q.put(f"data: {json.dumps({'type': 'agent', 'agent': agent_name})}\n\n")

                for chunk in orch._agents[agent_name].run_stream(refined_task):
                    q.put(f"data: {json.dumps({'type': 'chunk', 'text': chunk})}\n\n")

                q.put(f"data: {json.dumps({'type': 'done'})}\n\n")
            except Exception as exc:
                q.put(f"data: {json.dumps({'type': 'error', 'text': str(exc)})}\n\n")
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


@app.post("/api/fetch-website")
async def fetch_website(request: Request):
    body = await request.json()
    url = (body.get("url") or "").strip()
    if not url:
        return JSONResponse({"error": "No URL provided."}, status_code=400)
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
        # Strip HTML tags crudely
        import re
        text = re.sub(r"<[^>]+>", " ", resp.text)
        text = re.sub(r"\s+", " ", text).strip()
        return {"text": text[:4000], "url": url}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.post("/api/run")
async def run_task(request: Request):
    """Non-streaming fallback."""
    body = await request.json()
    task = (body.get("task") or "").strip()
    if not task:
        return JSONResponse({"error": "No task provided."}, status_code=400)
    if not os.getenv("ANTHROPIC_API_KEY"):
        return JSONResponse({"error": "ANTHROPIC_API_KEY not configured."}, status_code=500)
    try:
        biz_ctx = body.get("context", {})
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


@app.get("/api/health")
async def health():
    return {"status": "ok", "model": "claude-sonnet-4-6", "agents": ["sales", "operations", "marketing"]}


@app.get("/api/profile")
async def profile_info():
    p = get_yaml_profile()
    return {"name": p.name, "industry": p.industry, "channels": p.content_channels, "kpis": p.kpi_metrics}

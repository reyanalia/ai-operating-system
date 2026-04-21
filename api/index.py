import os
import sys
from pathlib import Path

# Add project root to path so all modules resolve on Vercel
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from core.business_profile import BusinessProfile
from core.memory import Memory
from core.orchestrator import Orchestrator
from agents.sales_agent import SalesAgent
from agents.operations_agent import OperationsAgent
from agents.marketing_agent import MarketingAgent

app = FastAPI(title="AI Operating System")

# Load profile once per cold-start
_profile: BusinessProfile | None = None

def get_profile() -> BusinessProfile:
    global _profile
    if _profile is None:
        _profile = BusinessProfile.load(str(ROOT / "config" / "business_profile.yaml"))
    return _profile


def build_orchestrator() -> Orchestrator:
    profile = get_profile()
    memory = Memory()
    sales = SalesAgent(profile, memory)
    ops = OperationsAgent(profile, memory)
    marketing = MarketingAgent(profile, memory)
    orch = Orchestrator(profile, memory)
    orch.register_agent("sales", sales)
    orch.register_agent("operations", ops)
    orch.register_agent("marketing", marketing)
    return orch


# ── HTML UI (embedded to avoid static-file complexity on Vercel) ──────────────

def get_html(business_name: str, industry: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AI OS — {business_name}</title>
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --bg:#0d0d0f;--surface:#16161a;--surface2:#1e1e24;
  --border:#2a2a35;--text:#e4e4ef;--muted:#6b7280;
  --accent:#6366f1;--accent2:#818cf8;
  --sales:#3b82f6;--ops:#10b981;--mktg:#a855f7;
  --user:#1e3a5f;
}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:var(--bg);color:var(--text);height:100vh;display:flex;overflow:hidden}}

/* Sidebar */
.sidebar{{width:270px;min-width:270px;background:var(--surface);border-right:1px solid var(--border);display:flex;flex-direction:column;padding:20px 16px;gap:20px;overflow-y:auto}}
.logo{{display:flex;align-items:center;gap:8px;font-size:17px;font-weight:700}}
.logo-icon{{width:32px;height:32px;background:var(--accent);border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px}}
.biz-name{{font-size:12px;color:var(--muted);margin-top:2px}}
.biz-industry{{font-size:11px;color:var(--accent2);text-transform:uppercase;letter-spacing:.5px}}

.section-title{{font-size:10px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:8px;font-weight:600}}

.agent-row{{display:flex;align-items:center;gap:8px;padding:8px 10px;border-radius:8px;font-size:13px;background:var(--surface2);margin-bottom:4px}}
.dot{{width:7px;height:7px;border-radius:50%;flex-shrink:0}}
.d-s{{background:var(--sales)}}.d-o{{background:var(--ops)}}.d-m{{background:var(--mktg)}}
.agent-desc{{font-size:11px;color:var(--muted);margin-top:1px}}

.chip{{display:block;width:100%;text-align:left;padding:8px 10px;background:var(--surface2);border:1px solid var(--border);border-radius:8px;color:var(--muted);font-size:12px;cursor:pointer;margin-bottom:4px;transition:all .15s;font-family:inherit;line-height:1.4}}
.chip:hover{{border-color:var(--accent);color:var(--text);background:rgba(99,102,241,.08)}}

/* Main */
.main{{flex:1;display:flex;flex-direction:column;min-width:0;overflow:hidden}}
.chat-header{{padding:14px 24px;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;background:var(--surface);flex-shrink:0}}
.chat-header h1{{font-size:15px;font-weight:600}}
.live{{display:inline-flex;align-items:center;gap:5px;font-size:12px;color:var(--ops)}}
.live::before{{content:'';display:block;width:6px;height:6px;border-radius:50%;background:var(--ops);animation:pulse 2s infinite}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}

.messages{{flex:1;overflow-y:auto;padding:24px;display:flex;flex-direction:column;gap:16px}}
.messages::-webkit-scrollbar{{width:4px}}
.messages::-webkit-scrollbar-track{{background:transparent}}
.messages::-webkit-scrollbar-thumb{{background:var(--border);border-radius:2px}}

/* Welcome */
.welcome{{margin:auto;text-align:center;max-width:400px}}
.welcome-icon{{font-size:40px;margin-bottom:16px}}
.welcome h2{{font-size:22px;font-weight:700;margin-bottom:8px}}
.welcome p{{font-size:14px;color:var(--muted);line-height:1.6}}

/* Messages */
.msg{{display:flex;flex-direction:column;gap:5px}}
.msg.user{{align-self:flex-end;max-width:75%}}
.msg.agent{{align-self:flex-start;max-width:85%}}
.bubble{{padding:12px 16px;border-radius:16px;font-size:14px;line-height:1.65}}
.msg.user .bubble{{background:var(--user);color:#fff;border-bottom-right-radius:4px}}
.msg.agent .bubble{{background:var(--surface);border-bottom-left-radius:4px;border:1px solid var(--border)}}
.agent-tag{{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--muted)}}
.badge{{padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px}}
.b-sales{{background:rgba(59,130,246,.15);color:var(--sales)}}
.b-operations{{background:rgba(16,185,129,.15);color:var(--ops)}}
.b-marketing{{background:rgba(168,85,247,.15);color:var(--mktg)}}

/* Typing */
.typing-bubble{{display:flex;gap:4px;align-items:center;padding:14px 18px;background:var(--surface);border-radius:16px;border-bottom-left-radius:4px;border:1px solid var(--border)}}
.typing-bubble span{{width:6px;height:6px;border-radius:50%;background:var(--muted);animation:bop 1.2s infinite}}
.typing-bubble span:nth-child(2){{animation-delay:.2s}}
.typing-bubble span:nth-child(3){{animation-delay:.4s}}
@keyframes bop{{0%,80%,100%{{transform:translateY(0)}}40%{{transform:translateY(-5px)}}}}

/* Input */
.input-wrap{{padding:16px 24px;border-top:1px solid var(--border);display:flex;gap:10px;background:var(--surface);flex-shrink:0}}
textarea{{flex:1;background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:11px 14px;color:var(--text);font-size:14px;font-family:inherit;resize:none;outline:none;line-height:1.5;min-height:46px;max-height:180px;transition:border-color .15s}}
textarea:focus{{border-color:var(--accent)}}
textarea::placeholder{{color:var(--muted)}}
.send{{background:var(--accent);border:none;border-radius:12px;padding:11px 20px;color:#fff;font-size:13px;font-weight:600;cursor:pointer;transition:opacity .15s;align-self:flex-end;font-family:inherit;white-space:nowrap}}
.send:hover{{opacity:.85}}.send:disabled{{opacity:.4;cursor:not-allowed}}

/* Markdown */
.bubble h1,.bubble h2,.bubble h3{{margin:10px 0 5px;line-height:1.3}}
.bubble h2{{font-size:15px}}.bubble h3{{font-size:14px}}
.bubble p{{margin:7px 0}}
.bubble ul,.bubble ol{{padding-left:18px;margin:7px 0}}
.bubble li{{margin:3px 0}}
.bubble table{{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px}}
.bubble th,.bubble td{{border:1px solid var(--border);padding:6px 10px;text-align:left}}
.bubble th{{background:rgba(255,255,255,.05);font-weight:600}}
.bubble code{{background:rgba(255,255,255,.07);padding:1px 5px;border-radius:4px;font-family:monospace;font-size:12px}}
.bubble pre{{background:rgba(255,255,255,.05);padding:12px;border-radius:8px;overflow-x:auto;margin:8px 0}}
.bubble pre code{{background:transparent;padding:0}}
.bubble blockquote{{border-left:3px solid var(--accent);padding-left:12px;color:var(--muted);margin:8px 0;font-style:italic}}
.bubble hr{{border:none;border-top:1px solid var(--border);margin:10px 0}}
.bubble strong{{color:#fff}}
.bubble em{{color:var(--accent2)}}
.bubble a{{color:var(--accent2);text-decoration:none}}
.bubble a:hover{{text-decoration:underline}}

@media(max-width:680px){{
  .sidebar{{display:none}}
  .msg.user{{max-width:90%}}.msg.agent{{max-width:95%}}
}}
</style>
</head>
<body>

<div class="sidebar">
  <div>
    <div class="logo">
      <div class="logo-icon">⚡</div>
      <div>
        <div>AI OS</div>
        <div class="biz-name">{business_name}</div>
      </div>
    </div>
    <div class="biz-industry" style="margin-top:10px;padding-left:4px">{industry}</div>
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
    <button class="chip" onclick="fill(this)">Build a content calendar for this month across LinkedIn and email</button>
    <button class="chip" onclick="fill(this)">Repurpose this for LinkedIn, Twitter, and email: We helped 50 operations teams eliminate weekly status meetings by centralizing project visibility in 30 days</button>
  </div>
</div>

<div class="main">
  <div class="chat-header">
    <h1>AI Operating System</h1>
    <span class="live">Claude claude-sonnet-4-6 · Live</span>
  </div>
  <div class="messages" id="msgs">
    <div class="welcome" id="welcome">
      <div class="welcome-icon">⚡</div>
      <h2>What can I help you with?</h2>
      <p>Type any sales, operations, or marketing task in plain English.<br>I'll route it to the right specialist agent automatically.</p>
    </div>
  </div>
  <div class="input-wrap">
    <textarea id="inp" placeholder="Describe a task… (Enter to send, Shift+Enter for new line)" rows="1"
      onkeydown="onKey(event)" oninput="resize(this)"></textarea>
    <button class="send" id="btn" onclick="send()">Send →</button>
  </div>
</div>

<script>
marked.setOptions({{gfm:true,breaks:true}});
let busy=false;

function fill(el){{
  document.getElementById('inp').value=el.textContent.trim();
  document.getElementById('inp').focus();
}}

function resize(el){{
  el.style.height='auto';
  el.style.height=Math.min(el.scrollHeight,180)+'px';
}}

function onKey(e){{
  if(e.key==='Enter'&&!e.shiftKey){{e.preventDefault();send();}}
}}

function addMsg(role,html,agent){{
  const w=document.getElementById('welcome');if(w)w.remove();
  const c=document.getElementById('msgs');
  const d=document.createElement('div');
  d.className='msg '+role;
  if(role==='agent'&&agent){{
    const t=document.createElement('div');
    t.className='agent-tag';
    t.innerHTML=`<span class="badge b-${{agent}}">${{agent}}</span> Agent`;
    d.appendChild(t);
  }}
  const b=document.createElement('div');
  b.className='bubble';
  b.innerHTML=role==='agent'?marked.parse(html):escHtml(html);
  d.appendChild(b);
  c.appendChild(d);
  c.scrollTop=c.scrollHeight;
}}

function escHtml(s){{
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}}

function showTyping(){{
  const c=document.getElementById('msgs');
  const d=document.createElement('div');
  d.id='typing';d.className='msg agent';
  d.innerHTML='<div class="typing-bubble"><span></span><span></span><span></span></div>';
  c.appendChild(d);c.scrollTop=c.scrollHeight;
}}
function rmTyping(){{const t=document.getElementById('typing');if(t)t.remove();}}

async function send(){{
  if(busy)return;
  const inp=document.getElementById('inp');
  const task=inp.value.trim();
  if(!task)return;
  busy=true;
  document.getElementById('btn').disabled=true;
  inp.value='';inp.style.height='auto';
  addMsg('user',task);
  showTyping();
  try{{
    const r=await fetch('/api/run',{{
      method:'POST',
      headers:{{'Content-Type':'application/json'}},
      body:JSON.stringify({{task}})
    }});
    const d=await r.json();
    rmTyping();
    if(d.error)addMsg('agent','**Error:** '+d.error,null);
    else addMsg('agent',d.result,d.agent);
  }}catch(e){{
    rmTyping();
    addMsg('agent','**Connection error:** '+e.message,null);
  }}
  busy=false;
  document.getElementById('btn').disabled=false;
  inp.focus();
}}
</script>
</body>
</html>"""


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index():
    profile = get_profile()
    return HTMLResponse(get_html(profile.name, profile.industry))


@app.post("/api/run")
async def run_task(request: Request):
    body = await request.json()
    task = (body.get("task") or "").strip()
    if not task:
        return JSONResponse({"error": "No task provided."}, status_code=400)

    if not os.getenv("ANTHROPIC_API_KEY"):
        return JSONResponse(
            {"error": "ANTHROPIC_API_KEY is not configured on the server."},
            status_code=500,
        )

    try:
        orch = build_orchestrator()
        agent_name, refined_task = orch.route(task)
        result = orch._agents[agent_name].run(refined_task)
        orch.memory.append_history(
            {"original_task": task, "routed_to": agent_name, "refined_task": refined_task}
        )
        return {"result": result, "agent": agent_name, "task": task}
    except Exception as exc:
        return JSONResponse({"error": str(exc)}, status_code=500)


@app.get("/api/health")
async def health():
    profile = get_profile()
    return {
        "status": "ok",
        "business": profile.name,
        "model": "claude-sonnet-4-6",
        "agents": ["sales", "operations", "marketing"],
    }


@app.get("/api/profile")
async def profile_info():
    p = get_profile()
    return {
        "name": p.name,
        "industry": p.industry,
        "channels": p.content_channels,
        "kpis": p.kpi_metrics,
        "crm": p.crm_tool,
    }

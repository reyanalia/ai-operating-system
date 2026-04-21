"""
AI Operating System — Entry Point

Usage:
    python main.py              # Interactive REPL mode
    python main.py demo         # Run built-in capability demonstrations
    python main.py --profile config/my_business.yaml   # Use custom business profile
"""

import os
import sys
import io
from pathlib import Path

# Force UTF-8 output on Windows to handle emoji/unicode in agent responses
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()

# Add project root to path so imports resolve regardless of CWD
sys.path.insert(0, str(Path(__file__).parent))

from core.business_profile import BusinessProfile
from core.memory import Memory
from core.orchestrator import Orchestrator
from agents.sales_agent import SalesAgent
from agents.operations_agent import OperationsAgent
from agents.marketing_agent import MarketingAgent
from workflows.proposal_workflow import ProposalWorkflow
from workflows.lead_workflow import LeadWorkflow
from workflows.onboarding_workflow import OnboardingWorkflow
from workflows.reporting_workflow import ReportingWorkflow
from workflows.content_workflow import ContentWorkflow

console = Console()


# ── Bootstrap ──────────────────────────────────────────────────────────────────

def build_ai_os(profile_path: str = "config/business_profile.yaml") -> dict:
    """Initialise the full AI OS: profile → agents → orchestrator → workflows."""
    profile = BusinessProfile.load(profile_path)
    memory = Memory()

    sales = SalesAgent(profile, memory)
    ops = OperationsAgent(profile, memory)
    marketing = MarketingAgent(profile, memory)

    orchestrator = Orchestrator(profile, memory)
    orchestrator.register_agent("sales", sales)
    orchestrator.register_agent("operations", ops)
    orchestrator.register_agent("marketing", marketing)

    workflows = {
        "proposal": ProposalWorkflow(orchestrator, memory),
        "lead": LeadWorkflow(orchestrator, memory),
        "onboarding": OnboardingWorkflow(orchestrator, memory),
        "reporting": ReportingWorkflow(orchestrator, memory),
        "content": ContentWorkflow(orchestrator, memory),
    }

    return {
        "orchestrator": orchestrator,
        "workflows": workflows,
        "profile": profile,
        "memory": memory,
    }


# ── Demo mode ──────────────────────────────────────────────────────────────────

DEMO_TASKS = [
    (
        "Sales — Pipeline Overview",
        "Search for all qualified leads in our CRM and give me a summary of the current pipeline for this month.",
    ),
    (
        "Sales — Proposal Creation",
        "Create a professional-tier proposal for Jane Smith at CloudOps Ltd. "
        "Their pain points are manual reporting and cross-team coordination issues.",
    ),
    (
        "Marketing — Content Repurposing",
        "Repurpose this for LinkedIn, Twitter, and email: "
        "'We helped 50 operations teams eliminate their weekly status meetings by "
        "centralizing project visibility. Here is how they did it in 30 days.'",
    ),
    (
        "Operations — Weekly Report",
        "Generate an executive weekly report covering MRR, churn_rate, NPS, and active_users.",
    ),
    (
        "Operations — Customer Onboarding",
        "Create a standard onboarding plan for Alex Johnson at RetailFlow "
        "(alex@retailflow.com). They have a 25-person team and want to reduce "
        "project tracking overhead and manual status updates.",
    ),
]


def demo_mode(ai_os: dict) -> None:
    profile = ai_os["profile"]
    orchestrator = ai_os["orchestrator"]

    console.print(
        Panel.fit(
            f"[bold cyan]AI OPERATING SYSTEM[/bold cyan]  •  [dim]Demo Mode[/dim]\n"
            f"[green]{profile.name}[/green]  |  [dim]{profile.industry}[/dim]\n"
            f"[dim]Powered by Claude claude-sonnet-4-6 with prompt caching[/dim]",
            border_style="cyan",
        )
    )

    for i, (title, task) in enumerate(DEMO_TASKS, 1):
        console.print(f"\n[bold yellow]{'─' * 60}[/bold yellow]")
        console.print(f"[bold yellow]Demo {i}/{len(DEMO_TASKS)}: {title}[/bold yellow]")
        console.print(f"[dim]▶ {task[:90]}{'…' if len(task) > 90 else ''}[/dim]\n")

        try:
            with console.status("[bold cyan]Agent working…[/bold cyan]"):
                result = orchestrator.run(task)
            preview = result[:900] + ("…" if len(result) > 900 else "")
            console.print(f"[green]✓ Result:[/green]\n{preview}")
        except Exception as exc:
            console.print(f"[red]✗ Error: {exc}[/red]")

    console.print(f"\n[bold cyan]{'─' * 60}[/bold cyan]")
    console.print("[green]Demo complete.[/green] Run [bold]python main.py[/bold] for interactive mode.")


# ── Interactive mode ───────────────────────────────────────────────────────────

def interactive_mode(ai_os: dict) -> None:
    profile = ai_os["profile"]
    orchestrator = ai_os["orchestrator"]
    memory = ai_os["memory"]

    console.print(
        Panel.fit(
            f"[bold cyan]AI OPERATING SYSTEM[/bold cyan]  •  [dim]Interactive Mode[/dim]\n"
            f"[green]{profile.name}[/green]  |  [dim]{profile.industry}[/dim]\n"
            "[dim]Type a task in plain English. Type 'help' for examples, 'exit' to quit.[/dim]",
            border_style="cyan",
        )
    )

    while True:
        try:
            user_input = console.input("\n[bold green]AI OS >[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Shutting down AI OS.[/dim]")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit", "q"):
            console.print("[dim]Shutting down AI OS.[/dim]")
            break
        if user_input.lower() == "help":
            _show_help()
            continue
        if user_input.lower() == "memory":
            snap = memory.snapshot()
            if snap:
                console.print_json(data=snap)
            else:
                console.print("[dim]Memory is empty.[/dim]")
            continue
        if user_input.lower() == "history":
            history = memory.get_history(20)
            for entry in history:
                console.print(
                    f"[dim]{entry.get('timestamp', '')}[/dim] "
                    f"[cyan]{entry.get('routed_to', '?')}[/cyan] — "
                    f"{entry.get('original_task', '')[:80]}"
                )
            continue

        try:
            with console.status("[bold cyan]Routing and executing…[/bold cyan]"):
                result = orchestrator.run(user_input)
            console.print(f"\n[green]✓[/green] {result}")
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Enter 'exit' to quit.[/dim]")
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")


def _show_help() -> None:
    table = Table(title="AI OS — Example Tasks", show_lines=True)
    table.add_column("Agent", style="cyan", width=14)
    table.add_column("Example Task", style="white")

    rows = [
        ("Sales", "Create a proposal for [Name] at [Company] — their pain points are [X, Y]"),
        ("Sales", "Search for all qualified leads in our pipeline"),
        ("Sales", "Score and qualify this lead: [company details]"),
        ("Sales", "Send a follow-up email to [Name] at [email]"),
        ("Operations", "Generate an executive weekly report for MRR, churn_rate, NPS"),
        ("Operations", "Create a standard onboarding plan for [Customer] starting today"),
        ("Operations", "Flag customers at risk of churning — medium threshold"),
        ("Operations", "Schedule a kickoff call with [email] this week"),
        ("Marketing", "Repurpose this blog post for LinkedIn and email: [content]"),
        ("Marketing", "Create a content calendar for this month across LinkedIn and Twitter"),
        ("Marketing", "Launch a 3-email nurture campaign targeting operations managers"),
        ("Marketing", "Analyze LinkedIn performance for this month"),
        ("System", "memory — show current memory state"),
        ("System", "history — show task routing history"),
        ("System", "exit — shut down"),
    ]

    for agent, task in rows:
        table.add_row(agent, task)

    Console().print(table)


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> None:
    if not os.getenv("ANTHROPIC_API_KEY"):
        console.print(
            Panel(
                "[red]ANTHROPIC_API_KEY not set.[/red]\n\n"
                "1. Copy [bold].env.example[/bold] → [bold].env[/bold]\n"
                "2. Add your API key: [bold]ANTHROPIC_API_KEY=sk-ant-...[/bold]\n"
                "3. Re-run the command.",
                title="Setup Required",
                border_style="red",
            )
        )
        sys.exit(1)

    # Parse optional --profile flag
    profile_path = "config/business_profile.yaml"
    args = sys.argv[1:]
    if "--profile" in args:
        idx = args.index("--profile")
        if idx + 1 < len(args):
            profile_path = args[idx + 1]
            args = [a for i, a in enumerate(args) if i not in (idx, idx + 1)]

    try:
        ai_os = build_ai_os(profile_path)
    except FileNotFoundError as exc:
        console.print(f"[red]Config error:[/red] {exc}")
        sys.exit(1)

    mode = args[0] if args else "interactive"

    if mode == "demo":
        demo_mode(ai_os)
    else:
        interactive_mode(ai_os)


if __name__ == "__main__":
    main()

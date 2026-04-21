from datetime import datetime

from core.orchestrator import Orchestrator
from core.memory import Memory


class ReportingWorkflow:
    """
    Automated reporting pipeline:
    fetch KPIs → generate report → flag at-risk customers → send to stakeholders.
    """

    def __init__(self, orchestrator: Orchestrator, memory: Memory) -> None:
        self.orchestrator = orchestrator
        self.memory = memory

    def weekly_report(
        self,
        recipients: list[str],
        metrics: list[str] | None = None,
    ) -> dict:
        default_metrics = metrics or [
            "MRR", "churn_rate", "NPS", "active_users", "ticket_resolution_time"
        ]
        date_str = datetime.now().strftime("%B %d, %Y")
        results: dict[str, str] = {}

        results["kpi_data"] = self.orchestrator.run(
            f"Get KPI data for this week. Metrics needed: {', '.join(default_metrics)}."
        )

        results["report"] = self.orchestrator.run(
            f"Generate a weekly operations report with these metrics: {', '.join(default_metrics)}. "
            "Format: executive. Include trend analysis and key highlights."
        )

        results["at_risk"] = self.orchestrator.run(
            "Identify customers at risk of churning. Use medium threshold. Lookback: 30 days."
        )

        results["sent"] = self.orchestrator.run(
            f"Send the weekly operations report to: {', '.join(recipients)}. "
            f"Subject: 'Weekly Operations Report — {date_str}'. "
            "Include the full report content and at-risk customer summary."
        )

        self.memory.set("last_weekly_report", {"date": date_str, "recipients": recipients})

        return {
            "workflow": "weekly_report",
            "date": date_str,
            "steps_completed": len(results),
            "steps": list(results.keys()),
            "results": results,
        }

    def monthly_report(
        self,
        recipients: list[str],
        metrics: list[str] | None = None,
    ) -> dict:
        all_metrics = metrics or [
            "MRR", "ARR", "churn_rate", "NPS", "CAC", "LTV",
            "active_users", "conversion_rate",
        ]
        date_str = datetime.now().strftime("%B %Y")
        results: dict[str, str] = {}

        results["report"] = self.orchestrator.run(
            f"Generate a detailed monthly report for {date_str} "
            f"covering: {', '.join(all_metrics)}. Format: detailed."
        )

        results["sent"] = self.orchestrator.run(
            f"Send the monthly report to: {', '.join(recipients)}. "
            f"Subject: 'Monthly Business Report — {date_str}'."
        )

        return {
            "workflow": "monthly_report",
            "date": date_str,
            "steps_completed": len(results),
            "results": results,
        }

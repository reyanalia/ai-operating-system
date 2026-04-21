from typing import Any

from core.base_agent import BaseAgent
from core.memory import Memory
from core.business_profile import BusinessProfile
from tools.crm_tool import CRMTool
from tools.email_tool import EmailTool
from tools.analytics_tool import AnalyticsTool


class OperationsAgent(BaseAgent):
    """
    Operations agent — handles customer onboarding, KPI reporting, and churn detection.

    Tools: create_onboarding_plan, track_onboarding_milestone, generate_report,
           get_kpi_data, send_report, schedule_onboarding_call, flag_at_risk_customers
    """

    def __init__(self, profile: BusinessProfile, memory: Memory) -> None:
        self.crm = CRMTool(profile.crm_tool)
        self.email = EmailTool(profile.email_tool)
        self.analytics = AnalyticsTool()
        super().__init__(profile, memory)

    def _system_prompt(self) -> str:
        metrics = ", ".join(self.profile.kpi_metrics)
        return (
            f"You are an expert operations agent for {self.profile.name}.\n\n"
            f"{self.profile.to_context_string()}\n"
            "Your responsibilities:\n"
            "- Design and execute structured customer onboarding plans\n"
            "- Generate clear, actionable reports on business performance\n"
            f"- Track and interpret KPIs: {metrics}\n"
            "- Detect at-risk customers early and recommend interventions\n"
            "- Coordinate onboarding calls and milestone tracking\n\n"
            "Be systematic and data-driven. Always fetch real data with tools before reporting. "
            "Flag anomalies and give specific, actionable recommendations."
        )

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "create_onboarding_plan",
                "description": "Create a structured, milestone-based onboarding plan for a new customer.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_name": {"type": "string"},
                        "customer_company": {"type": "string"},
                        "plan_type": {
                            "type": "string",
                            "enum": ["standard", "enterprise", "self-serve"],
                        },
                        "start_date": {
                            "type": "string",
                            "description": "ISO date string (YYYY-MM-DD).",
                        },
                        "team_size": {"type": "integer"},
                        "primary_goals": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["customer_name", "customer_company", "plan_type", "start_date"],
                },
            },
            {
                "name": "track_onboarding_milestone",
                "description": "Mark a specific onboarding milestone as complete for a customer.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_id": {"type": "string"},
                        "milestone": {"type": "string"},
                        "completion_date": {"type": "string"},
                        "notes": {"type": "string"},
                    },
                    "required": ["customer_id", "milestone"],
                },
            },
            {
                "name": "generate_report",
                "description": "Generate a formatted business report for a given period and set of metrics.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_type": {
                            "type": "string",
                            "enum": ["weekly", "monthly", "quarterly", "kpi", "custom"],
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Metric names to include (e.g. MRR, churn_rate, NPS).",
                        },
                        "period_start": {"type": "string"},
                        "period_end": {"type": "string"},
                        "format": {
                            "type": "string",
                            "enum": ["summary", "detailed", "executive"],
                        },
                    },
                    "required": ["report_type", "metrics"],
                },
            },
            {
                "name": "get_kpi_data",
                "description": "Fetch current KPI data for the specified metrics and time period.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "period": {
                            "type": "string",
                            "enum": ["today", "week", "month", "quarter"],
                        },
                    },
                    "required": ["metrics", "period"],
                },
            },
            {
                "name": "send_report",
                "description": "Send a report via email to a list of stakeholder recipients.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "report_content": {"type": "string"},
                        "recipients": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "subject": {"type": "string"},
                    },
                    "required": ["report_content", "recipients", "subject"],
                },
            },
            {
                "name": "schedule_onboarding_call",
                "description": "Schedule an onboarding or check-in call with a customer.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "customer_email": {"type": "string"},
                        "call_type": {
                            "type": "string",
                            "enum": ["kickoff", "check_in", "training", "review"],
                        },
                        "preferred_date": {"type": "string"},
                        "duration_minutes": {"type": "integer"},
                    },
                    "required": ["customer_email", "call_type", "preferred_date"],
                },
            },
            {
                "name": "flag_at_risk_customers",
                "description": "Identify customers at risk of churning based on usage and engagement signals.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "threshold": {
                            "type": "string",
                            "enum": ["low", "medium", "high"],
                            "description": "Risk sensitivity: low returns fewest results, high returns most.",
                        },
                        "period_days": {
                            "type": "integer",
                            "description": "Lookback window in days.",
                        },
                    },
                    "required": ["threshold"],
                },
            },
        ]

    def _execute_tool(self, name: str, inputs: dict) -> Any:
        if name == "create_onboarding_plan":
            return self.crm.create_onboarding_plan(
                duration_days=self.profile.onboarding_duration_days,
                **inputs,
            )
        if name == "track_onboarding_milestone":
            return self.crm.track_milestone(**inputs)
        if name == "generate_report":
            return self.analytics.generate_report(**inputs)
        if name == "get_kpi_data":
            return self.analytics.get_kpi_data(**inputs)
        if name == "send_report":
            return self.email.send_report(**inputs)
        if name == "schedule_onboarding_call":
            return self.crm.schedule_call(**inputs)
        if name == "flag_at_risk_customers":
            return self.analytics.flag_at_risk(**inputs)
        return {"error": f"Unknown tool: {name}"}

import yaml
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BusinessProfile:
    """Business context loaded from YAML and injected into every agent system prompt."""

    name: str
    industry: str
    description: str
    tone: str
    target_customers: str
    value_proposition: str
    crm_tool: str
    email_tool: str
    calendar_tool: str
    brand_voice: str
    content_channels: list
    kpi_metrics: list
    onboarding_duration_days: int
    lead_scoring_criteria: list
    reporting_cadence: str

    @classmethod
    def load(cls, path: str = "config/business_profile.yaml") -> "BusinessProfile":
        cfg_path = Path(path)
        if not cfg_path.exists():
            raise FileNotFoundError(f"Business profile not found: {path}")

        with open(cfg_path) as f:
            cfg = yaml.safe_load(f)

        b = cfg["business"]
        tools = cfg.get("tools", {})
        marketing = cfg.get("marketing", {})
        operations = cfg.get("operations", {})
        sales = cfg.get("sales", {})

        return cls(
            name=b["name"],
            industry=b["industry"],
            description=b["description"],
            tone=b["tone"],
            target_customers=b["target_customers"],
            value_proposition=b["value_proposition"],
            crm_tool=tools.get("crm", "mock"),
            email_tool=tools.get("email", "mock"),
            calendar_tool=tools.get("calendar", "mock"),
            brand_voice=marketing.get("brand_voice", "professional"),
            content_channels=marketing.get("content_channels", ["linkedin", "email"]),
            kpi_metrics=operations.get("kpi_metrics", ["MRR", "churn_rate", "NPS"]),
            onboarding_duration_days=operations.get("onboarding_duration_days", 30),
            lead_scoring_criteria=sales.get("lead_scoring_criteria", []),
            reporting_cadence=operations.get("reporting_cadence", "weekly"),
        )

    def to_context_string(self) -> str:
        channels = ", ".join(self.content_channels)
        kpis = ", ".join(self.kpi_metrics)
        return (
            f"Company: {self.name}\n"
            f"Industry: {self.industry}\n"
            f"Description: {self.description}\n"
            f"Brand Tone: {self.tone}\n"
            f"Target Customers: {self.target_customers}\n"
            f"Value Proposition: {self.value_proposition}\n"
            f"Content Channels: {channels}\n"
            f"Key KPIs: {kpis}\n"
        )

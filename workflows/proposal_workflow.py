from datetime import datetime

from core.orchestrator import Orchestrator
from core.memory import Memory


class ProposalWorkflow:
    """
    End-to-end proposal automation:
    create lead → score → generate proposal → send email → update CRM status
    """

    def __init__(self, orchestrator: Orchestrator, memory: Memory) -> None:
        self.orchestrator = orchestrator
        self.memory = memory

    def run(
        self,
        prospect_name: str,
        prospect_company: str,
        prospect_email: str,
        pain_points: list[str],
        pricing_tier: str = "professional",
    ) -> dict:
        today = datetime.now().strftime("%Y-%m-%d")
        results: dict[str, str] = {}

        results["lead"] = self.orchestrator.run(
            f"Create a new lead for {prospect_name} at {prospect_company} "
            f"(email: {prospect_email}). Pain points: {', '.join(pain_points)}."
        )

        results["score"] = self.orchestrator.run(
            f"Score the lead for {prospect_name} at {prospect_company}. "
            f"Pain points: {', '.join(pain_points)}. Timeline: this quarter."
        )

        results["proposal"] = self.orchestrator.run(
            f"Create a {pricing_tier} tier sales proposal for {prospect_name} at {prospect_company}. "
            f"Their pain points: {', '.join(pain_points)}."
        )

        results["email"] = self.orchestrator.run(
            f"Send the proposal to {prospect_name} at {prospect_email}. "
            f"Subject: 'Your Custom Proposal from [Company]'. Attach the proposal document."
        )

        results["status_update"] = self.orchestrator.run(
            f"Update {prospect_company}'s lead status to 'proposal_sent'. "
            f"Note: Proposal sent {today}."
        )

        self.memory.set(
            "last_proposal_workflow",
            {"prospect": prospect_name, "company": prospect_company, "date": today},
        )

        return {
            "workflow": "proposal_creation",
            "steps_completed": len(results),
            "steps": list(results.keys()),
            "results": results,
        }

from core.orchestrator import Orchestrator
from core.memory import Memory


class LeadWorkflow:
    """
    Lead qualification and pipeline management:
    create → score → outreach; pipeline review.
    """

    def __init__(self, orchestrator: Orchestrator, memory: Memory) -> None:
        self.orchestrator = orchestrator
        self.memory = memory

    def qualify_and_route(
        self,
        lead_name: str,
        company: str,
        email: str,
        company_size: str,
        budget: str,
        pain_points: list[str],
        timeline: str = "this quarter",
    ) -> dict:
        results: dict[str, str] = {}

        results["create"] = self.orchestrator.run(
            f"Create a new lead: {lead_name} from {company}, email {email}, "
            f"company size {company_size}. Pain points: {', '.join(pain_points)}."
        )

        results["score"] = self.orchestrator.run(
            f"Score the lead for {lead_name} at {company}. "
            f"Company size: {company_size}. Budget: {budget}. "
            f"Timeline: {timeline}. Pain points: {', '.join(pain_points)}."
        )

        results["outreach"] = self.orchestrator.run(
            f"Send a personalized follow-up email to {lead_name} at {email}. "
            f"Reference their pain points: {', '.join(pain_points[:2])}. "
            "Goal: schedule a 30-minute discovery call."
        )

        return {
            "workflow": "lead_qualification",
            "steps_completed": len(results),
            "steps": list(results.keys()),
            "results": results,
        }

    def pipeline_review(self, period: str = "month") -> dict:
        result = self.orchestrator.run(
            f"Get a complete pipeline summary for this {period}. "
            "Also search for all leads with status 'proposal_sent' and identify any "
            "that may need follow-up."
        )
        return {"workflow": "pipeline_review", "period": period, "result": result}

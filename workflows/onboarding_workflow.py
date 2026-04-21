from datetime import datetime

from core.orchestrator import Orchestrator
from core.memory import Memory


class OnboardingWorkflow:
    """
    Customer onboarding sequence:
    create plan → schedule kickoff call → send welcome email.
    """

    def __init__(self, orchestrator: Orchestrator, memory: Memory) -> None:
        self.orchestrator = orchestrator
        self.memory = memory

    def kickoff(
        self,
        customer_name: str,
        customer_company: str,
        customer_email: str,
        plan_type: str = "standard",
        team_size: int | None = None,
        goals: list[str] | None = None,
    ) -> dict:
        today = datetime.now().strftime("%Y-%m-%d")
        results: dict[str, str] = {}

        results["plan"] = self.orchestrator.run(
            f"Create a {plan_type} onboarding plan for {customer_name} at {customer_company}. "
            f"Start date: {today}. Team size: {team_size or 'unknown'}. "
            f"Primary goals: {', '.join(goals or ['Product adoption', 'First value milestone'])}."
        )

        results["kickoff_call"] = self.orchestrator.run(
            f"Schedule a kickoff onboarding call with {customer_name} at {customer_email}. "
            "Preferred date: within this week. Duration: 60 minutes."
        )

        results["welcome_email"] = self.orchestrator.run(
            f"Send a welcome onboarding email to {customer_name} at {customer_email}. "
            "Include: a warm welcome, what to expect in the first 30 days, and kickoff call details."
        )

        self.memory.set(
            f"onboarding_{customer_company.lower().replace(' ', '_')}",
            {
                "customer": customer_name,
                "email": customer_email,
                "plan_type": plan_type,
                "started": today,
            },
        )

        return {
            "workflow": "onboarding_kickoff",
            "steps_completed": len(results),
            "steps": list(results.keys()),
            "results": results,
        }

    def milestone_check(
        self, customer_id: str, customer_email: str, milestone: str
    ) -> dict:
        results: dict[str, str] = {}

        results["track"] = self.orchestrator.run(
            f"Mark the milestone '{milestone}' as complete for customer {customer_id}."
        )

        results["check_in"] = self.orchestrator.run(
            f"Schedule a check-in call with {customer_email}. "
            f"Call type: check_in. Preferred date: this week. Duration: 30 minutes."
        )

        return {
            "workflow": "milestone_check",
            "milestone": milestone,
            "steps_completed": len(results),
            "results": results,
        }

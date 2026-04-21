from core.orchestrator import Orchestrator
from core.memory import Memory


class ContentWorkflow:
    """
    Content automation pipeline:
    repurpose content; build calendar; launch email campaign.
    """

    def __init__(self, orchestrator: Orchestrator, memory: Memory) -> None:
        self.orchestrator = orchestrator
        self.memory = memory

    def repurpose_from_blog(
        self,
        blog_content: str,
        channels: list[str] | None = None,
    ) -> dict:
        target_channels = channels or ["linkedin", "twitter", "email", "newsletter"]

        result = self.orchestrator.run(
            f"Repurpose the following blog post for these channels: {', '.join(target_channels)}. "
            "Optimize each version for the platform's format, audience, and character limits.\n\n"
            f"Blog content:\n{blog_content[:1200]}"
        )

        return {
            "workflow": "content_repurposing",
            "channels": target_channels,
            "result": result,
        }

    def build_content_calendar(
        self,
        period: str = "month",
        posts_per_week: int = 3,
        channels: list[str] | None = None,
        themes: list[str] | None = None,
    ) -> dict:
        ch_str = ", ".join(channels) if channels else "all active channels"
        theme_str = f"Themes: {', '.join(themes)}." if themes else ""

        result = self.orchestrator.run(
            f"Create a content calendar for the next {period}. "
            f"Channels: {ch_str}. Posts per week: {posts_per_week}. {theme_str} "
            "Rotate through thought leadership, product tips, customer success, and industry insights."
        )

        return {
            "workflow": "content_calendar",
            "period": period,
            "posts_per_week": posts_per_week,
            "result": result,
        }

    def launch_email_campaign(
        self,
        campaign_goal: str,
        target_segment: str,
        num_emails: int = 3,
        key_offer: str = "",
    ) -> dict:
        result = self.orchestrator.run(
            f"Create an email nurture sequence with {num_emails} emails. "
            f"Campaign goal: {campaign_goal}. Target segment: {target_segment}. "
            f"{'Key offer: ' + key_offer + '.' if key_offer else ''} "
            "Include send-day schedule, subject lines, preview text, and content focus for each email."
        )

        return {
            "workflow": "email_campaign",
            "goal": campaign_goal,
            "target_segment": target_segment,
            "num_emails": num_emails,
            "result": result,
        }

    def create_linkedin_post(self, topic: str, key_message: str) -> dict:
        result = self.orchestrator.run(
            f"Create a LinkedIn post about: {topic}. "
            f"Key message: {key_message}. Include a strong hook, value, and CTA."
        )
        return {"workflow": "linkedin_post", "topic": topic, "result": result}

from typing import Any

from core.base_agent import BaseAgent
from core.memory import Memory
from core.business_profile import BusinessProfile
from tools.document_tool import DocumentTool
from tools.email_tool import EmailTool
from tools.analytics_tool import AnalyticsTool


class MarketingAgent(BaseAgent):
    """
    Marketing agent — handles content repurposing, social posts,
    email campaigns, calendars, and blog creation.

    Tools: repurpose_content, create_social_post, create_email_campaign,
           analyze_content_performance, create_content_calendar, write_blog_post
    """

    def __init__(self, profile: BusinessProfile, memory: Memory) -> None:
        self.document = DocumentTool()
        self.email = EmailTool(profile.email_tool)
        self.analytics = AnalyticsTool()
        super().__init__(profile, memory)

    def _system_prompt(self) -> str:
        channels = ", ".join(self.profile.content_channels)
        return (
            f"You are an expert marketing agent for {self.profile.name}.\n\n"
            f"{self.profile.to_context_string()}\n"
            "Your responsibilities:\n"
            f"- Repurpose content across channels: {channels}\n"
            "- Create platform-optimized social media posts respecting character limits\n"
            "- Design multi-email nurture campaigns for specific audience segments\n"
            "- Build content calendars and manage publishing cadence\n"
            "- Analyze content performance and surface actionable insights\n\n"
            f"Brand voice: {self.profile.brand_voice}\n"
            "Always adapt content to each platform's best practices and audience expectations. "
            "Prioritize clarity, value, and a clear call to action."
        )

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "repurpose_content",
                "description": "Repurpose a source piece of content into multiple channel-specific formats.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "source_content": {
                            "type": "string",
                            "description": "The original content to adapt.",
                        },
                        "source_type": {
                            "type": "string",
                            "enum": [
                                "blog_post", "webinar", "case_study",
                                "email", "tweet", "video_transcript", "podcast",
                            ],
                        },
                        "target_channels": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["linkedin", "twitter", "email", "blog", "instagram", "newsletter"],
                            },
                        },
                        "tone_override": {
                            "type": "string",
                            "description": "Override the default brand voice for this piece.",
                        },
                    },
                    "required": ["source_content", "source_type", "target_channels"],
                },
            },
            {
                "name": "create_social_post",
                "description": "Create an optimized social media post for a specific platform.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "enum": ["linkedin", "twitter", "instagram", "facebook"],
                        },
                        "topic": {"type": "string"},
                        "key_message": {"type": "string"},
                        "include_cta": {"type": "boolean"},
                        "hashtags": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["platform", "topic", "key_message"],
                },
            },
            {
                "name": "create_email_campaign",
                "description": "Create a multi-email nurture sequence for a target segment.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "campaign_goal": {"type": "string"},
                        "target_segment": {"type": "string"},
                        "num_emails": {"type": "integer"},
                        "sequence_days": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "description": "Day offsets for each email (e.g. [1, 3, 7]).",
                        },
                        "key_offer": {
                            "type": "string",
                            "description": "Primary CTA or offer featured in the campaign.",
                        },
                    },
                    "required": ["campaign_goal", "target_segment", "num_emails"],
                },
            },
            {
                "name": "analyze_content_performance",
                "description": "Retrieve performance metrics for a specific channel and period.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "enum": ["linkedin", "twitter", "email", "blog", "instagram"],
                        },
                        "period": {
                            "type": "string",
                            "enum": ["week", "month", "quarter"],
                        },
                        "metrics": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["channel", "period"],
                },
            },
            {
                "name": "create_content_calendar",
                "description": "Generate a structured content calendar for the specified period.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["week", "month", "quarter"],
                        },
                        "channels": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "themes": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Content themes to rotate through.",
                        },
                        "posts_per_week": {"type": "integer"},
                    },
                    "required": ["period", "channels"],
                },
            },
            {
                "name": "write_blog_post",
                "description": "Create an SEO-optimized blog post outline and metadata.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "target_keyword": {"type": "string"},
                        "outline": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "word_count": {"type": "integer"},
                        "audience": {"type": "string"},
                    },
                    "required": ["title", "target_keyword"],
                },
            },
        ]

    def _execute_tool(self, name: str, inputs: dict) -> Any:
        if name == "repurpose_content":
            return self.document.repurpose_content(
                brand_voice=self.profile.brand_voice, **inputs
            )
        if name == "create_social_post":
            return self.document.create_social_post(
                brand_voice=self.profile.brand_voice,
                company=self.profile.name,
                **inputs,
            )
        if name == "create_email_campaign":
            return self.document.create_email_campaign(
                company=self.profile.name,
                value_proposition=self.profile.value_proposition,
                **inputs,
            )
        if name == "analyze_content_performance":
            return self.analytics.analyze_content(**inputs)
        if name == "create_content_calendar":
            return self.document.create_content_calendar(
                company=self.profile.name, **inputs
            )
        if name == "write_blog_post":
            return self.document.write_blog_post(
                company=self.profile.name,
                industry=self.profile.industry,
                **inputs,
            )
        return {"error": f"Unknown tool: {name}"}

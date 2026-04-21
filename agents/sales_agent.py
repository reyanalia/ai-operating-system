from typing import Any

from core.base_agent import BaseAgent
from core.memory import Memory
from core.business_profile import BusinessProfile
from tools.crm_tool import CRMTool
from tools.document_tool import DocumentTool
from tools.email_tool import EmailTool


class SalesAgent(BaseAgent):
    """
    Sales agent — handles lead management, proposal creation, and pipeline reporting.

    Tools: search_leads, create_lead, update_lead_status, score_lead,
           create_proposal, send_email, get_pipeline_summary
    """

    def __init__(self, profile: BusinessProfile, memory: Memory) -> None:
        self.crm = CRMTool(profile.crm_tool)
        self.document = DocumentTool()
        self.email = EmailTool(profile.email_tool)
        super().__init__(profile, memory)

    def _system_prompt(self) -> str:
        return (
            f"You are an expert sales agent for {self.profile.name}.\n\n"
            f"{self.profile.to_context_string()}\n"
            "Your responsibilities:\n"
            "- Create compelling, personalized sales proposals tailored to prospect pain points\n"
            "- Manage and score leads in the CRM system\n"
            "- Track pipeline health and deal progression\n"
            "- Send professional outreach and follow-up emails\n\n"
            "Always use the available tools to take concrete actions. "
            "Be specific, data-driven, and tailor everything to the prospect's context. "
            "When creating proposals, reference their exact pain points and industry."
        )

    def _define_tools(self) -> list[dict]:
        return [
            {
                "name": "search_leads",
                "description": "Search for leads in the CRM by name, company, email, or status filter.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search term (name, company, email). Use '*' to return all.",
                        },
                        "status": {
                            "type": "string",
                            "enum": [
                                "all", "new", "qualified", "proposal_sent",
                                "negotiating", "closed_won", "closed_lost",
                            ],
                            "description": "Filter by pipeline stage.",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "create_lead",
                "description": "Create a new lead record in the CRM.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "company": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "company_size": {"type": "string"},
                        "pain_points": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of pain points the prospect mentioned.",
                        },
                        "source": {
                            "type": "string",
                            "description": "Lead source: inbound, outbound, referral, event, etc.",
                        },
                    },
                    "required": ["name", "company", "email"],
                },
            },
            {
                "name": "update_lead_status",
                "description": "Update the pipeline status of an existing lead.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "lead_id": {
                            "type": "string",
                            "description": "Lead ID, name, or company name.",
                        },
                        "status": {
                            "type": "string",
                            "enum": [
                                "new", "qualified", "proposal_sent",
                                "negotiating", "closed_won", "closed_lost",
                            ],
                        },
                        "notes": {"type": "string"},
                    },
                    "required": ["lead_id", "status"],
                },
            },
            {
                "name": "score_lead",
                "description": "Score a lead on fit criteria and return a qualification grade (A–D).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "lead_id": {"type": "string"},
                        "company_size": {"type": "string"},
                        "budget": {"type": "string"},
                        "timeline": {"type": "string"},
                        "pain_points": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": ["lead_id"],
                },
            },
            {
                "name": "create_proposal",
                "description": "Generate a complete, formatted sales proposal document for a prospect.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "prospect_name": {"type": "string"},
                        "prospect_company": {"type": "string"},
                        "pain_points": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "pricing_tier": {
                            "type": "string",
                            "enum": ["starter", "professional", "enterprise"],
                        },
                        "proposed_solution": {
                            "type": "string",
                            "description": "Custom solution narrative for this prospect.",
                        },
                        "custom_notes": {"type": "string"},
                        "lead_id": {"type": "string"},
                    },
                    "required": ["prospect_name", "prospect_company", "pain_points", "pricing_tier"],
                },
            },
            {
                "name": "send_email",
                "description": "Send an email to a prospect or lead.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to_email": {"type": "string"},
                        "to_name": {"type": "string"},
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "attach_proposal": {
                            "type": "boolean",
                            "description": "Whether to attach the latest proposal document.",
                        },
                    },
                    "required": ["to_email", "subject", "body"],
                },
            },
            {
                "name": "get_pipeline_summary",
                "description": "Get a summary of the current sales pipeline including stage counts and value.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "enum": ["week", "month", "quarter", "year"],
                        },
                    },
                    "required": ["period"],
                },
            },
        ]

    def _execute_tool(self, name: str, inputs: dict) -> Any:
        if name == "search_leads":
            return self.crm.search_leads(**inputs)
        if name == "create_lead":
            return self.crm.create_lead(**inputs)
        if name == "update_lead_status":
            return self.crm.update_lead_status(**inputs)
        if name == "score_lead":
            return self.crm.score_lead(**inputs)
        if name == "create_proposal":
            return self.document.create_proposal(
                business_name=self.profile.name,
                value_proposition=self.profile.value_proposition,
                **inputs,
            )
        if name == "send_email":
            return self.email.send(**inputs)
        if name == "get_pipeline_summary":
            return self.crm.get_pipeline_summary(**inputs)
        return {"error": f"Unknown tool: {name}"}

import json
import os

import anthropic

from .memory import Memory
from .business_profile import BusinessProfile
from .base_agent import BaseAgent


class Orchestrator:
    """
    Claude-powered intent router.

    Classifies a natural-language task and dispatches it to the correct
    registered agent (sales | operations | marketing).
    """

    MODEL = "claude-haiku-4-5-20251001"  # Fast model for routing only

    def __init__(self, profile: BusinessProfile, memory: Memory) -> None:
        self.profile = profile
        self.memory = memory
        self.client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self._agents: dict[str, BaseAgent] = {}

    def register_agent(self, name: str, agent: BaseAgent) -> None:
        self._agents[name] = agent

    def route(self, task: str) -> tuple[str, str]:
        """
        Use Claude to classify the task intent.

        Returns (agent_name, refined_task_description).
        """
        agent_list = " | ".join(self._agents.keys())

        routing_system = f"""You are a task router for an AI operating system for {self.profile.name}.

Available agents: {agent_list}

Agent responsibilities:
- sales: lead creation, lead scoring, lead search, proposal creation, pipeline review, outreach emails
- operations: customer onboarding, milestone tracking, KPI reporting, churn detection, call scheduling
- marketing: content repurposing, social media posts, email campaigns, content calendars, blog writing

Respond with ONLY valid JSON on a single line:
{{"agent": "<agent_name>", "task": "<concise refined task description>"}}

Do not include markdown code fences or any other text."""

        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=256,
            system=[
                {
                    "type": "text",
                    "text": routing_system,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": task}],
        )

        raw = response.content[0].text.strip()
        # Strip markdown fences if Claude adds them despite the instruction
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        try:
            parsed = json.loads(raw)
            agent_name = parsed.get("agent", "").strip()
            refined_task = parsed.get("task", task).strip()
        except json.JSONDecodeError:
            # Fallback: default to sales agent
            agent_name = list(self._agents.keys())[0]
            refined_task = task

        if agent_name not in self._agents:
            agent_name = list(self._agents.keys())[0]

        return agent_name, refined_task

    def run(self, task: str, context: dict | None = None) -> str:
        """Route and execute a task, logging to shared memory."""
        agent_name, refined_task = self.route(task)

        self.memory.append_history(
            {
                "original_task": task,
                "routed_to": agent_name,
                "refined_task": refined_task,
            }
        )

        agent = self._agents[agent_name]
        result = agent.run(refined_task, context=context)

        self.memory.set(f"last_{agent_name}_result", result, agent=agent_name)
        return result

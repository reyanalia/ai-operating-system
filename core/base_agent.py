from abc import ABC, abstractmethod
from typing import Any

import anthropic

from .memory import Memory
from .business_profile import BusinessProfile


class BaseAgent(ABC):
    """
    Abstract base for all AI OS agents.

    Implements the full Claude tool-use agentic loop with prompt caching.
    Subclasses define their tool schemas, system prompt, and tool dispatcher.
    """

    MODEL = "claude-sonnet-4-6"
    MAX_TOKENS = 4096

    def __init__(self, profile: BusinessProfile, memory: Memory) -> None:
        self.profile = profile
        self.memory = memory
        self.client = anthropic.Anthropic()
        self.tools = self._define_tools()

    @abstractmethod
    def _define_tools(self) -> list[dict]:
        """Return list of Anthropic-format tool definitions."""

    @abstractmethod
    def _system_prompt(self) -> str:
        """Return the agent's system prompt (injected with business profile)."""

    @abstractmethod
    def _execute_tool(self, name: str, inputs: dict) -> Any:
        """Dispatch a tool call by name and return the result."""

    def run(self, task: str, context: dict | None = None) -> str:
        """
        Execute a task through the full agentic loop.

        Continues looping until Claude returns end_turn (no more tool calls).
        Returns the final text response.
        """
        user_content = task
        if context:
            ctx_lines = "\n".join(f"  {k}: {v}" for k, v in context.items())
            user_content = f"Context:\n{ctx_lines}\n\nTask: {task}"

        messages: list[dict] = [{"role": "user", "content": user_content}]

        while True:
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                system=[
                    {
                        "type": "text",
                        "text": self._system_prompt(),
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                tools=self.tools,
                messages=messages,
            )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return ""

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        try:
                            result = self._execute_tool(block.name, block.input)
                        except Exception as exc:
                            result = {"error": str(exc)}
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(result),
                            }
                        )
                messages.append({"role": "user", "content": tool_results})
            else:
                break

        return "Task completed."

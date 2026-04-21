# AI OS — Lessons Learned

_Updated as corrections are received from the user._

## Architecture
- Tool mock implementations must match the same interface as real providers so swapping is zero-friction
- Business profile YAML is the single source of truth for all agent behavior — never hardcode business context in agents

## Claude API
- Always add `cache_control: {"type": "ephemeral"}` to system prompts to enable prompt caching
- Handle both `end_turn` and `tool_use` stop reasons in the agentic loop
- Tool input schemas must use `input_schema` key (not `parameters`) in the Anthropic format

## Description

letta desktop integration but only for memory management (tries to manage mcp servers as well which we do not want) https://github.com/letta-ai/letta/blob/main/compose.yaml https://docs.letta.com/guides/server/remote see how it is used here: https://github.com/wsargent/recipellm?tab=readme-ov-file
## Implementation Plan

1. Set up Letta with memory-only configuration
2. Disable MCP server management features
3. Configure remote server access
4. Integrate with OpenWebUI


## Implementation Notes

Only want memory management, not MCP server management - see recipellm for usage

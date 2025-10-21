
we use:
https://github.com/ibm/mcp-context-forge

by far the most comprehensive setup for mcp s i have found. 

from reddit thread below:
```
What I'm currently playing around with as a solution for a silimar situation - is this:

Im using an Atlassian MCP server(using the sooperset image).

I host 2 instances of that Mcp server, one configured with just Jira and the other server just configured with confluence.

Since these Mcp servers NEED a PAT token passed in my case (since it's the data center version),

AND I want users to be able to pass their own pat token

AND the Mcp server needs to passed as an Authorization header.

I elected to install IBM mcp-context-forge as an MCP gateway, which allows my users to pass in an X-header with their pat, and then the gateway rewrites the Auth header with the correct token in flight, before forwarding to the mcp server.

Then in open-webUI, they just configure the tool with their extra X-header with Pat and it should work

(Disclaimer I'm testing this all out currently lol so no guarentees)

Also they just released v0.8.0 a few days ago with some amazing new features, like plugins and MCP registry/marketplace kinda thing, https://github.com/IBM/mcp-context-forge/releases/tag/v0.8.0
```

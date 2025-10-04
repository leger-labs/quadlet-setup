First priority: cloudflare mcp similar to how claude.ai uses, but can use browserbase or "generic" puppeteerring as backup
https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/
https://github.com/cloudflare/mcp-server-cloudflare/tree/main/apps/browser-rendering
https://browser.mcp.cloudflare.com/sse

## Description

tool for downloading websites to markdown and image frm url
using https://developers.cloudflare.com/agents/model-context-protocol/mcp-servers-for-cloudflare/ 
specifically https://github.com/cloudflare/mcp-server-cloudflare/tree/main/apps/browser-rendering
https://browser.mcp.cloudflare.com/sse
we set this up as a utility that takes in a url and downloads the contents.
images could optionally be uploaded into a cloudflare images and remplace the image url in the generated markdown file
## Implementation Plan

1. Set up Cloudflare browser rendering MCP server
2. Create URL to markdown conversion utility
3. Implement optional Cloudflare Images integration
4. Create image URL replacement logic


## Implementation Notes

depends on mcpo integration on leger, and a way to show the integration marketplace

---

## Description

puppetteering browser locally if cloudflare browser is not working for some reason: https://github.com/browserbase/mcp-server-browserbase specifically also investigate https://github.com/harlan-zw/mdream as part of a local alternative to cloudflare browser mcp (for "ripping" contents) as it is used in a dedicated docker container
## Implementation Plan

1. Set up browserbase MCP server as fallback
2. Investigate mdream for content extraction
3. Configure dedicated Docker container
4. Create fallback logic from Cloudflare browser


## Implementation Notes

This is a fallback option if Cloudflare browser MCP doesn't work

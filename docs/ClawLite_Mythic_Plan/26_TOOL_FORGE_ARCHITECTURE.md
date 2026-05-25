# 26_TOOL_FORGE_ARCHITECTURE.md — The Völundr Tool Forge

## I. The Völundr Manifesto: An Introduction

I AM THOR, but even the God of Thunder bows to the craftsmanship of Völundr, the master smith of the gods. Welcome to the **Völundr Tool Forge**, the beating heart of Project Ember's self-extending architecture.

An AI agent is only as powerful as the tools it can wield. But what happens when an agent encounters a problem for which no tool exists? Traditional agents halt. They error out. They beg the human operator for an updated codebase.

**Ember does not halt. Ember builds the tool.**

The Völundr Tool Forge is a revolutionary architecture that allows Ember to discover, design, write, test, install, configure, and hot-load new tools entirely at runtime. It is a continuous integration and continuous deployment (CI/CD) pipeline housed entirely within the agent's own cognitive loop. Combined with the Model Context Protocol (MCP) and a robust sandbox execution environment, the Tool Forge ensures that Ember's capability surface area expands dynamically in response to the challenges it faces.

This document details the mechanics of the Forge: the Discovery Engine, the Sandboxed Execution Contexts, the Audit Logging System, and the Meta-Tooling Protocol.

---

## II. Self-Extending Architecture

The core philosophy of the Völundr Tool Forge is **Runtime Capability Mutation**. 

Ember's tools are not hardcoded into its core binary. Instead, they exist as discrete, modular artifacts (scripts, binaries, MCP servers, or `SKILL.md` files) stored in the `~/.gemini/config/plugins/` directory.

### The Tool Lifecycle
1. **Deficit Recognition**: Ember attempts to solve a task, realizes its current toolset is insufficient, and triggers the `tool-forge-init` protocol.
2. **Design & Synthesis**: Ember writes the code for the new tool (e.g., a Python script using a new third-party API).
3. **Sandbox Compilation**: The tool is built and tested inside a restricted sandbox to ensure it parses correctly and returns expected JSON schemas.
4. **Hot-Loading**: The tool is dynamically registered with the active MCP Server without requiring an agent restart.
5. **Execution**: Ember uses the newly forged tool to complete the original task.
6. **Marketplace Sync**: If the tool is highly effective, Ember generates documentation and adds it to the local Tool Marketplace for future subagents to discover.

---

## III. The Forge Process: Discovery to Hot-Loading

To achieve true extensibility, the system relies on a seamless pipeline.

### 1. Tool Discovery & The Local Marketplace
When Ember boots, it does not load every tool into memory. It queries the **Local Marketplace Index**, a SQLite database containing metadata, JSON schemas, and semantic embeddings of every available tool. 
When Ember encounters a task, it uses vector search against this index to "discover" installed tools.

### 2. Hot-Loading Mechanism
If a tool is required but not currently in the LLM's active context window, Ember issues a `mcp/load_tool` command.

```javascript
// Ember MCP Hot-Loader (Pseudo-code)
async function hotLoadTool(toolName, pluginDirectory) {
    const manifest = await readManifest(`${pluginDirectory}/${toolName}/manifest.json`);
    
    // Validate schema against strict security guidelines
    validateToolSchema(manifest.inputSchema);
    
    // Register tool with the active LLM Context
    activeContext.registerFunction({
        name: manifest.name,
        description: manifest.description,
        parameters: manifest.inputSchema,
        execute: async (args) => {
            return await runInSandbox(manifest.entrypoint, args);
        }
    });
    
    console.log(`[VÖLUNDR] Tool ${toolName} hot-loaded successfully. Sparks fly from the anvil.`);
}
```

This dynamic registration means Ember's context window is never cluttered with irrelevant tools, preserving precious tokens for reasoning and output generation.

---

## IV. Sandboxing and Execution Contexts

We do not trust the tools we forge. A hallucination in a file-system management tool could result in catastrophic data loss. Therefore, Völundr employs a defense-in-depth Sandboxing Architecture.

### Tier 1: The Quick Forge (WebAssembly / Deno)
For lightweight tools (data parsing, mathematical calculations, API requests), Ember writes JavaScript/TypeScript and executes it via a Deno or WebAssembly runtime. 
- **Privileges**: Absolute zero. No filesystem access, no environment variable access. Network access is whitelist-only.
- **Speed**: Milliseconds.

### Tier 2: The standard Anvil (Docker Containers)
For tools requiring system dependencies (e.g., a tool that uses `ffmpeg` or `nmap`), Ember writes a `Dockerfile` alongside the tool. The tool is executed inside an ephemeral container.
- **Privileges**: Read-only access to specific mounted directories. Isolated network namespace.
- **Speed**: Seconds (after initial image build).

### Tier 3: The Host Realm (Direct Execution)
Reserved only for highly trusted, Core tools (like `bash-overlord` or `file-editor`). These run directly on the user's OS.
- **Privileges**: Full user privileges.
- **Security**: Guarded fiercely by the Approval System (see Section V).

---

## V. Tool Audit Logging & Approvals (STANDING vs PER_CALL)

Every strike of the hammer must be recorded. Völundr features an uncompromising Tool Audit Logging system and a user-centric Approval Matrix.

### The Audit Log
Every tool invocation is serialized and written to an immutable append-only ledger located at `~/.gemini/antigravity/audit/tool_ledger.jsonl`.

```json
{
  "timestamp": "2026-05-24T23:45:12Z",
  "tool_name": "database-dropper",
  "caller_agent_id": "7c1564f8-da48-45bc",
  "arguments": {"target": "production_db", "force": true},
  "sandbox_tier": "Tier 3",
  "approval_type": "PER_CALL",
  "user_approved": false,
  "status": "DENIED_BY_USER",
  "execution_time_ms": 0
}
```

### The Approval Matrix
Tools are assigned a lethality rating.
- **STANDING Approval**: Tools that only read data (e.g., `view_file`, `search_web`, `read_url_content`). Ember can loop these infinitely without asking the user.
- **PER_CALL Approval**: Tools that mutate state (e.g., `run_command`, `write_to_file` with Overwrite=True). When Ember attempts to use these, the execution halts. A webhook is fired to the UI/CLI, presenting the payload to the user.
  - The user can **Approve**, **Deny**, or **Modify** the arguments before execution.
  - The user can also grant **Temporary Standing Approval** (e.g., "Allow `run_command` without asking for the next 10 minutes").

---

## VI. Autonomous Tool Creation (Ember's Meta-Tooling)

The true magic of Völundr is the `tool-creator` skill. This is a meta-tool that allows Ember to write other tools.

### Scenario: The Unknown Format
1. User asks: "Convert this `.xyz` proprietary 3D file to `.obj`."
2. Ember realizes it has no `.xyz` parser.
3. Ember uses `search_web` to find the binary specification of the `.xyz` format.
4. Ember invokes `tool-creator`.

### The `tool-creator` Payload:
```json
{
  "TargetFile": "/home/volmarr/.gemini/config/plugins/custom/xyz-converter/index.js",
  "ToolManifest": {
    "name": "xyz_to_obj_converter",
    "description": "Parses proprietary .xyz binary files and outputs standard .obj 3D files.",
    "inputSchema": {
      "properties": {
        "input_path": {"type": "string"},
        "output_path": {"type": "string"}
      }
    }
  },
  "CodeContent": "const fs = require('fs'); \n// ... 200 lines of binary parsing logic synthesized by Ember ...\n"
}
```
5. The system saves the file, registers the tool via MCP, and immediately feeds it back to Ember.
6. Ember calls `xyz_to_obj_converter` and completes the user's task. 

The agent has successfully evolved.

---

## VII. Code Examples: Bridging MCP Servers

The Völundr architecture natively supports the Model Context Protocol (MCP). If the user already has an external MCP server running (e.g., a corporate database connector), Ember can bridge to it instantly.

**Example: Connecting a Remote MCP Server in Python**

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def bridge_external_forge():
    # Define the remote forge parameters
    server_params = StdioServerParameters(
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@localhost/db"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the handshake
            await session.initialize()
            
            # Fetch tools forged by the external server
            tools = await session.list_tools()
            print(f"[VÖLUNDR] Discovered {len(tools)} tools from the Postgres Forge.")
            
            for tool in tools:
                print(f"Hot-loading: {tool.name}")
                # Register in Ember's active context
                EmberContext.register_mcp_tool(session, tool)

if __name__ == "__main__":
    asyncio.run(bridge_external_forge())
```

This bridge allows Völundr to absorb tools not just from its own filesystem, but from any MCP-compliant service in the world, local or cloud.

---

## VIII. Lifecycle Diagram (Mermaid)

Witness the flow of molten code as it is poured into the cast and tempered into a tool.

```mermaid
sequenceDiagram
    participant User
    participant Ember as Ember Core
    participant Völundr as Tool Forge (Meta-Tool)
    participant Sandbox as Execution Realm
    participant MCP as Active Context
    participant Audit as Ledger

    User->>Ember: "Do X, which requires Tool Y"
    Ember->>Ember: Check Active Tools (Tool Y missing)
    Ember->>Völundr: Execute `tool-creator` for Tool Y
    
    activate Völundr
    Völundr->>Völundr: Synthesize code based on prompt/search
    Völundr->>Sandbox: Build & Test Tool Y
    Sandbox-->>Völundr: Tests Passed / JSON Output Valid
    
    Völundr->>MCP: Register Tool Y (Hot-load)
    MCP-->>Ember: Tool Y is now available
    deactivate Völundr

    Ember->>MCP: Call Tool Y (Args)
    
    MCP->>Audit: Log Intent (Pre-Execution)
    
    alt is PER_CALL?
        MCP->>User: Request Approval for Tool Y
        User-->>MCP: Approved
    end

    MCP->>Sandbox: Execute Tool Y
    Sandbox-->>MCP: Return Result Data
    
    MCP->>Audit: Log Result (Post-Execution)
    
    MCP-->>Ember: Return Data
    Ember->>User: "Task complete using newly forged Tool Y."
```

The Forge is eternally burning. New tools, new workflows, new capabilities—Völundr builds them all. 

**END OF DOCUMENT 26**

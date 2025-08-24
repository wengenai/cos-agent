# LangGraph Studio Setup

## Quick Start with LangGraph Studio

1. **Install LangGraph Studio CLI:**
   ```bash
   pip install langgraph-cli
   ```

2. **Launch LangGraph Studio:**
   ```bash
   langgraph dev
   ```

3. **Access Studio Interface:**
   - Open your browser to http://localhost:8123
   - The studio will automatically detect the `langgraph.json` configuration

## Configuration

### Required Environment Variables
Create a `.env` file with your API keys:
```bash
# Required for the agent to work
OPENAI_API_KEY=your_openai_api_key_here

# Optional for web search functionality  
TAVILY_API_KEY=your_tavily_api_key_here

# Optional for tracing in LangSmith
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=cos-agent
```

### MCP Servers (Optional)
If you have MCP servers running, configure them:
```bash
# EDFX MCP Server (Company risk analysis)
EDFX_MCP_URL=localhost
EDFX_MCP_PORT=8080

# RPA MCP Server (Deal and borrower analysis)  
RPA_MCP_URL=localhost
RPA_MCP_PORT=8081

# Analysis MCP Server (Portfolio metrics)
ANALYSIS_MCP_URL=localhost
ANALYSIS_MCP_PORT=8082
```

## Graph Structure

The agent follows a **Plan-Execute** pattern:

```
START → Planning → Execution → [Action Nodes] → Completion → END
```

### Available Nodes:
- **planning**: Creates detailed execution plans
- **execution**: Executes individual plan steps
- **research**: Web search and information gathering
- **analysis**: Data analysis and insights
- **code_generation**: Code creation
- **validation**: Input/output validation
- **summarization**: Content summarization
- **completion**: Final workflow completion

## Studio Features

### Interactive Testing
- Send messages to test different conversation flows
- Inspect state at each node
- View execution traces and timing
- Debug routing decisions

### State Inspection  
Monitor the agent state including:
- Current task and execution plan
- Research results and analysis
- Tools used and iteration count
- Error logs and context

### Visual Graph
- See the complete workflow graph
- Track execution path through nodes
- Identify bottlenecks and optimization opportunities

## Example Usage

1. **Start the studio**: `langgraph dev`
2. **Open browser**: http://localhost:8123
3. **Send a message**: "Research the latest AI trends and create a summary"
4. **Watch execution**: See the agent plan, research, analyze, and summarize

## Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. **Missing API Keys**: Check that OPENAI_API_KEY is set in `.env`

3. **MCP Connection Failures**: MCP servers are optional - the agent will work without them

4. **Graph Compilation Errors**: Check `studio_app.py` for any syntax issues

### Debug Mode:
Enable verbose logging:
```bash
export LANGCHAIN_VERBOSE=true
langgraph dev
```

## Advanced Features

### Custom Prompts
- Prompts are managed in the `prompts/` directory
- Edit templates and restart studio to see changes

### Knowledge Base
- Add custom knowledge in the `knowledge_base/` directory  
- Agent will automatically incorporate relevant knowledge

### Function Calling
- Register custom functions in `function_tools.py`
- Test function calls through the studio interface
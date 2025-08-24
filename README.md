# LangGraph Agentic Solution

A comprehensive agentic solution built with LangGraph featuring separate planning and execution phases, designed to work with MCP (Model Context Protocol) servers.

## 🏗️ Architecture

The agent follows a **Plan-Execute** pattern with clear separation of concerns:

```
START → Planning → Execution → Action Nodes → Completion → END
```

### Key Components

- **Planning Node**: Creates detailed execution plans with steps, tools, and success criteria
- **Execution Node**: Executes individual steps of the plan
- **Action Nodes**: Specialized nodes for research, analysis, code generation, validation, and summarization
- **Multi-MCP Integration**: Seamless integration with multiple MCP servers (EDFX-MCP, RPA-MCP, Analysis-MCP)
- **State Management**: Comprehensive state tracking with checkpoints

## 📋 Features

- ✅ **Separate Planning & Execution**: Clear separation between planning and execution phases
- ✅ **Multi-MCP Server Integration**: Native support for multiple MCP protocol servers (EDFX-MCP, RPA-MCP, Analysis-MCP)
- ✅ **Comprehensive State Management**: Full state tracking with SQLite checkpointing
- ✅ **Multiple Tool Support**: Built-in tools for research, analysis, code generation, and validation
- ✅ **Interactive & Batch Modes**: Support for both interactive and batch processing
- ✅ **Error Handling**: Robust error handling and recovery mechanisms
- ✅ **Extensible Architecture**: Easy to extend with new nodes and tools

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.8+
python3 --version

# Install dependencies
pip install -r requirements.txt
```

### Setup

1. **Clone and setup:**
   ```bash
   cd langgraph-agent-solution
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Required API Keys:**
   - `OPENAI_API_KEY`: OpenAI API key for the LLM
   - `TAVILY_API_KEY`: Tavily API key for web search (optional)
   - `LANGCHAIN_API_KEY`: LangSmith API key for tracing (optional)

### Running the Agent

#### Interactive Mode
```bash
python main.py --interactive
```

#### Single Query
```bash
python main.py --query "Research the latest trends in artificial intelligence"
```

#### With Multiple MCP Servers
```bash
# Configure multiple MCP servers in .env
EDFX_MCP_URL=localhost
EDFX_MCP_PORT=8080
RPA_MCP_URL=localhost  
RPA_MCP_PORT=8081
ANALYSIS_MCP_URL=localhost
ANALYSIS_MCP_PORT=8082

python main.py --query "Analyze company risk and assess portfolio metrics" --interactive
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional
TAVILY_API_KEY=your_tavily_api_key_here
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=langgraph-agent-solution

# Multi-MCP Server Configuration
EDFX_MCP_URL=your_edfx_server_url
EDFX_MCP_PORT=8080
RPA_MCP_URL=your_rpa_server_url
RPA_MCP_PORT=8081
ANALYSIS_MCP_URL=your_analysis_server_url
ANALYSIS_MCP_PORT=8082

# Agent Settings
DEFAULT_MODEL=gpt-4
MAX_ITERATIONS=10
```

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --query TEXT              Query to process
  --task-type [research|analysis|code_gen|qa|general]
                           Type of task to perform
  --max-iterations INTEGER Maximum number of iterations
  --model TEXT             Model to use (default: gpt-4)
  --interactive            Run in interactive mode
  --visualize              Show graph visualization
  --help                   Show help message
```

## 🔄 Workflow

### 1. Planning Phase
- Analyzes the input task
- Creates a structured execution plan with:
  - Sequential steps
  - Required tools for each step
  - Success criteria
  - Risk assessment

### 2. Execution Phase
- Executes each step in the plan
- Routes to appropriate action nodes
- Handles tool integration (including MCP tools)
- Manages state transitions

### 3. Action Nodes
- **Research**: Web search and information gathering
- **Analysis**: Data analysis and insights generation
- **Code Generation**: Code creation based on requirements
- **Validation**: Input/output validation
- **Summarization**: Content summarization and synthesis

## 🛠️ Multi-MCP Server Integration

The agent supports multiple MCP (Model Context Protocol) servers for specialized functionality:

### Supported MCP Servers
- **EDFX-MCP**: Company risk profile analysis tools
- **RPA-MCP**: Deal analysis and borrower relationship management tools  
- **Analysis-MCP**: Portfolio metrics and performance analysis tools

### MCP Features
- **Smart Server Selection**: Automatically routes tasks to appropriate servers
- **Health Monitoring**: Monitors all server connections and health status
- **Tool Discovery**: Auto-discovers tools from all connected servers
- **Graceful Fallbacks**: Handles server failures with error recovery

### Using MCP Tools
```python
# Direct server access
await tools.execute_edfx_tool("analyze_company_risk", {"company_id": "AAPL"})
await tools.execute_rpa_tool("analyze_deal", {"deal_id": "12345", "borrower_id": "B001"})  
await tools.execute_analysis_tool("calculate_portfolio_metrics", {"portfolio_id": "P001"})

# Smart routing (agent picks best server automatically)
await tools.execute_mcp_tool_auto("assess risk for this company", "analyze_risk", params)

# Get all available tools
all_tools = await tools.get_all_mcp_tools()
```

### Server Connection Status
When running, you'll see connection status for all servers:
```
✓ Connected to 3/3 MCP servers
  ✅ EDFX-MCP: Company risk profile analysis tools
  ✅ RPA-MCP: Deal analysis and borrower relationship management tools
  ✅ Analysis-MCP: Portfolio metrics and performance analysis tools
```

## 📊 State Management

The agent maintains comprehensive state including:

```python
AgentState = {
    "messages": [],           # Conversation history
    "current_task": str,      # Current task description
    "task_history": [],       # History of tasks
    "research_results": [],   # Research findings
    "analysis_results": {},   # Analysis outputs
    "final_answer": str,      # Final response
    "tools_used": [],        # Tools that were used
    "iteration_count": int,   # Number of iterations
    "error_log": [],         # Error tracking
    "context": {}            # Execution context
}
```

## 🧪 Testing

Run the test suite:

```bash
python test_agent.py
```

Test categories:
- Basic workflow functionality
- State management
- Tool integration
- MCP integration
- Planning and execution separation
- Graph structure and routing

## 📁 Project Structure

```
langgraph-agent-solution/
├── agent_state.py          # State definitions and schemas
├── agent_nodes.py          # Agent nodes (planning, execution, actions)
├── agent_graph.py          # LangGraph workflow definition
├── tools.py                # Built-in agent tools
├── mcp_integration.py      # MCP protocol integration
├── multi_mcp_manager.py    # Multi-MCP server management
├── main.py                 # Main application entry point
├── test_agent.py          # Test suite
├── requirements.txt        # Python dependencies
├── .env.example           # Environment configuration template
└── README.md              # This file
```

## 🔌 Extending the Agent

### Adding New Action Nodes

1. **Create the node function:**
```python
async def custom_action_node(self, state: AgentState) -> AgentState:
    # Your custom logic here
    return state
```

2. **Add to the graph:**
```python
graph.add_node("custom_action", self.nodes.custom_action_node)
```

3. **Update routing:**
```python
# Add routing logic in agent_graph.py
```

### Adding New Tools

1. **Extend the AgentTools class:**
```python
async def custom_tool(self, input_data: Any) -> ToolResult:
    # Tool implementation
    return ToolResult(...)
```

2. **Update execution nodes to use the new tool**

## 🐛 Troubleshooting

### Common Issues

1. **Missing API Keys**
   - Ensure all required API keys are set in `.env`
   - Check API key validity

2. **MCP Connection Issues**
   - Verify all MCP servers (EDFX, RPA, Analysis) are running
   - Check server URLs and port configurations in .env
   - Review server logs for errors
   - Use `mcp_health_check` tool to diagnose issues

3. **Graph Execution Errors**
   - Check state transitions
   - Verify node implementations
   - Review error logs in agent state

### Debug Mode

Enable detailed logging:
```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_VERBOSE=true
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request


## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Uses [LangChain](https://github.com/langchain-ai/langchain) ecosystem
- MCP protocol support for enhanced capabilities
- Inspired by the agent workflow patterns in modern AI systems
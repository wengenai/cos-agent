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

- ✅ **Dual LLM Support**: Choose between OpenAI (GPT) or Anthropic (Claude) models
- ✅ **Multi-Round Conversations**: Engaging conversational interface for interactive dialogues
- ✅ **Separate Planning & Execution**: Clear separation between planning and execution phases
- ✅ **Multi-MCP Server Integration**: Native support for multiple MCP protocol servers (EDFX-MCP, RPA-MCP, Analysis-MCP)
- ✅ **Comprehensive State Management**: Full state tracking with SQLite checkpointing
- ✅ **Multiple Tool Support**: Built-in tools for research, analysis, code generation, and validation
- ✅ **Interactive & Batch Modes**: Support for both interactive and batch processing
- ✅ **Error Handling**: Robust error handling and recovery mechanisms
- ✅ **Extensible Architecture**: Easy to extend with new nodes and tools

## 🚀 Quick Start - Complete Installation Guide

### Prerequisites

Before installing, ensure you have:

```bash
# Python 3.8+ (Required)
python3 --version
# Should show Python 3.8.x or higher

# Git (for cloning the repository)
git --version

# pip (Python package manager - usually comes with Python)
pip --version
```

### 📦 Complete Installation Steps

#### Step 1: Clone the Repository
```bash
# Clone the repository
git clone https://github.com/your-username/langgraph-agent-solution.git
cd langgraph-agent-solution
```

#### Step 2: Set Up Python Environment
```bash
# Create a virtual environment (recommended)
python3 -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify virtual environment is active (you should see (venv) in your prompt)
which python  # Should show path with /venv/
```

#### Step 3: Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list | grep langgraph
pip list | grep langchain
```

#### Step 4: Environment Configuration
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your preferred text editor
# nano .env    # On Linux/macOS
# notepad .env # On Windows
# code .env    # If you have VS Code
```

#### Step 5: Configure API Keys

**Choose your preferred LLM provider and add the corresponding API key to `.env`:**

**Option A: OpenAI (GPT models)**
```bash
# Add to .env file:
OPENAI_API_KEY=sk-your-openai-api-key-here
DEFAULT_MODEL=gpt-4o
```

**Option B: Anthropic (Claude models)**
```bash
# Add to .env file:
ANTHROPIC_API_KEY=sk-ant-api03-your-anthropic-key-here
DEFAULT_MODEL=claude-3-5-sonnet-20241022
```

**Option C: Both (for maximum flexibility)**
```bash
# Add both to .env file:
OPENAI_API_KEY=sk-your-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-api03-your-anthropic-key-here
DEFAULT_MODEL=gpt-4o  # or claude-3-5-sonnet-20241022
```

**Optional APIs (add if needed):**
```bash
# Web search capability (optional)
TAVILY_API_KEY=tvly-your-tavily-key-here

# LangSmith tracing (optional)
LANGCHAIN_API_KEY=lsv2_sk_your-langsmith-key-here
LANGCHAIN_TRACING_V2=true
```

### 🚀 Running the Agent

#### Step 6: Verify Installation
```bash
# Run comprehensive verification script
python3 verify_installation.py

# If verification passes, you'll see:
# 🎉 Installation verification SUCCESSFUL!
# ✅ Your LangGraph Agent is ready to use!
```

**If verification fails**, check the specific error messages and refer to the troubleshooting section below.

#### Step 7: Choose How to Run

**Option A: Interactive Mode (Terminal)**
```bash
# Start interactive conversation in terminal
python main.py --interactive

# Example conversation:
# > Hello! How can you help me today?
# > Tell me about artificial intelligence
# > What should I learn first?
```

**Option B: Single Query Mode**
```bash
# Run a single query
python main.py --query "Research the latest trends in artificial intelligence"

# With specific model
python main.py --query "Explain machine learning" --model gpt-4o
python main.py --query "Explain machine learning" --model claude-3-5-sonnet-20241022
```

**Option C: LangGraph Studio (Visual Interface)**
```bash
# Start LangGraph Studio for visual agent development
langgraph dev

# Then open in browser:
# https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

#### Step 8: Advanced Configuration (Optional)

**MCP Server Integration (for specialized tools):**
```bash
# Add to .env file for custom MCP servers:
MCP_SERVER_WEATHER_URL=http://weather-mcp.example.com
MCP_SERVER_WEATHER_PORT=9001
MCP_SERVER_WEATHER_DESC=Weather forecasting tools

# Test MCP connectivity
python3 test_flexible_mcp.py
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# LLM Provider (choose one or both)
OPENAI_API_KEY=your_openai_api_key_here          # For GPT models
ANTHROPIC_API_KEY=your_anthropic_api_key_here    # For Claude models

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

# Agent Settings - Choose your model
# OpenAI models: gpt-4o, gpt-4, gpt-3.5-turbo, gpt-4-turbo
# Claude models: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
DEFAULT_MODEL=gpt-4o
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
- **Conversation**: Multi-round conversational interactions
- **Research**: Web search and information gathering
- **Analysis**: Data analysis and insights generation
- **Code Generation**: Code creation based on requirements
- **Validation**: Input/output validation
- **Summarization**: Content summarization and synthesis

## 🤖 LLM Provider Support

The agent supports both OpenAI and Anthropic models with automatic provider detection:

### Supported Models

**OpenAI (GPT)**:
- `gpt-4o` - Latest and most capable model
- `gpt-4` - Previous generation flagship
- `gpt-3.5-turbo` - Fast and cost-effective
- `gpt-4-turbo` - Enhanced capabilities

**Anthropic (Claude)**:
- `claude-3-5-sonnet-20241022` - Latest balanced model
- `claude-3-opus-20240229` - Most capable model
- `claude-3-sonnet-20240229` - Balanced performance
- `claude-3-haiku-20240307` - Fastest model

### Model Selection

The agent automatically detects which provider to use based on:
1. **Model Name**: Recognizes model patterns (gpt-* for OpenAI, claude-* for Anthropic)
2. **Available API Keys**: Uses the appropriate key for the selected model
3. **Fallback Logic**: If model name is ambiguous, prefers available provider

### Switching Between Providers

1. **Environment Variable**: Set `DEFAULT_MODEL` in your `.env` file
2. **Command Line**: Use `--model` parameter
3. **Runtime**: Models are determined at agent initialization

```bash
# Use OpenAI
export DEFAULT_MODEL=gpt-4o
python main.py --interactive

# Use Anthropic  
export DEFAULT_MODEL=claude-3-5-sonnet-20241022
python main.py --interactive
```

## 💬 Conversational Features

The agent supports engaging multi-round conversations with:
- **Context Retention**: Maintains conversation history (last 6 messages)
- **Smart Routing**: Automatically routes simple questions to conversational mode
- **Research Integration**: Can access research results and analysis in conversations
- **Natural Responses**: Provides helpful, conversational responses

## 🛠️ Multi-MCP Server Integration

The agent supports multiple MCP (Model Context Protocol) servers for specialized functionality with **flexible configuration**:

### Supported MCP Servers
- **EDFX-MCP**: Company risk profile analysis tools
- **RPA-MCP**: Deal analysis and borrower relationship management tools  
- **Analysis-MCP**: Portfolio metrics and performance analysis tools
- **Dynamic Servers**: Add any number of custom MCP servers

### MCP Configuration Options

#### 1. **Predefined Servers** (Legacy format)
```bash
# Traditional format for known servers
EDFX_MCP_URL=https://your-edfx-server.com
EDFX_MCP_PORT=8080

RPA_MCP_URL=https://your-rpa-server.com  
RPA_MCP_PORT=8081

ANALYSIS_MCP_URL=https://your-analysis-server.com
ANALYSIS_MCP_PORT=8082
```

#### 2. **Dynamic Server Configuration** (New flexible format)
```bash
# Add ANY number of MCP servers using this pattern:
MCP_SERVER_WEATHER_URL=http://weather-mcp.example.com
MCP_SERVER_WEATHER_PORT=9001
MCP_SERVER_WEATHER_DESC=Weather forecasting tools

MCP_SERVER_DATABASE_URL=https://db-mcp.company.com
MCP_SERVER_DATABASE_PORT=8090
MCP_SERVER_DATABASE_DESC=Database query tools

MCP_SERVER_ANALYTICS_URL=http://analytics.internal:8095
MCP_SERVER_ANALYTICS_PORT=8095
MCP_SERVER_ANALYTICS_DESC=Custom analytics and reporting tools
```

### MCP Features
- **Dynamic Discovery**: Automatically detects servers using environment variable patterns
- **Runtime Management**: Add/remove servers programmatically at runtime
- **Smart Server Selection**: Automatically routes tasks to appropriate servers
- **Health Monitoring**: Monitors all server connections and health status
- **Tool Discovery**: Auto-discovers tools from all connected servers
- **Graceful Fallbacks**: Handles server failures with error recovery

### Using MCP Tools

#### Direct Server Access
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

#### Programmatic Server Management
```python
from multi_mcp_manager import default_multi_mcp_manager as mcp_manager

# Add a new server at runtime
mcp_manager.add_server_config(
    server_id="weather",
    name="Weather-MCP", 
    url="http://weather-service.com",
    port=9000,
    description="Weather forecasting and climate data"
)

# Connect to the new server
await mcp_manager.connect_server("weather")

# List all configured servers
servers = mcp_manager.list_server_configs()
print(servers)

# Connect to specific server
await mcp_manager.connect_server("weather")

# Disconnect from specific server  
await mcp_manager.disconnect_server("weather")

# Remove server configuration
mcp_manager.remove_server_config("weather")
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

## 🎯 Updating System Prompts

### Method 1: Direct Template Editing

To customize how the agent behaves, you can modify system prompts in `prompt_manager.py`:

#### **1. Locate the Prompt Template**
Edit the appropriate template in `prompt_manager.py` (lines 67-200):

```python
"planning_agent": PromptTemplate(
    name="planning_agent",
    version="1.0.0",
    template="""You are a planning agent responsible for creating detailed execution plans.

Task: {task}
Context: {context}

Your custom instructions here...

Return a JSON plan with this structure:
{{
    "steps": [
        {{"step": 1, "action": "action_name", "description": "what to do", "tools_needed": ["tool1"]}},
    ],
    "expected_outcome": "description of expected result",
    "success_criteria": ["criteria1", "criteria2"],
    "risks": ["risk1", "risk2"]
}}

Be specific and actionable in your planning.""",
    variables=["task", "context"],  # ⚠️ Must list ALL {variables} used in template
    description="Main planning agent prompt for creating execution plans",
    # ... other fields
),
```

#### **2. Available Prompt Templates**
- **`planning_agent`** - Creates execution plans (lines 67-100)
- **`execution_coordinator`** - Manages plan execution (lines 102-130)  
- **`research_specialist`** - Handles research tasks (lines 132-162)
- **`knowledge_integration`** - Integrates knowledge sources (lines 164-199)
- **`conversational_node`** - Multi-round conversations (in `agent_nodes.py:538-563`)

#### **3. Critical Requirements**
- **Variables**: Always include ALL `{variables}` used in template in the `variables` list
- **JSON Format**: For structured responses, specify exact JSON structure with `{{` and `}}`
- **Error Handling**: Include fallback instructions for error scenarios
- **Consistency**: Use consistent variable names like `{task}`, `{context}`, `{current_step}`

#### **4. Testing Changes**
```bash
# LangGraph Studio automatically reloads when you save prompt_manager.py
langgraph dev

# Or test via command line
python main.py --query "test query" --interactive
```

**Note**: Changes to `prompt_manager.py` are automatically detected and reloaded in LangGraph Studio! 🔄

## 🖥️ System Requirements

### Minimum Requirements
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Required for API calls and package installation

### Supported Platforms
- ✅ **Windows** (10, 11)
- ✅ **macOS** (Intel and Apple Silicon)
- ✅ **Linux** (Ubuntu, CentOS, Debian, etc.)
- ✅ **WSL2** (Windows Subsystem for Linux)

## 🐛 Troubleshooting

### Installation Issues

1. **Python Version Issues**
   ```bash
   # Check Python version
   python3 --version
   
   # If Python 3.8+ not available, install it:
   # On macOS: brew install python@3.11
   # On Ubuntu: sudo apt update && sudo apt install python3.11
   # On Windows: Download from python.org
   ```

2. **Package Installation Errors**
   ```bash
   # Clear pip cache and retry
   pip cache purge
   pip install --no-cache-dir -r requirements.txt
   
   # If still failing, try with verbose output
   pip install -v -r requirements.txt
   ```

3. **Virtual Environment Issues**
   ```bash
   # Remove and recreate virtual environment
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

### Runtime Issues

1. **Missing API Keys**
   ```bash
   # Check if .env file exists and has your API key
   cat .env
   
   # Ensure API key is valid (test with simple query)
   python3 -c "import os; from dotenv import load_dotenv; load_dotenv(); print('OpenAI key:', os.getenv('OPENAI_API_KEY', 'Not set')[:10] + '...')"
   ```

2. **Import Errors**
   ```bash
   # Test critical imports
   python3 -c "import langgraph; print('✅ LangGraph OK')"
   python3 -c "import langchain; print('✅ LangChain OK')"
   python3 -c "import langchain_openai; print('✅ OpenAI OK')"
   python3 -c "import langchain_anthropic; print('✅ Anthropic OK')"
   ```

3. **LangGraph Studio Issues**
   ```bash
   # If Studio won't start
   pip install --upgrade langgraph langgraph-checkpoint-sqlite
   
   # If port 2024 is in use
   langgraph dev --port 2025
   
   # Check if server is running
   curl http://localhost:2024/health
   ```

4. **MCP Connection Issues**
   ```bash
   # Test MCP configuration
   python3 test_flexible_mcp.py
   
   # Check MCP server status in .env
   echo "MCP Servers configured:"
   grep "MCP" .env
   ```

### Performance Issues

1. **Slow Response Times**
   - Check internet connection
   - Try different model (gpt-3.5-turbo is faster than gpt-4o)
   - Reduce MAX_ITERATIONS in .env file

2. **Memory Issues**
   - Reduce context window size
   - Clear conversation history periodically
   - Use lighter models (claude-3-haiku, gpt-3.5-turbo)

### Debug Mode

Enable detailed logging:
```bash
# Add to .env file
LANGCHAIN_TRACING_V2=true
LANGCHAIN_VERBOSE=true

# Run with debug output
python main.py --interactive --debug
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
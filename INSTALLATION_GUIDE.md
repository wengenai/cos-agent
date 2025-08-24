# 🚀 Complete Installation Guide

This guide provides step-by-step instructions to install and run the LangGraph Agent on a new PC.

## 📋 Pre-Installation Checklist

Before starting, ensure you have:

- [ ] **Python 3.8+** installed
- [ ] **Git** installed
- [ ] **Internet connection** for package downloads
- [ ] **Text editor** (VS Code, Notepad++, nano, etc.)
- [ ] **API key** from OpenAI or Anthropic

## 🛠️ Installation Steps

### Step 1: Verify Prerequisites

```bash
# Check Python version (should be 3.8 or higher)
python3 --version

# Check pip
pip --version

# Check git
git --version
```

If any of these are missing:
- **Python**: Download from [python.org](https://python.org)
- **Git**: Download from [git-scm.com](https://git-scm.com)

### Step 2: Clone Repository

```bash
# Option A: Clone via HTTPS
git clone https://github.com/your-username/langgraph-agent-solution.git

# Option B: Clone via SSH (if you have SSH keys set up)
git clone git@github.com:your-username/langgraph-agent-solution.git

# Option C: Download ZIP file and extract it

# Navigate to directory
cd langgraph-agent-solution
```

### Step 3: Set Up Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Verify activation (you should see (venv) in your terminal prompt)
which python
# Should show path containing 'venv'
```

### Step 4: Install Dependencies

```bash
# Upgrade pip to latest version
pip install --upgrade pip

# Install main requirements
pip install -r requirements.txt

# Install LangGraph Studio requirements
pip install -r studio_requirements.txt

# Verify critical packages are installed
pip list | grep langgraph
pip list | grep langchain
```

### Step 5: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your preferred editor
# Windows: notepad .env
# macOS: open -e .env
# Linux: nano .env
# VS Code: code .env
```

### Step 6: Add API Keys

Edit the `.env` file and add your API keys:

**For OpenAI (recommended for beginners):**
```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
DEFAULT_MODEL=gpt-4o
```

**For Anthropic:**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-anthropic-key-here
DEFAULT_MODEL=claude-3-5-sonnet-20241022
```

**For both (maximum flexibility):**
```bash
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-anthropic-key-here
DEFAULT_MODEL=gpt-4o
```

### Step 7: Verification Tests

Run these tests to ensure everything is working:

```bash
# Test 1: Import test
python3 -c "
import langgraph
import langchain
import langchain_openai
import langchain_anthropic
print('✅ All packages imported successfully')
"

# Test 2: Environment test
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
openai_key = os.getenv('OPENAI_API_KEY', 'Not set')
anthropic_key = os.getenv('ANTHROPIC_API_KEY', 'Not set')
print('OpenAI key:', openai_key[:10] + '...' if openai_key != 'Not set' else 'Not set')
print('Anthropic key:', anthropic_key[:10] + '...' if anthropic_key != 'Not set' else 'Not set')
"

# Test 3: Agent functionality test
python3 test_conversation.py

# Test 4: MCP configuration test
python3 test_flexible_mcp.py
```

### Step 8: First Run

Choose your preferred way to run the agent:

**Option A: Interactive Terminal Mode**
```bash
python main.py --interactive
```

**Option B: LangGraph Studio (Visual Interface)**
```bash
langgraph dev
# Then open: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
```

**Option C: Single Query**
```bash
python main.py --query "Hello! Tell me about yourself."
```

## ✅ Success Indicators

You'll know the installation was successful when:

1. **No import errors** in verification tests
2. **API keys detected** in environment test
3. **Agent responds** to test conversations
4. **LangGraph Studio opens** without errors (if using Studio)

## 🔧 Platform-Specific Instructions

### Windows

```cmd
# Install Python from python.org if not installed
# Use Command Prompt or PowerShell

# Clone repository
git clone https://github.com/your-username/langgraph-agent-solution.git
cd langgraph-agent-solution

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
pip install -r studio_requirements.txt

# Edit .env file
notepad .env
```

### macOS

```bash
# Install Python via Homebrew (recommended)
brew install python@3.11

# Clone repository
git clone https://github.com/your-username/langgraph-agent-solution.git
cd langgraph-agent-solution

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
pip install -r studio_requirements.txt

# Edit .env file
open -e .env
```

### Linux (Ubuntu/Debian)

```bash
# Install Python if not available
sudo apt update
sudo apt install python3 python3-pip python3-venv git

# Clone repository
git clone https://github.com/your-username/langgraph-agent-solution.git
cd langgraph-agent-solution

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt
pip install -r studio_requirements.txt

# Edit .env file
nano .env
```

## 🆘 Quick Fixes for Common Issues

### "Command not found: python3"
```bash
# Try python instead of python3
python --version

# Or install Python 3
# Windows: Download from python.org
# macOS: brew install python
# Linux: sudo apt install python3
```

### "No module named langgraph"
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall packages
pip install -r requirements.txt
```

### "OpenAI API key not valid"
```bash
# Check your API key format
# OpenAI keys start with: sk-
# Anthropic keys start with: sk-ant-api03-

# Test API key manually
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('API key loaded:', bool(os.getenv('OPENAI_API_KEY')))
"
```

### "Port 2024 already in use"
```bash
# Use different port for LangGraph Studio
langgraph dev --port 2025

# Or find and kill process using port 2024
# Windows: netstat -ano | findstr :2024
# macOS/Linux: lsof -ti:2024 | xargs kill
```

## 🎯 Next Steps

After successful installation:

1. **Explore examples**: Try the test files to understand capabilities
2. **Read documentation**: Check README.md for detailed feature descriptions
3. **Configure MCP servers**: Add custom MCP servers if needed
4. **Customize models**: Switch between OpenAI and Anthropic models
5. **Build conversations**: Start chatting with the agent!

## 📞 Getting Help

If you encounter issues:

1. **Check troubleshooting section** in README.md
2. **Run diagnostic tests** provided in this guide
3. **Check GitHub issues** for similar problems
4. **Create new issue** with error details and system info

---

🎉 **Congratulations! Your LangGraph Agent is now ready to use.**
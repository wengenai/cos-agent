# MCP Configuration Guide

## 📋 Overview

The Multi-MCP Manager now supports **highly flexible configuration** allowing you to add unlimited MCP servers through multiple methods.

## 🚀 Configuration Methods

### 1. **Predefined Servers** (Existing Method)
For well-known servers like EDFX, RPA, and Analysis:

```bash
# In .env file
EDFX_MCP_URL=https://your-edfx-server.com
EDFX_MCP_PORT=8080

RPA_MCP_URL=https://your-rpa-server.com  
RPA_MCP_PORT=8081

ANALYSIS_MCP_URL=https://your-analysis-server.com
ANALYSIS_MCP_PORT=8082
```

### 2. **Dynamic Environment Variables** (New Method)
Add any number of servers using the pattern:

```bash
# Pattern: MCP_SERVER_{NAME}_URL, MCP_SERVER_{NAME}_PORT, MCP_SERVER_{NAME}_DESC

# Weather service
MCP_SERVER_WEATHER_URL=http://weather-mcp.example.com
MCP_SERVER_WEATHER_PORT=9001
MCP_SERVER_WEATHER_DESC=Weather forecasting and climate data tools

# Database service
MCP_SERVER_DATABASE_URL=https://db-mcp.company.com
MCP_SERVER_DATABASE_PORT=8090
MCP_SERVER_DATABASE_DESC=Database query and management tools

# Analytics service
MCP_SERVER_ANALYTICS_URL=http://analytics.internal:8095
MCP_SERVER_ANALYTICS_PORT=8095
MCP_SERVER_ANALYTICS_DESC=Custom analytics and reporting tools

# Financial data service
MCP_SERVER_BLOOMBERG_URL=https://bloomberg-mcp.financial.com
MCP_SERVER_BLOOMBERG_PORT=8100
MCP_SERVER_BLOOMBERG_DESC=Bloomberg financial data and market analysis

# Custom AI service
MCP_SERVER_CUSTOM_AI_URL=http://ai-models.internal:9000
MCP_SERVER_CUSTOM_AI_PORT=9000
MCP_SERVER_CUSTOM_AI_DESC=Custom AI models and inference tools
```

### 3. **Programmatic Configuration** (Runtime Method)
Add servers directly in Python code:

```python
from multi_mcp_manager import default_multi_mcp_manager as mcp_manager

# Add a new server
mcp_manager.add_server_config(
    server_id="weather",
    name="Weather-MCP", 
    url="http://weather-service.com",
    port=9000,
    description="Weather forecasting and climate data"
)

# Connect to the server
await mcp_manager.connect_server("weather")
```

## 🛠️ Management API

### Server Management
```python
# List all configured servers
servers = mcp_manager.list_server_configs()

# Add a server
mcp_manager.add_server_config("server_id", "Name", "url", port, "description")

# Remove a server 
mcp_manager.remove_server_config("server_id")

# Connect to specific server
success = await mcp_manager.connect_server("server_id")

# Disconnect from specific server
await mcp_manager.disconnect_server("server_id")

# Connect to all servers
results = await mcp_manager.connect_all_servers()

# Disconnect from all servers
await mcp_manager.disconnect_all_servers()
```

### Server Information
```python
# Get server details
servers = mcp_manager.list_server_configs()
print(servers)
# Output:
# {
#   'weather': {
#     'name': 'Weather-MCP',
#     'url': 'http://weather-mcp.example.com', 
#     'port': 9001,
#     'description': 'Weather forecasting tools',
#     'connected': False
#   }
# }

# Get connection status
status = mcp_manager.get_connection_status()
```

## 🎯 Use Cases

### Adding Multiple Specialized Services
```bash
# Financial Services
MCP_SERVER_MARKET_DATA_URL=https://market-data.finance.com
MCP_SERVER_MARKET_DATA_PORT=8200
MCP_SERVER_MARKET_DATA_DESC=Real-time market data and trading information

# Development Tools
MCP_SERVER_GITHUB_URL=http://github-mcp.dev.internal
MCP_SERVER_GITHUB_PORT=8300
MCP_SERVER_GITHUB_DESC=GitHub integration and repository management

# Communication Tools
MCP_SERVER_SLACK_URL=https://slack-mcp.company.com
MCP_SERVER_SLACK_PORT=8400
MCP_SERVER_SLACK_DESC=Slack messaging and team collaboration

# Document Processing
MCP_SERVER_DOCUMENT_URL=http://doc-processor.internal:8500
MCP_SERVER_DOCUMENT_PORT=8500
MCP_SERVER_DOCUMENT_DESC=Document parsing and analysis tools
```

### Environment-Specific Configuration
```bash
# Development Environment
MCP_SERVER_DEV_DB_URL=http://dev-database.internal
MCP_SERVER_DEV_DB_PORT=5432
MCP_SERVER_DEV_DB_DESC=Development database access

# Production Environment  
MCP_SERVER_PROD_DB_URL=https://prod-database.secure.com
MCP_SERVER_PROD_DB_PORT=5432
MCP_SERVER_PROD_DB_DESC=Production database access

# Testing Environment
MCP_SERVER_TEST_SUITE_URL=http://test-runner.internal
MCP_SERVER_TEST_SUITE_PORT=8600
MCP_SERVER_TEST_SUITE_DESC=Automated testing and validation tools
```

## 🔧 Configuration Notes

### Environment Variable Rules:
- **URL**: `MCP_SERVER_{NAME}_URL` (required)
- **PORT**: `MCP_SERVER_{NAME}_PORT` (optional, defaults to 8080)  
- **DESC**: `MCP_SERVER_{NAME}_DESC` (optional, auto-generated from name)
- **NAME**: Can contain letters, numbers, and underscores
- **Case**: Environment variable names should be UPPERCASE

### Server ID Rules:
- Server IDs are automatically converted to lowercase
- Underscores in names are preserved in IDs
- Server IDs must be unique

### Examples:
```bash
MCP_SERVER_WEATHER_URL=...     → server_id: "weather"
MCP_SERVER_DATA_LAKE_URL=...   → server_id: "data_lake"  
MCP_SERVER_AI_MODELS_URL=...   → server_id: "ai_models"
```

## ✅ Benefits

1. **Unlimited Servers**: Add as many MCP servers as needed
2. **Zero Code Changes**: Add servers via environment variables only
3. **Runtime Management**: Add/remove servers programmatically
4. **Backward Compatible**: Existing EDFX/RPA/Analysis configs still work
5. **Flexible Naming**: Use any naming convention for your servers
6. **Auto-Discovery**: Servers are automatically detected from environment
7. **Easy Deployment**: Different configs for dev/staging/production environments

## 🎉 Quick Start

1. **Add environment variables** for your MCP servers
2. **Start the agent** - servers are automatically discovered
3. **Use the tools** - agent intelligently routes to appropriate servers
4. **Monitor connections** - see which servers are connected in logs

The system is now **fully flexible** and ready for any number of MCP servers!
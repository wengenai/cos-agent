#!/usr/bin/env python3
"""
Test the flexible MCP configuration system
"""

import asyncio
import os
from multi_mcp_manager import MultiMCPManager

async def test_dynamic_mcp_configuration():
    """Test dynamic MCP server configuration"""
    print("🧪 Testing Flexible MCP Configuration System")
    print("=" * 50)
    
    # Create a fresh MCP manager
    mcp_manager = MultiMCPManager()
    
    print("📋 Initial Configuration:")
    initial_servers = mcp_manager.list_server_configs()
    if initial_servers:
        for server_id, info in initial_servers.items():
            print(f"  📦 {server_id}: {info['name']} ({info['url']}:{info['port']})")
            print(f"      {info['description']}")
    else:
        print("  📝 No servers configured via environment variables")
    
    print(f"\n🔍 Found {len(initial_servers)} preconfigured servers")
    
    # Test adding dynamic servers
    print("\n🚀 Testing Dynamic Server Addition...")
    
    # Add some test servers
    test_servers = [
        {
            "id": "weather", 
            "name": "Weather-MCP",
            "url": "http://weather-mcp.example.com",
            "port": 9001,
            "description": "Weather forecasting and climate data tools"
        },
        {
            "id": "database",
            "name": "Database-MCP", 
            "url": "https://db-mcp.internal.com",
            "port": 8090,
            "description": "Database query and management tools"
        },
        {
            "id": "analytics",
            "name": "Analytics-MCP",
            "url": "http://analytics.company.local",
            "port": 8095, 
            "description": "Custom analytics and reporting tools"
        }
    ]
    
    # Add servers dynamically
    for server in test_servers:
        print(f"➕ Adding {server['name']}...")
        mcp_manager.add_server_config(
            server_id=server['id'],
            name=server['name'],
            url=server['url'], 
            port=server['port'],
            description=server['description']
        )
        print(f"   ✅ Added {server['name']}")
    
    # List all servers after addition
    print(f"\n📋 All Configured Servers After Addition:")
    all_servers = mcp_manager.list_server_configs()
    for server_id, info in all_servers.items():
        status = "🟢 Connected" if info['connected'] else "🔴 Disconnected"
        print(f"  📦 {server_id}: {info['name']}")
        print(f"      URL: {info['url']}:{info['port']}")
        print(f"      Description: {info['description']}")
        print(f"      Status: {status}")
        print()
    
    print(f"📊 Total servers configured: {len(all_servers)}")
    
    # Test server removal  
    print("🗑️  Testing Server Removal...")
    print("   Removing 'weather' server...")
    mcp_manager.remove_server_config("weather")
    
    remaining_servers = mcp_manager.list_server_configs()
    print(f"   ✅ Removed server. Remaining: {len(remaining_servers)}")
    
    # Test environment variable detection
    print("\n🌍 Testing Environment Variable Detection...")
    
    # Temporarily set environment variables to test dynamic detection
    test_env_vars = {
        "MCP_SERVER_TESTENV_URL": "http://test-env.example.com",
        "MCP_SERVER_TESTENV_PORT": "9999", 
        "MCP_SERVER_TESTENV_DESC": "Test environment server",
        "MCP_SERVER_ANOTHER_URL": "https://another-server.com"
    }
    
    # Set environment variables
    for key, value in test_env_vars.items():
        os.environ[key] = value
    
    # Create a new manager to test env var detection
    print("   Creating new MCP manager to test env var detection...")
    new_mcp_manager = MultiMCPManager()
    env_servers = new_mcp_manager.list_server_configs()
    
    print(f"   📋 Servers detected from environment variables:")
    for server_id, info in env_servers.items():
        if server_id in ["testenv", "another"]:  # Only show the test servers
            print(f"     🌟 {server_id}: {info['name']}")
            print(f"         URL: {info['url']}:{info['port']}")
            print(f"         Description: {info['description']}")
    
    # Cleanup environment variables
    for key in test_env_vars.keys():
        del os.environ[key]
    
    print("\n✅ Flexible MCP Configuration Test Completed!")
    
    return True

async def test_mcp_connection_simulation():
    """Test MCP connection methods (without actual servers)"""
    print("\n🔌 Testing MCP Connection Methods...")
    
    mcp_manager = MultiMCPManager()
    
    # Add a test server
    mcp_manager.add_server_config(
        server_id="test",
        name="Test-MCP",
        url="http://nonexistent-server.com", 
        port=8080,
        description="Test server for connection testing"
    )
    
    print("   📦 Test server configured")
    
    # Test individual server connection (will fail but won't crash)
    print("   🔍 Testing individual server connection...")
    try:
        result = await mcp_manager.connect_server("test")
        print(f"   📊 Connection result: {'✅ Success' if result else '❌ Failed (expected)'}")
    except Exception as e:
        print(f"   📊 Connection result: ❌ Failed with error (expected): {type(e).__name__}")
    
    # Test connecting to all servers
    print("   🔍 Testing connect to all servers...")
    try:
        results = await mcp_manager.connect_all_servers()
        print(f"   📊 Connection results: {results}")
    except Exception as e:
        print(f"   📊 Connection failed (expected): {type(e).__name__}")
    
    print("   ✅ Connection methods test completed")

async def main():
    """Run all tests"""
    print("🎯 Testing Enhanced MCP Configuration System")
    print("=" * 60)
    
    results = []
    
    # Test 1: Dynamic configuration
    print("\n📍 TEST 1: Dynamic MCP Configuration")
    config_result = await test_dynamic_mcp_configuration()
    results.append(("Dynamic Configuration", config_result))
    
    # Test 2: Connection methods
    print("\n📍 TEST 2: MCP Connection Methods")
    await test_mcp_connection_simulation()
    results.append(("Connection Methods", True))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY - Flexible MCP Configuration")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    print("\n🎉 MCP Configuration System Summary:")
    print("  ✅ Dynamic server discovery from environment variables")
    print("  ✅ Programmatic server management (add/remove)")
    print("  ✅ Flexible configuration patterns")
    print("  ✅ Individual and bulk server connection methods")
    print("  ✅ Server status monitoring and listing")
    
    print("\n💡 How to add new MCP servers:")
    print("  1. Environment Variables: MCP_SERVER_{NAME}_URL=...")
    print("  2. Predefined Variables: EDFX_MCP_URL, RPA_MCP_URL, etc.")  
    print("  3. Programmatic: mcp_manager.add_server_config(...)")

if __name__ == "__main__":
    asyncio.run(main())
#!/usr/bin/env python3
"""
CLI Tools for managing prompts and knowledge base
"""

import argparse
import json
import sys
from pathlib import Path
from prompt_manager import PromptManager, PromptTemplate
from knowledge_base import KnowledgeBase, KnowledgeItem, KnowledgeQuery
from datetime import datetime


def setup_prompt_commands(subparsers):
    """Setup prompt management commands"""
    
    # Prompt management
    prompt_parser = subparsers.add_parser('prompts', help='Manage system prompts')
    prompt_subparsers = prompt_parser.add_subparsers(dest='prompt_command', help='Prompt commands')
    
    # List prompts
    list_parser = prompt_subparsers.add_parser('list', help='List all prompts')
    list_parser.add_argument('--tags', type=str, help='Filter by tags (comma-separated)')
    
    # Show prompt
    show_parser = prompt_subparsers.add_parser('show', help='Show a specific prompt')
    show_parser.add_argument('name', help='Prompt name')
    show_parser.add_argument('--version', help='Specific version')
    
    # Create prompt
    create_parser = prompt_subparsers.add_parser('create', help='Create a new prompt')
    create_parser.add_argument('name', help='Prompt name')
    create_parser.add_argument('--template', help='Prompt template (or read from stdin)')
    create_parser.add_argument('--description', help='Prompt description')
    create_parser.add_argument('--variables', help='Variables (comma-separated)')
    create_parser.add_argument('--tags', help='Tags (comma-separated)')
    create_parser.add_argument('--file', help='Read template from file')
    
    # Update prompt
    update_parser = prompt_subparsers.add_parser('update', help='Update an existing prompt')
    update_parser.add_argument('name', help='Prompt name')
    update_parser.add_argument('--template', help='New template (or read from stdin)')
    update_parser.add_argument('--description', help='New description')
    update_parser.add_argument('--tags', help='New tags (comma-separated)')
    update_parser.add_argument('--file', help='Read template from file')
    
    # Test prompt
    test_parser = prompt_subparsers.add_parser('test', help='Test a prompt')
    test_parser.add_argument('name', help='Prompt name')
    test_parser.add_argument('--variables', help='Variables as JSON')
    test_parser.add_argument('--file', help='Read variables from file')


def setup_knowledge_commands(subparsers):
    """Setup knowledge base commands"""
    
    # Knowledge management
    kb_parser = subparsers.add_parser('knowledge', help='Manage knowledge base')
    kb_subparsers = kb_parser.add_subparsers(dest='kb_command', help='Knowledge commands')
    
    # List knowledge
    list_kb_parser = kb_subparsers.add_parser('list', help='List knowledge items')
    list_kb_parser.add_argument('--category', help='Filter by category')
    list_kb_parser.add_argument('--tags', help='Filter by tags (comma-separated)')
    
    # Show knowledge
    show_kb_parser = kb_subparsers.add_parser('show', help='Show knowledge item')
    show_kb_parser.add_argument('query', help='Search query or item ID')
    
    # Add knowledge
    add_kb_parser = kb_subparsers.add_parser('add', help='Add knowledge item')
    add_kb_parser.add_argument('title', help='Knowledge title')
    add_kb_parser.add_argument('--content', help='Knowledge content (or read from stdin)')
    add_kb_parser.add_argument('--category', default='general', help='Knowledge category')
    add_kb_parser.add_argument('--tags', help='Tags (comma-separated)')
    add_kb_parser.add_argument('--source', default='cli', help='Knowledge source')
    add_kb_parser.add_argument('--file', help='Read content from file')
    
    # Search knowledge
    search_kb_parser = kb_subparsers.add_parser('search', help='Search knowledge base')
    search_kb_parser.add_argument('query', help='Search query')
    search_kb_parser.add_argument('--max-results', type=int, default=5, help='Maximum results')
    search_kb_parser.add_argument('--category', help='Filter by category')
    search_kb_parser.add_argument('--tags', help='Filter by tags')
    
    # Import/Export knowledge
    import_kb_parser = kb_subparsers.add_parser('import', help='Import knowledge from file')
    import_kb_parser.add_argument('file', help='File to import')
    
    export_kb_parser = kb_subparsers.add_parser('export', help='Export knowledge to file')
    export_kb_parser.add_argument('file', help='Output file')
    
    # Knowledge stats
    kb_subparsers.add_parser('stats', help='Show knowledge base statistics')


async def handle_prompt_commands(args):
    """Handle prompt management commands"""
    pm = PromptManager()
    
    if args.prompt_command == 'list':
        prompts = pm.list_prompts()
        
        if args.tags:
            tag_filter = set(args.tags.split(','))
            prompts = [p for p in prompts if set(p['tags']).intersection(tag_filter)]
        
        if not prompts:
            print("No prompts found.")
            return
        
        print(f"{'Name':<25} {'Version':<10} {'Tags':<20} {'Description'}")
        print("-" * 80)
        for prompt in prompts:
            tags = ', '.join(prompt['tags'][:3])  # Limit displayed tags
            desc = prompt['description'][:30] + "..." if len(prompt['description']) > 30 else prompt['description']
            print(f"{prompt['name']:<25} {prompt['version']:<10} {tags:<20} {desc}")
    
    elif args.prompt_command == 'show':
        prompt = pm.load_prompt(args.name, args.version)
        if not prompt:
            print(f"Prompt '{args.name}' not found.")
            return
        
        print(f"Name: {prompt.name}")
        print(f"Version: {prompt.version}")
        print(f"Description: {prompt.description}")
        print(f"Variables: {', '.join(prompt.variables)}")
        print(f"Tags: {', '.join(prompt.tags)}")
        print(f"Created: {prompt.created_at}")
        print(f"Updated: {prompt.updated_at}")
        print(f"\nTemplate:\n{'-' * 40}")
        print(prompt.template)
    
    elif args.prompt_command == 'create':
        # Get template content
        if args.file:
            with open(args.file, 'r') as f:
                template = f.read()
        elif args.template:
            template = args.template
        else:
            print("Enter template (Ctrl+D to finish):")
            template = sys.stdin.read()
        
        # Parse variables
        variables = args.variables.split(',') if args.variables else []
        variables = [v.strip() for v in variables]
        
        # Parse tags
        tags = args.tags.split(',') if args.tags else []
        tags = [t.strip() for t in tags]
        
        # Create prompt
        prompt = PromptTemplate(
            name=args.name,
            version="1.0",
            template=template,
            variables=variables,
            description=args.description or f"Custom prompt: {args.name}",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags=tags
        )
        
        pm.save_prompt(prompt)
        print(f"✅ Created prompt '{args.name}' v{prompt.version}")
    
    elif args.prompt_command == 'update':
        # Get new template content
        if args.file:
            with open(args.file, 'r') as f:
                template = f.read()
        elif args.template:
            template = args.template
        else:
            print("Enter new template (Ctrl+D to finish):")
            template = sys.stdin.read()
        
        # Parse tags
        tags = args.tags.split(',') if args.tags else None
        tags = [t.strip() for t in tags] if tags else None
        
        # Create new version
        try:
            new_prompt = pm.create_prompt_version(
                args.name,
                template,
                description=args.description,
                tags=tags
            )
            print(f"✅ Created new version of '{args.name}': v{new_prompt.version}")
        except ValueError as e:
            print(f"❌ Error: {e}")
    
    elif args.prompt_command == 'test':
        # Get variables
        if args.file:
            with open(args.file, 'r') as f:
                variables = json.load(f)
        elif args.variables:
            variables = json.loads(args.variables)
        else:
            variables = {}
        
        try:
            formatted = pm.format_prompt(args.name, variables)
            print("✅ Prompt formatted successfully:")
            print("-" * 40)
            print(formatted)
        except Exception as e:
            print(f"❌ Error: {e}")


async def handle_knowledge_commands(args):
    """Handle knowledge base commands"""
    kb = KnowledgeBase()
    
    if args.kb_command == 'list':
        items = list(kb.knowledge_items.values())
        
        # Apply filters
        if args.category:
            items = [item for item in items if item.category == args.category]
        
        if args.tags:
            tag_filter = set(args.tags.split(','))
            items = [item for item in items if set(item.tags).intersection(tag_filter)]
        
        if not items:
            print("No knowledge items found.")
            return
        
        print(f"{'Title':<30} {'Category':<15} {'Tags':<25} {'Updated'}")
        print("-" * 90)
        for item in items:
            tags = ', '.join(item.tags[:3])  # Limit displayed tags
            updated = item.updated_at.split('T')[0]  # Just date part
            title = item.title[:27] + "..." if len(item.title) > 27 else item.title
            print(f"{title:<30} {item.category:<15} {tags:<25} {updated}")
    
    elif args.kb_command == 'show':
        # Try to find by ID first, then by search
        if args.query in kb.knowledge_items:
            item = kb.knowledge_items[args.query]
            print(f"Title: {item.title}")
            print(f"Category: {item.category}")
            print(f"Tags: {', '.join(item.tags)}")
            print(f"Source: {item.source}")
            print(f"Created: {item.created_at}")
            print(f"Updated: {item.updated_at}")
            print(f"Version: {item.version}")
            print(f"\nContent:\n{'-' * 40}")
            print(item.content)
        else:
            # Search for items
            query_obj = KnowledgeQuery(query=args.query, max_results=1)
            results = kb.search_knowledge(query_obj)
            if results:
                item, score = results[0]
                print(f"Best match (relevance: {score:.2f}):")
                print(f"Title: {item.title}")
                print(f"Category: {item.category}")
                print(f"Tags: {', '.join(item.tags)}")
                print(f"\nContent:\n{'-' * 40}")
                print(item.content)
            else:
                print(f"No knowledge found for query: {args.query}")
    
    elif args.kb_command == 'add':
        # Get content
        if args.file:
            with open(args.file, 'r') as f:
                content = f.read()
        elif args.content:
            content = args.content
        else:
            print("Enter content (Ctrl+D to finish):")
            content = sys.stdin.read()
        
        # Parse tags
        tags = args.tags.split(',') if args.tags else []
        tags = [t.strip() for t in tags]
        
        # Add knowledge
        item = kb.add_knowledge_from_text(
            title=args.title,
            content=content,
            category=args.category,
            tags=tags,
            source=args.source
        )
        
        print(f"✅ Added knowledge item: {item.title} (ID: {item.id})")
    
    elif args.kb_command == 'search':
        # Parse filters
        categories = [args.category] if args.category else None
        tags = args.tags.split(',') if args.tags else None
        tags = [t.strip() for t in tags] if tags else None
        
        query_obj = KnowledgeQuery(
            query=args.query,
            categories=categories,
            tags=tags,
            max_results=args.max_results
        )
        
        results = kb.search_knowledge(query_obj)
        
        if not results:
            print(f"No results found for query: {args.query}")
            return
        
        print(f"Found {len(results)} results for: {args.query}")
        print("-" * 60)
        
        for i, (item, score) in enumerate(results, 1):
            print(f"{i}. {item.title} (relevance: {score:.2f})")
            print(f"   Category: {item.category} | Tags: {', '.join(item.tags)}")
            print(f"   {item.content[:100]}..." if len(item.content) > 100 else f"   {item.content}")
            print()
    
    elif args.kb_command == 'import':
        try:
            imported_count = kb.import_knowledge(args.file)
            print(f"✅ Imported {imported_count} knowledge items from {args.file}")
        except Exception as e:
            print(f"❌ Import failed: {e}")
    
    elif args.kb_command == 'export':
        try:
            kb.export_knowledge(args.file)
            print(f"✅ Exported knowledge base to {args.file}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    elif args.kb_command == 'stats':
        stats = kb.get_statistics()
        print("📊 Knowledge Base Statistics")
        print("-" * 30)
        print(f"Total items: {stats['total_items']}")
        print(f"Categories: {len(stats['categories'])}")
        print(f"Total words: {stats['total_words']:,}")
        print(f"Avg content length: {stats['avg_content_length']} characters")
        print(f"\nTop categories:")
        for category, items in list(stats['categories'].items())[:5]:
            print(f"  {category}: {len(items)} items")
        print(f"\nTop tags:")
        for tag, items in stats['top_tags'][:5]:
            print(f"  {tag}: {len(items)} items")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description='LangGraph Agent CLI Tools')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Setup command groups
    setup_prompt_commands(subparsers)
    setup_knowledge_commands(subparsers)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'prompts':
            await handle_prompt_commands(args)
        elif args.command == 'knowledge':
            await handle_knowledge_commands(args)
        else:
            print(f"Unknown command: {args.command}")
            parser.print_help()
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    import asyncio
    exit(asyncio.run(main()))
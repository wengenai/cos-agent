"""
Knowledge Base Management System
Handles custom knowledge that the agent can leverage when needed
"""

import json
import os
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import re


@dataclass
class KnowledgeItem:
    """Represents a single knowledge item"""
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    source: str
    created_at: str
    updated_at: str
    version: int = 1
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class KnowledgeQuery:
    """Represents a knowledge search query"""
    query: str
    categories: List[str] = None
    tags: List[str] = None
    max_results: int = 10
    min_relevance_score: float = 0.1


class KnowledgeBase:
    """Manages custom knowledge for the agent"""
    
    def __init__(self, kb_dir: str = "knowledge_base"):
        self.kb_dir = Path(kb_dir)
        self.kb_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.kb_dir / "items").mkdir(exist_ok=True)
        (self.kb_dir / "categories").mkdir(exist_ok=True)
        (self.kb_dir / "indices").mkdir(exist_ok=True)
        
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.category_index: Dict[str, List[str]] = defaultdict(list)
        self.tag_index: Dict[str, List[str]] = defaultdict(list)
        self.text_index: Dict[str, List[str]] = defaultdict(list)  # Simple text search
        
        self.load_all_knowledge()
        
        # Create default categories if empty
        if not self.knowledge_items:
            self._create_default_knowledge()
    
    def _create_default_knowledge(self):
        """Create some default knowledge items"""
        default_items = [
            KnowledgeItem(
                id=self._generate_id("System Architecture"),
                title="System Architecture Guidelines",
                content="""
                Best practices for system architecture:
                
                1. Separation of Concerns - Each component should have a single responsibility
                2. Loose Coupling - Components should be independently deployable and testable
                3. High Cohesion - Related functionality should be grouped together
                4. Scalability - Design for growth and performance requirements
                5. Security by Design - Security considerations at every layer
                6. Observability - Built-in monitoring, logging, and tracing
                7. Fault Tolerance - Graceful degradation and error recovery
                8. Documentation - Clear documentation for all components
                """,
                category="software_engineering",
                tags=["architecture", "best_practices", "design_patterns"],
                source="internal_guidelines",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            
            KnowledgeItem(
                id=self._generate_id("AI Agent Design"),
                title="AI Agent Design Principles", 
                content="""
                Key principles for designing AI agents:
                
                1. Clear Goal Definition - Agents should have well-defined objectives
                2. State Management - Maintain comprehensive state across interactions
                3. Tool Integration - Seamless integration with external tools and APIs
                4. Error Handling - Robust error recovery and fallback mechanisms
                5. Human Oversight - Ability for human intervention and control
                6. Transparency - Clear reasoning and decision-making processes
                7. Iterative Improvement - Continuous learning and adaptation
                8. Safety Constraints - Built-in safety measures and limitations
                9. Scalability - Design for concurrent and distributed execution
                10. Monitoring - Real-time monitoring of agent behavior and performance
                """,
                category="ai_development", 
                tags=["ai", "agents", "design_principles", "best_practices"],
                source="internal_research",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ),
            
            KnowledgeItem(
                id=self._generate_id("LangGraph Patterns"),
                title="LangGraph Implementation Patterns",
                content="""
                Common patterns for LangGraph applications:
                
                1. Plan-Execute Pattern:
                   - Separate planning and execution phases
                   - Planning creates detailed step-by-step plans
                   - Execution follows plans with dynamic routing
                
                2. Multi-Agent Collaboration:
                   - Specialized agents for different tasks
                   - Message passing between agents
                   - Coordination and orchestration layers
                
                3. State Management:
                   - Comprehensive state schemas
                   - Checkpointing for resumability
                   - State validation and consistency
                
                4. Tool Integration:
                   - Native tool calling
                   - Error handling for tool failures
                   - Tool result validation
                
                5. Human-in-the-Loop:
                   - Breakpoints for human input
                   - Approval workflows
                   - Interactive debugging
                """,
                category="langgraph",
                tags=["langgraph", "patterns", "implementation", "workflows"],
                source="development_experience",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
        ]
        
        for item in default_items:
            self.add_knowledge_item(item)
    
    def _generate_id(self, title: str) -> str:
        """Generate a unique ID for a knowledge item"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_hash = hashlib.md5(title.encode()).hexdigest()[:8]
        return f"kb_{timestamp}_{content_hash}"
    
    def add_knowledge_item(self, item: KnowledgeItem):
        """Add a knowledge item to the base"""
        self.knowledge_items[item.id] = item
        
        # Update indices
        self.category_index[item.category].append(item.id)
        for tag in item.tags:
            self.tag_index[tag].append(item.id)
        
        # Simple text indexing (split content into words)
        words = re.findall(r'\w+', item.content.lower())
        for word in set(words):  # Use set to avoid duplicates
            if len(word) > 2:  # Skip very short words
                self.text_index[word].append(item.id)
        
        # Save to file
        self._save_knowledge_item(item)
    
    def add_knowledge_from_text(self, title: str, content: str, category: str = "general", 
                               tags: List[str] = None, source: str = "user_input") -> KnowledgeItem:
        """Add knowledge from raw text input"""
        if tags is None:
            tags = []
        
        item = KnowledgeItem(
            id=self._generate_id(title),
            title=title,
            content=content,
            category=category,
            tags=tags,
            source=source,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.add_knowledge_item(item)
        return item
    
    def update_knowledge_item(self, item_id: str, **updates) -> bool:
        """Update an existing knowledge item"""
        if item_id not in self.knowledge_items:
            return False
        
        item = self.knowledge_items[item_id]
        old_category = item.category
        old_tags = item.tags.copy()
        
        # Update fields
        for field, value in updates.items():
            if hasattr(item, field):
                setattr(item, field, value)
        
        item.updated_at = datetime.now().isoformat()
        item.version += 1
        
        # Update indices if category or tags changed
        if old_category != item.category:
            self.category_index[old_category].remove(item_id)
            self.category_index[item.category].append(item_id)
        
        # Update tag index
        for old_tag in old_tags:
            if old_tag not in item.tags:
                self.tag_index[old_tag].remove(item_id)
        for new_tag in item.tags:
            if new_tag not in old_tags:
                self.tag_index[new_tag].append(item_id)
        
        # Re-index text content if content changed
        if 'content' in updates:
            self._reindex_text_for_item(item)
        
        # Save updated item
        self._save_knowledge_item(item)
        return True
    
    def delete_knowledge_item(self, item_id: str) -> bool:
        """Delete a knowledge item"""
        if item_id not in self.knowledge_items:
            return False
        
        item = self.knowledge_items[item_id]
        
        # Remove from indices
        self.category_index[item.category].remove(item_id)
        for tag in item.tags:
            self.tag_index[tag].remove(item_id)
        
        # Remove from text index
        words = re.findall(r'\w+', item.content.lower())
        for word in set(words):
            if word in self.text_index and item_id in self.text_index[word]:
                self.text_index[word].remove(item_id)
        
        # Remove from memory and file
        del self.knowledge_items[item_id]
        file_path = self.kb_dir / "items" / f"{item_id}.json"
        if file_path.exists():
            file_path.unlink()
        
        return True
    
    def search_knowledge(self, query: KnowledgeQuery) -> List[Tuple[KnowledgeItem, float]]:
        """Search knowledge base with relevance scoring"""
        candidates = set()
        
        # Collect candidates based on different criteria
        if query.categories:
            for category in query.categories:
                candidates.update(self.category_index.get(category, []))
        
        if query.tags:
            for tag in query.tags:
                candidates.update(self.tag_index.get(tag, []))
        
        # Text search
        query_words = re.findall(r'\w+', query.query.lower())
        for word in query_words:
            candidates.update(self.text_index.get(word, []))
        
        # If no specific criteria, search all items
        if not candidates and not query.categories and not query.tags:
            candidates = set(self.knowledge_items.keys())
        
        # Score and rank results
        results = []
        for item_id in candidates:
            if item_id in self.knowledge_items:
                item = self.knowledge_items[item_id]
                score = self._calculate_relevance_score(item, query)
                if score >= query.min_relevance_score:
                    results.append((item, score))
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Return top results
        return results[:query.max_results]
    
    def _calculate_relevance_score(self, item: KnowledgeItem, query: KnowledgeQuery) -> float:
        """Calculate relevance score for a knowledge item"""
        score = 0.0
        
        # Text relevance (simple word matching)
        query_words = set(re.findall(r'\w+', query.query.lower()))
        content_words = set(re.findall(r'\w+', item.content.lower()))
        title_words = set(re.findall(r'\w+', item.title.lower()))
        
        # Title matches get higher weight
        title_matches = len(query_words.intersection(title_words))
        content_matches = len(query_words.intersection(content_words))
        
        if query_words:
            score += (title_matches / len(query_words)) * 0.4
            score += (content_matches / len(query_words)) * 0.3
        
        # Category matches
        if query.categories:
            if item.category in query.categories:
                score += 0.2
        
        # Tag matches
        if query.tags:
            tag_matches = len(set(query.tags).intersection(set(item.tags)))
            if tag_matches > 0:
                score += (tag_matches / len(query.tags)) * 0.1
        
        return score
    
    def get_relevant_knowledge(self, task: str, max_items: int = 3) -> List[KnowledgeItem]:
        """Get knowledge most relevant to a specific task"""
        query = KnowledgeQuery(
            query=task,
            max_results=max_items,
            min_relevance_score=0.1
        )
        
        results = self.search_knowledge(query)
        return [item for item, score in results]
    
    def get_knowledge_context(self, task: str, max_length: int = 2000) -> str:
        """Get formatted knowledge context for a task"""
        relevant_items = self.get_relevant_knowledge(task)
        
        if not relevant_items:
            return "No specific knowledge available for this task."
        
        context_parts = []
        current_length = 0
        
        for item in relevant_items:
            item_text = f"**{item.title}** (Category: {item.category})\n{item.content}\n\n"
            
            if current_length + len(item_text) > max_length:
                # Truncate if needed
                remaining = max_length - current_length
                if remaining > 100:  # Only add if there's meaningful space
                    item_text = item_text[:remaining-3] + "..."
                    context_parts.append(item_text)
                break
            
            context_parts.append(item_text)
            current_length += len(item_text)
        
        return "\n".join(context_parts)
    
    def _save_knowledge_item(self, item: KnowledgeItem):
        """Save a knowledge item to file"""
        file_path = self.kb_dir / "items" / f"{item.id}.json"
        with open(file_path, 'w') as f:
            json.dump(asdict(item), f, indent=2)
    
    def load_all_knowledge(self):
        """Load all knowledge items from files"""
        items_dir = self.kb_dir / "items"
        if not items_dir.exists():
            return
        
        for file_path in items_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    item = KnowledgeItem(**data)
                    self.knowledge_items[item.id] = item
                    
                    # Rebuild indices
                    self.category_index[item.category].append(item.id)
                    for tag in item.tags:
                        self.tag_index[tag].append(item.id)
                    
                    # Rebuild text index
                    words = re.findall(r'\w+', item.content.lower())
                    for word in set(words):
                        if len(word) > 2:
                            self.text_index[word].append(item.id)
                            
            except Exception as e:
                print(f"Error loading knowledge item from {file_path}: {e}")
    
    def _reindex_text_for_item(self, item: KnowledgeItem):
        """Re-index text content for a specific item"""
        # Remove old text index entries for this item
        for word_list in self.text_index.values():
            if item.id in word_list:
                word_list.remove(item.id)
        
        # Add new text index entries
        words = re.findall(r'\w+', item.content.lower())
        for word in set(words):
            if len(word) > 2:
                self.text_index[word].append(item.id)
    
    def export_knowledge(self, file_path: str):
        """Export all knowledge to a single file"""
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_items": len(self.knowledge_items),
            "categories": list(self.category_index.keys()),
            "items": [asdict(item) for item in self.knowledge_items.values()]
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def import_knowledge(self, file_path: str) -> int:
        """Import knowledge from a file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        imported_count = 0
        for item_data in data.get("items", []):
            try:
                item = KnowledgeItem(**item_data)
                self.add_knowledge_item(item)
                imported_count += 1
            except Exception as e:
                print(f"Error importing knowledge item: {e}")
        
        return imported_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        return {
            "total_items": len(self.knowledge_items),
            "categories": dict(self.category_index),
            "top_tags": sorted(self.tag_index.items(), key=lambda x: len(x[1]), reverse=True)[:10],
            "total_words": sum(len(re.findall(r'\w+', item.content)) for item in self.knowledge_items.values()),
            "avg_content_length": sum(len(item.content) for item in self.knowledge_items.values()) // max(1, len(self.knowledge_items))
        }
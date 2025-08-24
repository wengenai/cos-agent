"""
System Prompt Management Module
Allows easy testing, iteration, and management of system prompts
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


@dataclass
class PromptTemplate:
    """Represents a system prompt template"""
    name: str
    version: str
    template: str
    variables: List[str]
    description: str
    created_at: str
    updated_at: str
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class PromptTestResult:
    """Results from prompt testing"""
    prompt_name: str
    prompt_version: str
    test_input: str
    expected_output: str
    actual_output: str
    success: bool
    score: float
    timestamp: str
    notes: str = ""


class PromptManager:
    """Manages system prompts for easy testing and iteration"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.prompts_dir / "templates").mkdir(exist_ok=True)
        (self.prompts_dir / "tests").mkdir(exist_ok=True)
        (self.prompts_dir / "results").mkdir(exist_ok=True)
        
        self.prompts: Dict[str, PromptTemplate] = {}
        self.load_all_prompts()
        
        # Initialize with default prompts if none exist
        if not self.prompts:
            self._create_default_prompts()
    
    def _create_default_prompts(self):
        """Create default system prompts"""
        default_prompts = {
            "planning_agent": PromptTemplate(
                name="planning_agent",
                version="1.0.0",
                template="""You are a planning agent responsible for creating detailed execution plans.

Task: {task}
Context: {context}

Analyze the task and create a comprehensive execution plan. Consider:
1. What information needs to be gathered
2. What analysis needs to be performed  
3. What tools or resources are required
4. What the expected output should be
5. Potential risks or challenges

Return a JSON plan with this structure:
{{
    "steps": [
        {{"step": 1, "action": "action_name", "description": "what to do", "tools_needed": ["tool1"], "estimated_time": "5 minutes"}},
    ],
    "expected_outcome": "description of expected result",
    "success_criteria": ["criteria1", "criteria2"],
    "risks": ["risk1", "risk2"],
    "priority": "high|medium|low",
    "complexity": "simple|moderate|complex"
}}

Be specific and actionable in your planning.""",
                variables=["task", "context"],
                description="Main planning agent prompt for creating execution plans",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tags=["planning", "core"]
            ),
            
            "execution_coordinator": PromptTemplate(
                name="execution_coordinator", 
                version="1.0.0",
                template="""You are an execution coordinator managing the execution of a plan.

Current Plan: {execution_plan}
Current Step: {current_step}
Step Status: {step_status}
Available Tools: {available_tools}

Your role:
1. Monitor execution progress
2. Decide on next actions based on results
3. Handle errors and exceptions
4. Ensure plan objectives are met

Based on the current state, determine the next action:
- "continue" - proceed to next step
- "retry" - retry current step with modifications
- "escalate" - need human intervention
- "complete" - plan execution finished

Respond with: {{"next_action": "action", "reasoning": "explanation", "modifications": "any changes needed"}}""",
                variables=["execution_plan", "current_step", "step_status", "available_tools"],
                description="Coordinates execution of planned steps",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tags=["execution", "coordination"]
            ),
            
            "research_specialist": PromptTemplate(
                name="research_specialist",
                version="1.0.0", 
                template="""You are a research specialist focused on gathering and synthesizing information.

Research Query: {query}
Knowledge Base: {knowledge_context}
Search Results: {search_results}

Your tasks:
1. Analyze the search results for relevance and reliability
2. Synthesize information from multiple sources
3. Identify gaps in information
4. Provide structured research findings

Consider the provided knowledge base context when evaluating information.

Format your response as:
{{
    "key_findings": ["finding1", "finding2"],
    "sources": [{{"url": "url", "reliability": "high/medium/low", "relevance": "high/medium/low"}}],
    "information_gaps": ["gap1", "gap2"],
    "recommendations": ["next steps for research"],
    "confidence_score": 0.8
}}""",
                variables=["query", "knowledge_context", "search_results"],
                description="Specialized prompt for research and information gathering",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tags=["research", "analysis"]
            ),
            
            "knowledge_integration": PromptTemplate(
                name="knowledge_integration",
                version="1.0.0",
                template="""You are a knowledge integration specialist.

Current Task: {task}
Available Knowledge: {knowledge_base}
External Information: {external_info}

Your role:
1. Integrate provided knowledge with external information
2. Identify relevant knowledge for the current task
3. Resolve any conflicts between sources
4. Provide contextualized recommendations

Knowledge Integration Guidelines:
- Prioritize provided knowledge base when authoritative
- Clearly distinguish between internal knowledge and external sources
- Highlight any contradictions or inconsistencies
- Suggest when additional knowledge might be needed

Response format:
{{
    "relevant_knowledge": ["key knowledge items"],
    "knowledge_gaps": ["areas lacking information"], 
    "integrated_insights": ["combined insights"],
    "recommendations": ["action items"],
    "confidence_level": "high/medium/low",
    "knowledge_source_breakdown": {{"internal": 70, "external": 30}}
}}""",
                variables=["task", "knowledge_base", "external_info"],
                description="Integrates custom knowledge with external information",
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat(),
                tags=["knowledge", "integration"]
            )
        }
        
        for prompt in default_prompts.values():
            self.save_prompt(prompt)
    
    def save_prompt(self, prompt: PromptTemplate):
        """Save a prompt template to file"""
        self.prompts[f"{prompt.name}_v{prompt.version}"] = prompt
        
        file_path = self.prompts_dir / "templates" / f"{prompt.name}_v{prompt.version}.json"
        with open(file_path, 'w') as f:
            json.dump(asdict(prompt), f, indent=2)
    
    def load_prompt(self, name: str, version: str = None) -> Optional[PromptTemplate]:
        """Load a specific prompt template"""
        if version:
            key = f"{name}_v{version}"
        else:
            # Get latest version
            matching_keys = [k for k in self.prompts.keys() if k.startswith(f"{name}_v")]
            if not matching_keys:
                return None
            key = max(matching_keys)  # Assumes version sorting works
        
        return self.prompts.get(key)
    
    def load_all_prompts(self):
        """Load all prompt templates from files"""
        templates_dir = self.prompts_dir / "templates"
        if not templates_dir.exists():
            return
        
        for file_path in templates_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    prompt = PromptTemplate(**data)
                    self.prompts[f"{prompt.name}_v{prompt.version}"] = prompt
            except Exception as e:
                print(f"Error loading prompt from {file_path}: {e}")
    
    def create_prompt_version(self, base_name: str, new_template: str, description: str = "", tags: List[str] = None) -> PromptTemplate:
        """Create a new version of an existing prompt"""
        base_prompt = self.load_prompt(base_name)
        if not base_prompt:
            raise ValueError(f"Base prompt '{base_name}' not found")
        
        # Generate new version number
        existing_versions = [k for k in self.prompts.keys() if k.startswith(f"{base_name}_v")]
        version_numbers = [float(k.split("_v")[1]) for k in existing_versions]
        new_version = f"{max(version_numbers) + 0.1:.1f}" if version_numbers else "1.0"
        
        new_prompt = PromptTemplate(
            name=base_name,
            version=new_version,
            template=new_template,
            variables=base_prompt.variables,
            description=description or f"Updated version of {base_name}",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            tags=tags or base_prompt.tags
        )
        
        self.save_prompt(new_prompt)
        return new_prompt
    
    def format_prompt(self, prompt_name: str, variables: Dict[str, Any], version: str = None) -> str:
        """Format a prompt template with variables"""
        prompt = self.load_prompt(prompt_name, version)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")
        
        try:
            return prompt.template.format(**variables)
        except KeyError as e:
            missing_var = str(e).strip("'")
            raise ValueError(f"Missing variable '{missing_var}' for prompt '{prompt_name}'")
    
    def test_prompt(self, prompt_name: str, test_inputs: List[Dict[str, Any]], 
                   expected_outputs: List[str], version: str = None) -> List[PromptTestResult]:
        """Test a prompt with multiple inputs and expected outputs"""
        results = []
        
        for i, (test_input, expected_output) in enumerate(zip(test_inputs, expected_outputs)):
            try:
                formatted_prompt = self.format_prompt(prompt_name, test_input, version)
                
                # For now, we'll just check if formatting works
                # In a real implementation, you'd run this through the LLM
                actual_output = f"[Formatted prompt - would need LLM execution]\n{formatted_prompt[:200]}..."
                
                # Simple success check (would be more sophisticated with LLM)
                success = len(formatted_prompt) > 0
                score = 1.0 if success else 0.0
                
                result = PromptTestResult(
                    prompt_name=prompt_name,
                    prompt_version=version or "latest",
                    test_input=json.dumps(test_input),
                    expected_output=expected_output,
                    actual_output=actual_output,
                    success=success,
                    score=score,
                    timestamp=datetime.now().isoformat(),
                    notes=f"Test case {i+1}"
                )
                
                results.append(result)
                
            except Exception as e:
                result = PromptTestResult(
                    prompt_name=prompt_name,
                    prompt_version=version or "latest", 
                    test_input=json.dumps(test_input),
                    expected_output=expected_output,
                    actual_output="",
                    success=False,
                    score=0.0,
                    timestamp=datetime.now().isoformat(),
                    notes=f"Error: {str(e)}"
                )
                results.append(result)
        
        # Save test results
        self._save_test_results(prompt_name, results)
        return results
    
    def _save_test_results(self, prompt_name: str, results: List[PromptTestResult]):
        """Save test results to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.prompts_dir / "results" / f"{prompt_name}_test_{timestamp}.json"
        
        results_data = [asdict(result) for result in results]
        with open(file_path, 'w') as f:
            json.dump(results_data, f, indent=2)
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """List all available prompts"""
        return [
            {
                "name": prompt.name,
                "version": prompt.version,
                "description": prompt.description,
                "variables": prompt.variables,
                "tags": prompt.tags,
                "updated_at": prompt.updated_at
            }
            for prompt in self.prompts.values()
        ]
    
    def search_prompts(self, query: str) -> List[PromptTemplate]:
        """Search prompts by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for prompt in self.prompts.values():
            if (query_lower in prompt.name.lower() or 
                query_lower in prompt.description.lower() or
                any(query_lower in tag.lower() for tag in prompt.tags)):
                results.append(prompt)
        
        return results
    
    def get_prompt_stats(self) -> Dict[str, Any]:
        """Get statistics about prompts"""
        return {
            "total_prompts": len(self.prompts),
            "unique_names": len(set(p.name for p in self.prompts.values())),
            "tags": list(set(tag for p in self.prompts.values() for tag in p.tags)),
            "most_recent": max(self.prompts.values(), key=lambda x: x.updated_at).name if self.prompts else None
        }
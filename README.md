# AI-Powered Multi Agent Story Assessment Workflow

Sandbox project for experimenting with Langgraph and the concept of multi-agent workflows. With a particular spin on trying to add in "creative misinterpreation" feedback loop to help crafters of original input prompts for user stories not get lulled into a false assumption that they are providing clear and unambugious direction.

This project implements an intelligent workflow system that provides two main capabilities: Python code generation with review/refactoring, and user story assessment with AWS expertise. It leverages LangChain and various language models to create a multi-agent system that can generate, review, and improve both code and user stories.

The system uses a graph-based workflow architecture where specialized AI agents work together in sequence. For code generation, it employs a three-step process of coding, reviewing, and refactoring. For user stories, it implements a validation workflow with story writing, technical review, and quality assessment specifically focused on AWS implementations.

## Repository Structure
```
.
├── requirements.txt          # Project dependencies including LangChain and graph components
└── src/
    ├── assessor.py          # User story assessment workflow implementation
    └── python_coder.py      # Python code generation and review workflow implementation
```

## Usage Instructions
### Prerequisites
- Python 3.7+
- OpenAI API key (for GPT-4 integration) or Ollama setup (for local model usage)
- Environment variable `OPENAI_API_KEY_AGENT` set with your OpenAI API key

Required packages:
```
langchain-community==0.3.22
langchain-ollama==0.3.2
langchain-openai==0.3.14
langgraph==0.3.34
```

### Installation
1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
# For Linux/MacOS
export OPENAI_API_KEY_AGENT='your-api-key'

# For Windows (PowerShell)
$env:OPENAI_API_KEY_AGENT='your-api-key'
```

### Quick Start
1. For Python code generation:
```python
from src.python_coder import chain

# Generate, review, and refactor code
result = chain.invoke({"input": "Create a function that calculates the factorial of a number"})
print(result.get("code"))        # View generated code
print(result.get("review"))      # View code review
print(result.get("refactored"))  # View refactored code
```

2. For user story assessment:
```python
from src.assessor import chain

# Generate and assess a user story
result = chain.invoke({
    "input": "Trigger a lambda at 2200 hours which adjusts the regional WAF to block all traffic"
})
print(result.get("story"))    # View generated user story
print(result.get("review"))   # View technical review
print(result.get("fakenews")) # View assessment
```

### More Detailed Examples
1. Code Generation Workflow:
```python
# Example task for code generation
task = "Create a function that implements binary search"
result = chain.invoke({"input": task})

# Access different stages of the workflow
generated_code = result.get("code")
code_review = result.get("review")
final_code = result.get("refactored")
```

2. User Story Assessment:
```python
# Example AWS-related task
task = """
Create a CloudWatch event that triggers an EC2 instance start at 9 AM 
and stop at 6 PM on weekdays
"""
result = chain.invoke({"input": task})

# Access workflow outputs
user_story = result.get("story")
technical_review = result.get("review")
assessment = result.get("fakenews")
```

### Troubleshooting
Common issues and solutions:

1. OpenAI API Key Issues
```bash
Error: OpenAI API key not found
Solution: Ensure OPENAI_API_KEY_AGENT environment variable is set correctly
```

2. Ollama Connection Issues
```python
# Check if Ollama is running locally
import requests
try:
    requests.get("http://localhost:11434")
except ConnectionError:
    print("Ollama service not running")
```

3. Memory Issues
- Symptom: Process crashes during large text generation
- Solution: Reduce model temperature or break input into smaller chunks

## Data Flow
The system implements two parallel workflows for code generation and user story assessment, each using a three-stage agent pipeline for generation, review, and refinement.

```ascii
Input Task ─→ [Agent 1] ─→ [Agent 2] ─→ [Agent 3] ─→ Final Output
             (Generate)   (Review)    (Refactor/Assess)
```

Component Interactions:
1. Each agent receives input from the previous stage through the StateGraph
2. Agents communicate using a typed dictionary structure (AgentState)
3. The workflow is sequential with no parallel processing
4. Error handling is managed through the LangChain error handling system
5. State transitions are managed by the langgraph StateGraph
6. All agent interactions are stateless and independent
7. Results are accumulated in the state dictionary as the workflow progresses
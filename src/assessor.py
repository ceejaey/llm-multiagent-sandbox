from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
import os

# 1. Shared State
class AgentState(TypedDict):
    input: str
    story: str
    review: str
    fakenews: str

# 2. Model
api_key = os.getenv('OPENAI_API_KEY_AGENT')
# gpt4 = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0)
gpt4 = ChatOllama(model="gemma3:4b", base_url="http://localhost:11434", temperature=0)



# 3. Create Agent
def create_agent(role: str, instructions: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a {role}. {instructions}"),
        ("human", "{input}")
    ])
    return prompt | gpt4

# 4. Correct Wrapping
def wrap_agent_field(agent, input_field: str, output_field: str):
    return RunnableLambda(lambda state: {"input": state[input_field]}) | agent | RunnableLambda(
        lambda output: {output_field: getattr(output, "content", output)}
    )

# 5. Build Agents
coder = wrap_agent_field(
    create_agent("User Story Writer", "Write Jira user story based on the given requirements."),
    input_field="input",
    output_field="story"
)

reviewer = wrap_agent_field(
    create_agent("Technical Reviewer with high degree of AWS experience", "Review the given user story and suggest improvements."),
    input_field="story",
    output_field="review"
)

refactor = wrap_agent_field(
    create_agent("Developer who misinterprets stories not clearly defined", "Accept the story if well defined. Reject otherwise. Explain decision making."),
    input_field="review",
    output_field="fakenews"
)

# 6. Build Graph
workflow: StateGraph = StateGraph(state_schema=AgentState)
workflow.add_node("writer", coder)
workflow.add_node("reviewer", reviewer)
workflow.add_node("badpenny", refactor)
workflow.set_entry_point("writer")
workflow.add_edge("writer", "reviewer")
workflow.add_edge("reviewer", "badpenny")
workflow.add_edge("badpenny", END)
chain = workflow.compile()

# 7. Invoke
task = "Trigger a lambda at 2200 hours which adjusts the regional WAF to block all traffic. At 0645 hours the lambda should remove this restriction."
result = chain.invoke({"input": task})

# 8. Print Results
print("\n🧾 Final Result State:")
print(result)

print("\n🧮 Story:\n", result.get("story"))
print("\n🧐 Review:\n", result.get("review"))
print("\n🔧 Misinterpretation:\n", result.get("fakenews"))

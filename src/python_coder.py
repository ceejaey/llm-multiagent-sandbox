from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
import os

# 1. Shared State
class AgentState(TypedDict):
    input: str
    code: str
    review: str
    refactored: str

# 2. Model
api_key = os.getenv('OPENAI_API_KEY_AGENT')
gpt4 = ChatOpenAI(model="gpt-4", api_key=api_key, temperature=0)

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
    create_agent("Coder", "Write Python code based on the given requirements."),
    input_field="input",
    output_field="code"
)

reviewer = wrap_agent_field(
    create_agent("Reviewer", "Review the given code and suggest improvements."),
    input_field="code",
    output_field="review"
)

refactor = wrap_agent_field(
    create_agent("Refactor", "Implement the suggested improvements in the code."),
    input_field="review",
    output_field="refactored"
)

# 6. Build Graph
workflow: StateGraph = StateGraph(state_schema=AgentState)
workflow.add_node("coder", coder)
workflow.add_node("reviewer", reviewer)
workflow.add_node("refactor", refactor)
workflow.set_entry_point("coder")
workflow.add_edge("coder", "reviewer")
workflow.add_edge("reviewer", "refactor")
workflow.add_edge("refactor", END)
chain = workflow.compile()

# 7. Invoke
task = "Create a function that calculates the factorial of a number"
result = chain.invoke({"input": task})

# 8. Print Results
print("\n🧾 Final Result State:")
print(result)

print("\n🧮 Generated Code:\n", result.get("code"))
print("\n🧐 Review:\n", result.get("review"))
print("\n🔧 Refactored Code:\n", result.get("refactored"))

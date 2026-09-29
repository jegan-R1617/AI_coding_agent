from typing import TypedDict

from langchain.tools import tool
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command, interrupt

class BookingState(TypedDict):
    flight: str
    price: int
    confirmed: bool

def booking_node(state:BookingState):
    approved=interrupt({
        "question":"Confirm booking",
        "filght":state["flight"],
        "price":state["price"]
    })
    return {"confirmed":approved}

graph=StateGraph(BookingState)
graph.add_node("booking_node",booking_node)
graph.add_edge(START,"booking_node")
graph.add_edge("booking_node",END)

checkpoint=InMemorySaver()

graphh=graph.compile(checkpointer=checkpoint)

config={"configurable":{"thread_id":"123"}}
result=graphh.invoke({
    "flight":"Boeing",
    "price":123456,
    "confirmed":False
},config=config)

print(result["__interrupt__"])

def ask_user_confirmation():
    response=input("confirm booking(yes/no)?").strip().lower()
    return response=="yes"
user_approved=ask_user_confirmation()
if user_approved:
    graphh.invoke(Command(resume=user_approved),config=config)
    print(f"Flight {result["flight"]} has been booked")

else:
    print("Booking Cancelled")

from langchain.agents import create_agent
@tool
def task(agent_name:str, user_content)->str:
    agent=get_agent_registry(agent_name)
    result=agent.invoke({"message":{"role":"user","content":user_content}})

main_agent=create_agent(model=llm,tools=[task],system_prompt="Select")
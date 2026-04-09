from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from tools import search_models, compare_models, calculate_total_cost, query_pdf, get_vehicle_info
from rag import initialize_rag
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Check API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print("🔑 OPENAI_API_KEY found - RAG will use OpenAI embeddings")
else:
    print("⚠️  OPENAI_API_KEY not set - RAG will use fallback embeddings")
    print("   To use OpenAI: Create .env file with OPENAI_API_KEY=sk-...")

# Initialize RAG from PDF
try:
    rag = initialize_rag()
except Exception as e:
    print(f"⚠️  RAG initialization failed: {e}")
    print("   Fallback: Using hard-coded database only")

# 1. Đọc System Prompt
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()

# 2. Khai báo State
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 3. Khởi tạo LLM và Tools
# query_pdf đứng ĐẦU → Agent ưu tiên query PDF trước
# get_vehicle_info để Agent tra cứu xe theo TÊN (không cần budget)
tools_list = [query_pdf, get_vehicle_info, search_models, compare_models, calculate_total_cost]
llm = ChatOpenAI(model="gpt-4o-mini")
llm_with_tools = llm.bind_tools(tools_list)

# 4. Agent Node
def agent_node(state: AgentState):
    messages = state["messages"]
    
    # Chắc chắn SystemMessage luôn ở đầu
    has_system = any(isinstance(msg, SystemMessage) for msg in messages)
    if not has_system:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    response = llm_with_tools.invoke(messages)
    
    # === LOGGING ===
    if response.tool_calls:
        for tc in response.tool_calls:
            print(f"🔧 Gọi tool: {tc['name']}({tc['args']})")
    else:
        print(f"✍️  Trả lời trực tiếp")
        
    return {"messages": [response]}

# 5. Xây dựng Graph với Memory
builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)

tool_node = ToolNode(tools_list)
builder.add_node("tools", tool_node)

# Khai báo edges (LangGraph workflow)
builder.add_edge(START, "agent")  # START → agent
builder.add_conditional_edges("agent", tools_condition)  # agent → tools hoặc END
builder.add_edge("tools", "agent")  # tools → agent (loop back)

# Thêm MemorySaver để lưu context giữa các lần hỏi
memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# 6. Chat loop
if __name__ == "__main__":
    print("=" * 60)
    print("🚗 VinFast AI Advisor – Tư vấn mua xe thông minh")
    print("      (Gõ 'quit' để thoát)")
    print("=" * 60)
    
    # Config xác định session (để lưu memory)
    config = {"configurable": {"thread_id": "main_chat"}}
    
    while True:
        user_input = input("\n👤 Bạn: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            print("\n👋 Tạm biệt! Cảm ơn bạn đã sử dụng VinFast AI Advisor.")
            break
            
        print("\n🤔 AI đang xử lý...")
        result = graph.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)
        final = result["messages"][-1]
        print(f"\n🤖 VinFast AI: {final.content}")
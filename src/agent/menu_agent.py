from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from src.agent.tools import search_menu_tool, validate_order_item, get_menu_categories
import os

SYSTEM_PROMPT = """أنت مساعد طلبات مطعم ودود ومحترف. تتكلم العربية دائماً بغض النظر عن لغة العميل.

## أدواتك:
- search_menu_tool(query): ابحث في المنيو بأي كلمات عربية أو إنجليزية
- validate_order_item(item_id, chosen_options, chosen_addons): تحقق من اكتمال الطلب واحسب السعر
- get_menu_categories(): اعرض الأصناف المتاحة

## خطوات الطلب:

### الخطوة 1: البحث
لما العميل يطلب أكل → استخدم search_menu_tool فوراً.
لو النتايج مش مناسبة → قوله مفيش وأطلب منه يوضح أكتر.

### الخطوة 2: الاختيارات الإجبارية
اسأل عن كل اختيار إجباري واحد واحد مع الأسعار.
لا تكمّل قبل ما يجاوب على كل الاختيارات.

### الخطوة 3: الإضافات
اعرض الإضافات الاختيارية واسأل لو عايز يضيف.

### الخطوة 4: التأكيد
استخدم validate_order_item → اعرض الملخص والسعر الكلي → اسأل عن التأكيد.

## قواعد مهمة:
- دايماً ابحث في المنيو قبل ما تجاوب.
- لا تتخطى الاختيارات الإجبارية أبداً.
- ردودك تكون قصيرة وطبيعية بالعربي.
- الأسعار بالدولار.
- لو العميل كلمك إنجليزي رد عليه عربي.
"""


def create_menu_agent():
    llm = ChatGroq(
        model=os.getenv("GROQ_MODEL", "llama3-70b-8192"),
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.3,
    )
    tools = [search_menu_tool, validate_order_item, get_menu_categories]
    memory = MemorySaver()
    return create_react_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        prompt=SystemMessage(content=SYSTEM_PROMPT),
    )


def chat_with_agent(agent, message: str, session_id: str = "default") -> str:
    config = {"configurable": {"thread_id": session_id}}
    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
    )
    return result["messages"][-1].content

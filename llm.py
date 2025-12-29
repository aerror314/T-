from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, END

from prompt import SYSTEM_PROMPT, TABLE_PROMPT
from state import AgentState
from tool import tools
from spider import Spider
from typing import AsyncGenerator
import asyncio
from os import environ


class LLM:
    def __init__(self, spider):
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            base_url="https://api.deepseek.com",
            api_key=environ["YOUR_API_KEY"],
            temperature=0,
        ).bind_tools(tools)

        self.spider = spider
        self.state: AgentState = {
            "messages": [SystemMessage(SYSTEM_PROMPT), SystemMessage("当前选课阶段为预选阶段。")],
            "table": "",
        }
        self.app = self.init_graph()
        self.admit_user_table = False

    def init_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("agent", self._agent_node)
        workflow.add_node("tools", self._tools_node)
        workflow.add_node("tab", self._tab_node)
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", self._route_tools,{"tools": "tools", "tab": "tab"})
        workflow.add_edge("tools", "agent")
        workflow.add_edge("tab", END)

        return workflow.compile()

    async def _tab_node(self, state: AgentState) -> dict:
        context_messages = state["messages"] + [SystemMessage(TABLE_PROMPT)]
        response = await self.llm.ainvoke(context_messages)

        return {"table": response.content}

    async def _agent_node(self, state: AgentState) -> dict:
        context_messages = state["messages"]
        if self.admit_user_table:
            context_messages += [SystemMessage("用户允许你查看他的选课情况")]
        else:
            context_messages += [SystemMessage("用户不允许你查看他的选课情况")]
        response = await self.llm.ainvoke(context_messages)

        return {"messages": [response]}

    async def _tools_node(self, state: AgentState) -> dict:
        messages = state["messages"]
        last_message = messages[-1]
        tool_messages = []

        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            spider = self.spider
            for tool_call in last_message.tool_calls:
                tool_name = tool_call['name']
                tool_call_id = tool_call['id']

                if tool_name in ["search_course", "search_situation", "search_teacher", "search_user_table"]:
                    if tool_name == "search_user_table" and not self.admit_user_table:
                        error_msg = ToolMessage(
                            content="用户不允许你查看他的选课情况！！！",
                            tool_call_id=tool_call_id,
                        )
                        tool_messages.append(error_msg)
                    tool_func = getattr(spider, tool_name)
                    tool_args = tool_call['args'].copy()

                    # print("tool_name", tool_name, "tool_args", tool_args)

                    try:
                        result_text = tool_func(**tool_args)

                        tool_msg = ToolMessage(
                            content=str(result_text),
                            tool_call_id=tool_call_id
                        )
                        tool_messages.append(tool_msg)

                    except Exception as e:
                        error_msg = ToolMessage(
                            content=f"工具执行出错: {e}",
                            tool_call_id=tool_call_id
                        )
                        tool_messages.append(error_msg)
                else:
                    error_msg = ToolMessage(
                        content=f"错误：未知的工具 '{tool_name}'",
                        tool_call_id=tool_call_id
                    )

                    tool_messages.append(error_msg)
        else:
            print("[DEBUG] execute_tools_node 被调用，但上一条消息没有 tool_calls。")
        for message in tool_messages:
            print("Tool message：", message.content)
        return {
            "messages": tool_messages
        }

    @staticmethod
    async def _route_tools(state: AgentState):
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return "tab"

    async def stream_response(self) -> AsyncGenerator[tuple[str, str], None]:
        config = {"configurable": {"thread_id": f"user_{id(self)}"}, "recursion_limit": 100}
        async for event in self.app.astream_events(self.state, config=config, version="v2"):
            kind = event["event"]
            if kind == "on_chat_model_stream":
                yield event["data"]["chunk"].content, event["metadata"]["langgraph_node"]
            elif kind == "on_chain_end":
                if output := event["data"].get("output"):
                    self.state = output

    def add_message(self, message):
        self.state["messages"].append(HumanMessage(message))


async def test():
    llm = LLM(spider=Spider("2025013622", "dice123456", "2025-2026-2"))

    while True:
        user_input = input("> ")
        llm.add_message(user_input)

        table = ""
        async for message, node in llm.stream_response():
            if node == 'agent':
                print(message, end="")
            elif node == "tab":
                table += message
        print('\n-------------')
        print(table)


if __name__ == "__main__":
    asyncio.run(test())

# 我是一名水木书院大一的学生，本学期我们需要选的课有：中国近现代史纲要，写作与沟通，形势与政策，英语（阅读写作或者听说交流都可以），高等微积分（2），大学物理CE（只能选我们书院开的课），程序设计与计算思维（只能选我们书院开的课）。能帮我规划一下课表吗？

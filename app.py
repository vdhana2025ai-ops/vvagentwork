import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.messages import SystemMessage


web_tool = DuckDuckGoSearchRun()

def web_search(query: str) -> str:
    """Searches the web for current events, facts, or up-to-date information. Use this tool to answer general knowledge questions."""
    print(f"⭐Web Search function called for: '{query}'")
    return web_tool.invoke(query)

#active_tools = [web_search]

st.title('🌍 Venkat AI websearch Agent')
st.write("Ask me anything about current events. I will browse the web to find the answer.")

# 1. Sidebar Configuration
with st.sidebar:
    st.header('⚙️ System Config')
    user_api_key = "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"
    # st.text_input('Groq API Key:', type='password')
    st.info('Equipped with: DuckDuckGo Web Search Tool')
    # Active toggle value
    enable_search = st.toggle('Enable Web Search', value=True)

# 2. The Memory
if 'messages' not in st.session_state:
    st.session_state.messages = []

# 3. Draw the Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg['role']):
        st.markdown(msg['content'])

# 4. The CORE Agentic AI Loop:
if user_query := st.chat_input("Ask about today's news..."):

    #if not user_api_key:
    #   st.error('Please enter your API Key in the sidebar')

#    else:
        # A. Display the user message instantly
        st.session_state.messages.append({'role': 'user', 'content': user_query})
        with st.chat_message('user'):
            st.markdown(user_query)

        # Determine active tools based on toggle state
        active_tools = [web_search] if enable_search else []

        # Initialise the LLM and the Langgraph Agent
        llm = ChatGroq(temperature=0, model_name='llama-3.3-70b-versatile', api_key = user_api_key)
        llm = llm.bind_tools(active_tools)

        if enable_search:
            llm = llm.bind_tools(active_tools)

        # Dynamically change the system prompt depending on the toggle
        if enable_search:
          system_prompt_text = """
                            You are a live research assistant. You MUST use the web search tool to find the current information
                            before answering. Answer the query clearly.
                             """
        else:
          system_prompt_text = """
                            You are in offline mode, so just answer "Web Search is disabled".
                             """

        system_message = SystemMessage(content=system_prompt_text)

        agent = create_react_agent(llm, active_tools, prompt=system_message)

        # C. The Bridge: Translate streamlit memory -> Langgraph Memory
        # Streamlit stores messages as - "user", "assistant"
        # Langgraph stores messsages as "HumanMessage", "AIMessage"
        langgraph_history = []

        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                langgraph_history.append(HumanMessage(content=msg['content']))

            else:
                langgraph_history.append(AIMessage(content=msg['content']))

        # D. Execute the Agent (with a visual loading spinner)
        with st.chat_message('assistant'):
            with st.spinner("🤖 Browsing the web and analyzing results..."):

                # We feed the translated history into the graph
                result_state = agent.invoke({'messages': langgraph_history})

                # The final answer, which is the last message
                bot_answer = result_state['messages'][-1].content

            st.markdown(bot_answer)

        # E. Save the final answer back into streamlit memory
        st.session_state.messages.append({"role": "assistant", "content": bot_answer})

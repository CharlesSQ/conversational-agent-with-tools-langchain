import time
import os
from config import OPENAI_API_KEY

from langchain.memory import ConversationBufferWindowMemory
from langchain import LLMMathChain
from langchain.chat_models import ChatOpenAI
from langchain.agents import LLMSingleActionAgent, AgentExecutor, Tool
from langchain import LLMChain
from output_parser import CustomOutputParser1, CustomOutputParser2
from prompt_template import CustomPromptTemplate
from langchain.chains import ConversationChain
from prompts import TEMPLATE_INSTRUCTIONS_1, TEMPLATE_INSTRUCTIONS_2, SUFFIX
from tools import LLMChatChain

# Set API key for OpenAI
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
print('API key set')

# Set OpenAI LLM and embeddings
llm_chat = ChatOpenAI(temperature=0.9, max_tokens=150,
                      model='gpt-3.5-turbo-0613', client='')

# Set conversation memory buffer
memory = ConversationBufferWindowMemory(memory_key="history", k=5)

print('Memory buffer set')

# Set tools
llm_math_chain = LLMMathChain.from_llm(llm=llm_chat)
# conversation = LLMChatChain(
#     llm=llm_chat, memory=memory)
tools = [
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math",
        # return_direct=True,
    ),
    # Tool(
    #     name="chat",
    #     func=conversation.respond_to_user,
    #     description="useful for when you need to respond to user utterance without using other tools. use the question as the input",
    #     return_direct=True
    # )
]

# Set up prompt template
prompt = CustomPromptTemplate(
    prefix='',
    instructions=TEMPLATE_INSTRUCTIONS_2,
    sufix='',
    tools=tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=["input", "intermediate_steps", "history"]
)

# Set up output parser
output_parser = CustomOutputParser2()

# Set up the agent
llm_chain = LLMChain(llm=llm_chat, prompt=prompt)
tool_names = [tool.name for tool in tools]
agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:"],
    allowed_tools=tool_names,
)
agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent, tools=tools, max_iterations=3, memory=memory)


def main():
    user_prompt = input("Usuario: ")
    response = agent_executor.run(user_prompt)
    print('Assistant: ' + response)


if __name__ == '__main__':
    while True:
        main()
        time.sleep(1)

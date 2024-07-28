from langchain_core.prompts.prompt import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from typing import Tuple, List


# Condense a chat history and follow-up question into a standalone question
def template():

    _template= """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question,
    in its original language.
    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""  # noqa: E501
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

    return CONDENSE_QUESTION_PROMPT


def _format_chat_history(chat_history: List[Tuple[str, str]]) -> List:

    buffer = []
    for human, ai in chat_history:
        buffer.append(HumanMessage(content=human))
        buffer.append(AIMessage(content=ai))

    return buffer

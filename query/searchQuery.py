from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
import history
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI


def _search_query_create():

    return RunnableBranch(
        # If input includes chat_history, we condense it with the follow-up question
        (
            RunnableLambda(lambda x: bool(x.get("chat_history"))).with_config(
                run_name="HasChatHistoryCheck"
            ),  # Condense follow-up question and chat into a standalone_question
            RunnablePassthrough.assign(chat_history=lambda x: history.
                                       _format_chat_history(x["chat_history"]))
            | history.template()
            | ChatOpenAI(temperature=0)
            | StrOutputParser(),
        ),
        # Else, we have no chat history, so just pass through the question
        RunnableLambda(lambda x: x["question"]),
    )

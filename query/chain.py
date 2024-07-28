from dotenv import load_dotenv
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.graphs import Neo4jGraph
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableBranch, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from vector import index
from structuredRetriever import structured_retriever
import history
from langchain_community.callbacks import get_openai_callback


def chain(user_question):

    load_dotenv()
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    NEO4J_URI = os.environ.get('NEO4J_URI')
    NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME')
    NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD')
    graph = Neo4jGraph()

    UNSTRUCTURE_DATA_LIMIT = os.getenv("UNSTRUCTURE_DATA_LIMIT")
    MODEL_NAME = os.getenv("MODEL_NAME")

    print(f"NEO4J_URI:{NEO4J_URI}")
    # if (NEO4J_URI == "bolt://192.168.1.241:7689"):
    #     print("非固定節點")
    # else:
    #     print("固定節點")

    llm = ChatOpenAI(temperature=0, model_name=MODEL_NAME)

    # 建立索引 & 索引器
    vector_index = index()

    # 創建一個 "entity" 全文索引，是根據帶有 __Entity__ 標籤的節點裡 id 屬性創建
    graph.query(
        "CREATE FULLTEXT INDEX entity IF NOT EXISTS FOR (e:__Entity__) ON EACH [e.id]"
    )

    def retriever(question: str):
        # print(f"Search query: {question}")

        structured_data = structured_retriever(question)

        unstructured_data = [
            el.page_content for el in vector_index.similarity_search(
                question, k=int(UNSTRUCTURE_DATA_LIMIT))
        ]

        final_data = f"""Structured data:
    {structured_data}
    Unstructured data:
    {"#Document ". join(unstructured_data)}
        """
        # print(f"input: {final_data}")
        return final_data

    _search_query = RunnableBranch(
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

    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    Use natural language and be concise.
    Please use Traditional Chinese.
    當問題中的人名正確再回答。
    我要文章中確實的答案。
    提供我相關的source，並整理在答案下面，如:資料來源: 1.日期,...(提供部分內文)  2.日期,...(提供部分內文)。
    如無答案，則不用提供資料來源。
    由於提供的 content 是根據問題在資料庫中檢索到的，有關統計或需了解全部資料才能回答的問題，請勿回答。
    Answer:"""
    prompt = ChatPromptTemplate.from_template(template)

    def inspect(state):
        # print(state['context'])
        return state

    chain = (RunnableParallel({
        "context": _search_query | retriever,
        "question": RunnablePassthrough(),
    })
             | RunnableLambda(inspect)
             | prompt
             | llm
             | StrOutputParser())

    with get_openai_callback() as cb:

        print(f"question: {user_question}\n")

        result = chain.invoke({"question": user_question})
        query = retriever(user_question)

        response = {"query": query, "answer": result}
        print(f"query: {query}\n")
        print(f"answer: {result}\n")
        print(cb)

        return response

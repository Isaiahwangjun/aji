from dotenv import load_dotenv
import os
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from entityChain import extract_question

load_dotenv()
openai_api_key = os.environ.get('OPENAI_API_KEY')
NEO4J_URI = os.environ.get('NEO4J_URI')
NEO4J_USERNAME = os.environ.get('NEO4J_USERNAME')
NEO4J_PASSWORD = os.environ.get('NEO4J_PASSWORD')
graph = Neo4jGraph()

QUERY_SIMILARITY = os.getenv("QUERY_SIMILARITY")
STRUCTURE_DATA_LIMIT = os.getenv("STRUCTURE_DATA_LIMIT")
MODEL_NAME = os.getenv("MODEL_NAME")

llm = ChatOpenAI(temperature=0, model_name=MODEL_NAME)

# entity_chain 會把使用者問題中的人物，組織擷取出來
entity_chain = extract_question(llm=llm)


def structured_retriever(question: str) -> str:
    """
    Collects the neighborhood of entities mentioned
    in the question
    """
    result = ""
    entities = entity_chain.invoke({"question": question})
    print(entities)
    for entity in entities.names:
        response = graph.query(
            """
                CALL db.index.fulltext.queryNodes('entity', $query, {limit:$QUERY_SIMILARITY})
                YIELD node, score
                WITH collect(node) AS nodes
                UNWIND nodes AS queryNode
                MATCH (queryNode)-[r:!MENTIONS]-(neighbor)
                WITH queryNode, r, type(r) AS relationship_type, neighbor, keys(r) AS output2, [prop in keys(r) | r[prop]] AS values
                RETURN 
                    CASE
                        WHEN startNode(r) = queryNode THEN queryNode.id + ' - ' + relationship_type + ' -> ' + neighbor.id
                        ELSE neighbor.id + ' - ' + relationship_type + ' -> ' + queryNode.id
                    END AS output,
                    output2,
                    values
                LIMIT $STRUCTURE_DATA_LIMIT
            """, {
                "query": entity,
                "QUERY_SIMILARITY": int(QUERY_SIMILARITY),
                "STRUCTURE_DATA_LIMIT": int(STRUCTURE_DATA_LIMIT)
            })

        response = [el for el in response if el['output'] is not None]
        # result += "\n".join([el['output'] for el in response])
        for el in response:
            output = el['output'] if el['output'] is not None else ''
            values = ', '.join([
                f'{k}: {v}' for k, v in zip(el['output2'], el['values'])
            ]) if el['values'] is not None else ''
            if output:
                result += output
            if values:
                result += ', ' + values
            result += '\n'
    return result

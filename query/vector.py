from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Neo4jVector


def index():

    vector_index = Neo4jVector.from_existing_graph(
        embedding=OpenAIEmbeddings(),
        search_type="hybrid",
        node_label="Document",
        text_node_properties=["text", "source"],
        embedding_node_property="embedding")

    return vector_index


# 此檔為建立兩個索引，分別為 "全文索引" & "向量索引"，可加速查詢。

# 全文索引
# 資料庫裡會有固定的節點 "Document"，裡面的屬性 "text" 存放原始資料，
# 也就是所有的節點都是根據原始資料來建立的。
# 在查詢時會先匹配 Document's text，有匹配成功才會根據此 document 相連的點來查詢

# 向量索引
# 節點 "Document"，裡面的屬性 "text" 經過 embedding 後，儲存在"embedding"屬性，
# 此屬性可用來向量搜尋

# in neo4j show index 可看到類似如下
# name		 type	     entityType	 labelsOrTypes	 properties	     indexProvider
# "keyword"	 "FULLTEXT"	 "NODE"	     ["Document"]	 ["text"]	     "fulltext-1.0"
# "vector"	 "VECTOR"	 "NODE"	     ["Document"]	 ["embedding"]	 "vector-2.0"

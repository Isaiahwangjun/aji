from neo4j import GraphDatabase


def createSource(uri, user, password):

    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        session.run("""
            MATCH ()<-[r]-(n:Document)
            SET r.source = n.source
        """)
    driver.close()

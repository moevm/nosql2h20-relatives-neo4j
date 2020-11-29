from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

import logging
import datetime


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.label = None
        self.relativeRelation = "DirectRelative"

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def set_label(self, label):
        self.label = label

    def get_family_graph_nodes(self, limit):
        with self.driver.session() as session:
            query = (
                "MATCH p=() - [r:DirectRelative]->() "
                "RETURN p LIMIT %i " % limit
            )
            res = session.run(query)
            family = []
            try:
                for r in res:
                    for a in r["p"]:
                        for b in a.nodes:
                            family.append(
                                {
                                    b["id"]: [
                                        b["firstName"],
                                        b["lastName"],
                                        b["middleName"],
                                        b["bornDate"],
                                        b["socialStatus"]
                                    ]
                                }
                            )
                # Capture any errors along with the query and data for traceability
            except ServiceUnavailable as exception:
                logging.error("{query} raised an error: \n {exception}".format(
                    query=query, exception=exception))
                raise
            return family

    def create_node(self, firstName, lastName, middleName, bornDate, socialStatus):
        with self.driver.session() as session:
            query = (
                "CREATE (n:%s {firstName: $fn, lastName: $ln, middleName: $mn, "
                "bornDate: $bd, socialStatus: $ss}) "
                "SET n.id = id(n) " % self.label
            )
            session.run(query, fn=firstName, ln=lastName, mn=middleName,
                        bd=bornDate, ss=socialStatus)

    def remove_node(self, nodeId):
        with self.driver.session() as session:
            query = (
                "MATCH (n:%s { id: $id }) "
                "DELETE n " % self.label
            )
            session.run(query, id=nodeId)

    def create_relation(self, nodeIdOne, nodeIdTwo):
        with self.driver.session() as session:
            query = (
                "MATCH (a:%s), (b:%s) "
                "WHERE a.id = %i AND b.id = %i "
                "CREATE (a)-[: %s]->(b) "
                "RETURN a,b " % (self.label, self.label,
                                 nodeIdOne, nodeIdTwo,
                                 self.relativeRelation)
            )
            session.run(query)

    def remove_relation(self, nodeIdOne, nodeIdTwo):
        with self.driver.session() as session:
            query = (
                "MATCH (n:%s {id: $id1})-[r: %s]-(m:%s {id: $id2}) "
                "DELETE r " % (self.label, self.relativeRelation, self.label)
            )
            session.run(query, id1=nodeIdOne, id2=nodeIdTwo)



if __name__ == "__main__":
    # See https://neo4j.com/developer/aura-connect-driver/ for Aura specific connection URL.
    scheme = "bolt"  # Connecting to Aura, use the "neo4j+s" URI scheme
    host_name = "127.0.0.1"
    port = 7687
    url = "{scheme}://{host_name}:{port}".format(scheme=scheme, host_name=host_name, port=port)
    user = "neo4j"
    password = "123456"
    app = App(url, user, password)
    app.set_label(label="Давыдовы")

    # Создаем узле, по умолчанию айди будет 0 если база пустая
    #app.create_node(firstName="Анатолий", lastName="Давыдов", midleName="Николаевич",
    #                socialStatus="менеджер", bornDate=datetime.datetime(1973, 11, 26))
    #app.create_node(firstName="Александр", lastName="Давыдов", midleName="Анатольевич",
    #                socialStatus="ученик-студент", bornDate=datetime.datetime(1973, 11, 26))
    #app.create_relation(4, 5)
    print(app.get_family_graph_nodes(limit=5))

    # Удаляем узел с айди узла 0
    app.remove_node(nodeId=0)

    app.close()
from neo4j import GraphDatabase

import logging
import datetime


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.label = None

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def set_label(self, label):
        self.label = label

    def create_node(self, firstName, lastName, midleName, bornDate, socialStatus):
        with self.driver.session() as session:
            query = (
                "CREATE (n:%s {firstName: $fn, lastName: $ln, middleName: $mn, "
                "bornDate: $bd, socialStatus: $ss}) "
                "SET n.id = id(n) " % self.label
            )
            session.run(query, fn=firstName, ln=lastName, mn=midleName,
                        bd=bornDate, ss=socialStatus)

    def remove_node(self, nodeId):
        with self.driver.session() as session:
            query = (
                "MATCH (n:%s { id: $id }) "
                "DELETE n " % self.label
            )
            session.run(query, id=nodeId)


if __name__ == "__main__":
    # See https://neo4j.com/developer/aura-connect-driver/ for Aura specific connection URL.
    scheme = "bolt"  # Connecting to Aura, use the "neo4j+s" URI scheme
    host_name = "127.0.0.1"
    port = 7687
    url = "{scheme}://{host_name}:{port}".format(scheme=scheme, host_name=host_name, port=port)
    user = "neo4j"
    password = "123456"
    app = App(url, user, password)
    app.set_label(label="FamilyDavydo")

    # Создаем узле, по умолчанию айди будет 0 если база пустая
    app.create_node(firstName="Анатолий", lastName="Давыдов", midleName="Николаевич",
                    socialStatus="менеджер", bornDate=datetime.datetime(1973, 11, 26))

    # Удаляем узел с айди узла 0
    app.remove_node(nodeId=0)

    app.close()
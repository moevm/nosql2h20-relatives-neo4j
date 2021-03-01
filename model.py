from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
import os
import logging
import json


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.label = None
        self.relativeRelation = "PARENT"

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()

    def set_label(self, label):
        self.label = label

    def get_database(self):
        with self.driver.session() as session:
            query = (
                "MATCH (n) RETURN n"
            )
            result = session.run(query).data()
            nodes = []
            try:
                for n in result:
                    nodes.append(n['n'])
            except ServiceUnavailable as exception:
                logging.error("{query} raised an error: \n {exception}".format(
                    query=query, exception=exception))
                raise

        with self.driver.session() as session:
            query = (
                "MATCH (n)-[:%s]->(c) RETURN n, c" % self.relativeRelation
            )
            result = session.run(query).data()
            relations = []
            try:
                for relation in result:
                    relations.append(relation['n']['id'])
                    relations.append(relation['c']['id'])
            except ServiceUnavailable as exception:
                logging.error("{query} raised an error: \n {exception}".format(
                    query=query, exception=exception))
                raise

        return nodes, relations

    def get_family_graph_nodes(self, limit):
        with self.driver.session() as session:
            query = (
                "MATCH p=() - [r: %s]->() "
                "RETURN p LIMIT %i " % (self.relativeRelation,
                                        limit)
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
                                        b["name"],
                                        b["lastName"],
                                        b["middleName"],
                                        b["bornDate"],
                                        b["sex"],
                                        b["educ"],
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

    def create_node(self, name, lastName, middleName, bornDate, sex, educ, socialStatus):
        with self.driver.session() as session:
            query = (
                "CREATE (n:%s {name: $fn, lastName: $ln, middleName: $mn, "
                "bornDate: $bd, sex: $sx, educ: $ed, socialStatus: $ss}) "
                "SET n.id = id(n) " % self.label
            )
            session.run(query, fn=name, ln=lastName, mn=middleName,
                        bd=bornDate, sx=sex, ed=educ, ss=socialStatus)

    def remove_node(self, nodeId):
        with self.driver.session() as session:
            query = (
                "MATCH (n:%s) "
                "WHERE ID(n) = $id "
                "DETACH DELETE n " % self.label
            )
            session.run(query, id=nodeId)

    def get_relation(self, nodeIdOne, nodeIdTwo):
        with self.driver.session() as session:
            query = (
                "MATCH (a:%s)-[:%s]->(b:%s) "
                "WHERE ID(a) = %i AND ID(b) = %i "
                "RETURN a,b " % (self.label, self.relativeRelation, self.label, nodeIdOne, nodeIdTwo)
            )
            return session.run(query).data()

    def create_relation(self, nodeIdOne, nodeIdTwo):
        with self.driver.session() as session:
            query = (
                "MATCH (a:%s), (b:%s) "
                "WHERE ID(a) = %i AND ID(b) = %i "
                "CREATE (a)-[:%s]->(b) "
                "RETURN a,b " % (self.label, self.label,
                                 nodeIdOne, nodeIdTwo,
                                 self.relativeRelation)
            )
            return session.run(query)

    def remove_relation(self, nodeIdOne, nodeIdTwo):
        with self.driver.session() as session:
            query = (
                "MATCH (a:%s)-[r:%s]-(b:%s) "
                "WHERE ID(a) = $id1 AND ID(b) = $id2 "
                "DELETE r " % (self.label, self.relativeRelation, self.label)
            )
            session.run(query, id1=nodeIdOne, id2=nodeIdTwo)

    # скачать apoc в папку neo4j/plugins
    # установить значения в true для эксорта/импорта в neo4j.conf
    def get_json(self):
        with self.driver.session() as session:
            # экспорт в папку tmp
            query = (
                "CALL apoc.export.json.all(\"/tmp/all.json\",{})"
            )
            os.system('cp /tmp/all.json ./')
            print(json.dumps(session.run(query).data()))
            return session.run(query).data()

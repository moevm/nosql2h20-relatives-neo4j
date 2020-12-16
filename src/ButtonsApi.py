from PyQt5 import uic, QtWidgets
from model import App

Form, _ = uic.loadUiType("gui/createNode.ui")

scheme = "bolt"  # Connecting to Aura, use the "neo4j+s" URI scheme
host_name = "127.0.0.1"
port = 7687
url = "{scheme}://{host_name}:{port}".format(scheme=scheme, host_name=host_name, port=port)
user = "neo4j"
password = "ybrbnfbugaga1999"


class NodeCreator(QtWidgets.QMainWindow, Form):
    def __init__(self):
        super(NodeCreator, self).__init__()
        self.setupUi(self)
        self.btnCreateNode.clicked.connect(self.createNode)

        self.lastName = ''
        self.name = ''
        self.middleName = ''
        self.bornDate = ''
        self.status = ''
        self.app = App(url, user, password)
        self.app.set_label("Person")

    def createNode(self):
        self.lastName = self.lineLastName.text()
        self.name = self.lineName.text()
        self.middleName = self.lineMiddleName.text()
        self.bornDate = self.dateEdit.text()
        self.status = self.lineStatus.text()

        if self.checkInput():
            # отправляем в БД
            self.app.create_node(self.name, self.lastName, self.middleName, self.bornDate, self.status)
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, 'Предупреждение', 'Для добавления узла необходимо заполнить все поля')

    def checkInput(self):
        if self.lastName == '' or self.name == '' or self.middleName == '' or self.status == '':
            return False
        else:
            return True


class DatabaseGetter:
    def __init__(self):
        self.app = App(url, user, password)
        self.app.set_label("Person")

    def getDatabase(self):
        return self.app.get_database()


class NodeDeleter:
    def __init__(self):
        self.app = App(url, user, password)
        self.app.set_label("Person")

    def deleteNode(self, node_id):
        self.app.remove_node(node_id)

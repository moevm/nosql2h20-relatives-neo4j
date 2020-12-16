import sys
from PyQt5 import uic, QtWidgets, QtCore
from ButtonsApi import NodeCreator, DatabaseGetter, NodeDeleter

Form, _ = uic.loadUiType("gui/main.ui")


class Ui(QtWidgets.QMainWindow, Form):
    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)

        # table properties
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 150)

        # connect buttons
        self.btnOpenTree.clicked.connect(self.displayDatabase)
        self.btnCreateNode.clicked.connect(self.createNode)
        self.btnDeleteNode.clicked.connect(self.deleteNode)
        self.btnCreateRelations.clicked.connect(self.createRelation)
        self.btnDeleteRelations.clicked.connect(self.deleteRelation)

        # properties
        self.database = None
        self.nodeCreator = None
        self.nodeDeleter = None

        # view database
        self.displayDatabase()

    # button 'Показать в виде таблицы'
    def displayDatabase(self):
        self.database = DatabaseGetter().getDatabase()
        if self.database is None:
            return
        self.writeDatabaseInTable()

    # button 'Создать узел'
    def createNode(self):
        self.nodeCreator = NodeCreator()
        self.nodeCreator.show()

    # button 'Удалить узел'
    def deleteNode(self):
        self.nodeDeleter = NodeDeleter()
        self.nodeDeleter.deleteNode(int(self.table.takeItem(self.table.currentItem().row(), 0).text()))
        self.displayDatabase()

    # button 'Создать связь'
    def createRelation(self):
        print('test3')

    # button 'Удалить связь'
    def deleteRelation(self):
        print('test3')

    def writeDatabaseInTable(self):
        if self.database is None:
            return None

        # заполнение таблицы
        self.table.setRowCount(len(self.database))
        for i in range(len(self.database)):
            node = self.database[i]
            self.table.setItem(i, 0, QtWidgets.QTableWidgetItem(str(node['id'])))
            self.table.setItem(i, 1, QtWidgets.QTableWidgetItem(node['lastName'] + ' ' + node['name'] + ' '
                                                                + node['middleName']))
            self.table.setItem(i, 2, QtWidgets.QTableWidgetItem(node['bornDate']))
            self.table.setItem(i, 3, QtWidgets.QTableWidgetItem(node['socialStatus']))

        # выравнивание по центру столбцов ID и Дата рождения
        for i in range(self.table.rowCount()):
            self.table.item(i, 0).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.table.item(i, 2).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Ui()
    w.show()
    sys.exit(app.exec_())

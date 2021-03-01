import sys
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from ButtonsApi import NodeCreator, DatabaseGetter, NodeDeleter, RelationsApi, ImportExport

Form, _ = uic.loadUiType("gui/main.ui")


class Ui(QtWidgets.QMainWindow, Form):
    def __init__(self):
        super(Ui, self).__init__()
        self.setupUi(self)

        # table properties
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 300)
        self.table.setColumnWidth(2, 150)
        self.table.setColumnWidth(3, 250)

        # connect buttons
        self.btnOpenTree.clicked.connect(self.displayDatabase)
        self.btnCreateNode.clicked.connect(self.createNode)
        self.btnDeleteNode.clicked.connect(self.deleteNode)
        self.btnCreateRelations.clicked.connect(self.createRelation)
        self.btnDeleteRelations.clicked.connect(self.deleteRelation)
        self.btnExport.clicked.connect(self.export_json)
        self.btnStatistics.clicked.connect(self.displayStatistics)
        

        # properties
        self.database = None
        self.relations = None
        self.nodeCreator = None
        self.nodeDeleter = None
        self.relationsApi = None

        # view database
        self.displayDatabase()

    # button 'Показать в виде таблицы'
    def displayDatabase(self):
        self.database, self.relations = DatabaseGetter().getDatabase()
        if self.database is None:
            return
        self.writeDatabaseInTable()

    # button 'Статистика'
    def displayStatistics(self):
        self.displayDatabase()
    
        
    # button 'Создать узел'
    def createNode(self):
        self.nodeCreator = NodeCreator(self)
        self.nodeCreator.show()

    # button 'Удалить узел'
    def deleteNode(self):
        self.nodeDeleter = NodeDeleter()
        ids = self.getSelectedNodes()

        if len(ids) == 0:
            QtWidgets.QMessageBox.information(self, 'Информация',
                                              'Для удаления узла необходимо выделить соответствующую строку или ячейку')
            return

        # если пользователь отказался удалять все выбранные узлы
        if len(ids) > 1 and self.openMessageBoxForDeleteFewNodes() is False:
            return

        for row in self.table.selectedItems():
            if self.table.item(row.row(), 0).text() in ids:
                self.nodeDeleter.deleteNode(int(self.table.item(row.row(), 0).text()))

        self.displayDatabase()

    # button 'Создать связь'
    def createRelation(self):
        self.relationsApi = RelationsApi()
        ids = self.getSelectedNodes()

        if len(ids) != 2:
            QtWidgets.QMessageBox.warning(self, 'Предупреждение', 'Для создания связи необходимо выбрать только 2 узла')
            return

        # если уже есть связь в любую сторону
        if len(self.relationsApi.checkRelation(ids[0], ids[1])) != 0 or \
                len(self.relationsApi.checkRelation(ids[1], ids[0])) != 0:
            QtWidgets.QMessageBox.warning(self, 'Предупреждение', 'Узлы уже связаны')
            return

        ids = self.openMessageBoxForCreateRelation(ids)
        self.relationsApi.createRelation(ids[0], ids[1])
        self.displayDatabase()

    # button 'Удалить связь'
    def deleteRelation(self):
        self.relationsApi = RelationsApi()
        ids = self.getSelectedNodes()

        if len(ids) != 2:
            QtWidgets.QMessageBox.warning(self, 'Предупреждение', 'Для создания связи необходимо выбрать только 2 узла')
            return

        relation1 = self.relationsApi.checkRelation(ids[0], ids[1])
        relation2 = self.relationsApi.checkRelation(ids[1], ids[0])

        if len(relation1) == 0 and len(relation2) == 0:
            QtWidgets.QMessageBox.warning(self, 'Предупреждение', 'Узлы не связаны')
            return

        if len(relation1) != 0:
            self.relationsApi.deleteRelation(ids[0], ids[1])
        elif len(relation2) != 0:
            self.relationsApi.deleteRelation(ids[1], ids[0])

        self.displayDatabase()

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

        # очистка столбца "дети"
        for row in range(self.table.rowCount()):
            self.table.setItem(row, 4, None)

        # заполнение детей в таблице
        for i in range(0, len(self.relations), 2):
            for row in range(self.table.rowCount()):
                if self.table.item(row, 0).text() == str(self.relations[i]):
                    prev_item = self.table.item(row, 4)
                    if prev_item is None:
                        self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(str(self.relations[i + 1])))
                    else:
                        self.table.setItem(row, 4, QtWidgets.QTableWidgetItem(prev_item.text() + ', ' +
                                                                              str(self.relations[i + 1])))

        # выравнивание по центру столбцов ID и Дата рождения
        for i in range(self.table.rowCount()):
            self.table.item(i, 0).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
            self.table.item(i, 2).setTextAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)

    def openMessageBoxForDeleteFewNodes(self):
        box = QtWidgets.QMessageBox()
        box.setWindowTitle('Удаление узлов')
        box.setText('Вы уверенны, что хотите удалить ВСЕ выбранные узлы?')
        box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        button_yes = box.button(QtWidgets.QMessageBox.Yes)
        button_no = box.button(QtWidgets.QMessageBox.No)
        box.exec_()

        if box.clickedButton() == button_yes:
            return True
        elif box.clickedButton() == button_no:
            return False

    def openMessageBoxForCreateRelation(self, ids):
        box = QtWidgets.QMessageBox()
        box.setWindowTitle('Создание связи')
        box.setText('Какую связь Вы хотите создать?')
        box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)

        button_one = box.button(QtWidgets.QMessageBox.Yes)
        button_one.setIcon(QtGui.QIcon())
        button_one.setText(ids[1] + ' --> ' + ids[0])

        button_two = box.button(QtWidgets.QMessageBox.No)
        button_two.setIcon(QtGui.QIcon())
        button_two.setText(ids[0] + ' --> ' + ids[1])
        box.exec_()

        if box.clickedButton() == button_one:
            return [ids[1], ids[0]]
        elif box.clickedButton() == button_two:
            return [ids[0], ids[1]]

    def getSelectedNodes(self):
        selected_rows = self.table.selectedItems()
        selected_nodes = {}  # { node_id: item }
        for i in selected_rows:
            selected_nodes[self.table.item(i.row(), 0).text()] = i.text()

        return list(selected_nodes.keys())

    def export_json(self):
        data = ImportExport().export_json()
        print(data)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Ui()
    w.show()
    sys.exit(app.exec_())

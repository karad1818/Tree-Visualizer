from PyQt5.QtWidgets import QLabel ,QLineEdit , QApplication, QWidget , QDialog, QMainWindow ,QPushButton , QVBoxLayout, QGridLayout
from PyQt5.QtGui import QIcon, QPainter, QBrush, QPen, QFont
from PyQt5.QtCore import Qt
import sys
import math

class WindowManipulation(QWidget):
    def __init__(self):
        self.data = ""
        self.store = dict()
        self.uniq_id = 0
        self.printHeight = 0
        super().__init__()
        self.setGeometry(100,100,600,600) #window size (x,y),(width,height)
        self.setWindowTitle("Tree Visualizer")
        self.setWindowIcon(QIcon('tree.jpg'))
        self.setWindowOpacity(1)
        self.add_input_box()

    

    def add_input_box(self):
        l = QLineEdit("",self)
        l.setGeometry(300, 35, 200, 20)
        label = QLabel("Enter Node (Press 2 times Enter): ",self)
        label.setGeometry(100, 35, 170, 13)
        l.returnPressed.connect(lambda : take_data())
        heightLabel = QLabel("Height : 0",self)
        heightLabel.setGeometry(100,50,170,13)
        def take_data():
            self.repaint()
            self.data = l.text()
            heightLabel.setText("Height : "+str(self.printHeight))
            
    def paintEvent(self,event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black,1,Qt.SolidLine))
        painter.setBrush(QBrush(Qt.gray,Qt.SolidPattern))
        painter.setFont(QFont('Times',22))
        def draw_circle_text(number,x,y):
            py = y+33
            px = x+17
            painter.drawEllipse(x,y,50,50)
            st = str(number)
            if len(st)>1:
                st = st[0] + ".."
            painter.drawText(px,py,st)

        def right_child(idx,number,px,py,space):
            cx = px + space
            cy = py + 100
            self.store[idx] = [cx,cy]
            lx1 = px + 50
            lx2 = cx + 15
            ly1 = py + 35
            ly2 = cy
            painter.drawLine(lx1,ly1,lx2,ly2)
            draw_circle_text(number,cx,cy)

        def left_child(idx,number,px,py,space):
            global store
            cx = px - space
            cy = py + 100
            self.store[idx] = [cx,cy]
            lx1 = px 
            lx2 = cx + 35
            ly1 = py + 35
            ly2 = cy
            painter.drawLine(lx1,ly1,lx2,ly2)
            draw_circle_text(number,cx,cy)

        list_of_node = self.data.split(',')
        height = math.floor(math.log2(len(list_of_node)))
        self.printHeight = height
        # print("height : "+str(height))
        queue = []
        if len(list_of_node) >= 1 and list_of_node[0] != ' ':
            draw_circle_text(list_of_node[0],500,200)
            self.store[self.uniq_id] = [500,200]
            queue = [self.uniq_id]
            self.uniq_id += 1
        level = 0
        p = 2
        for i in range(1,len(list_of_node),2):
            front = queue[0]
            px = self.store[front][0]
            py = self.store[front][1]
            queue.pop(0)
            h = 2**(height-1)
            space = (h*80+(h-1)*35)//2
            space = int(space)
            if list_of_node[i]!= 'null':
                queue.append(self.uniq_id)
                left_child(self.uniq_id,list_of_node[i],px,py,space)
                self.uniq_id += 1

            if i+1 < len(list_of_node) and list_of_node[i+1] != 'null':
                queue.append(self.uniq_id)
                right_child(self.uniq_id,list_of_node[i+1],px,py,space)
                self.uniq_id += 1

            level += 2
            if level % p == 0:
                height -= 1
                level = 0
                p *= 2


if __name__ == "__main__":
    app = QApplication([])
    window = WindowManipulation()
    window.show()
    app.exec_()

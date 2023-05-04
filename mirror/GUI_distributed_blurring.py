import sys, os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QSpinBox
from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QPixmap, QFont

maxMask = 5


def startBlurring():
	global maxMask
	os.system("mpicc mpi_images.c -o mpi_images")
	os.system(f"mpiexec -n {maxMask} -f blur_processors ./mpi_images")

def moveImage(image):
	os.system("rm -rf img/img.bmp")
	os.system("rm -rf img_blur/*")
	os.system(f"cp {image} /mirror/img")
	os.system("mv img/*.bmp img/img.bmp")
	

# ------------------------------------------------ #

def assignProcesses(activeHosts):
    global maxMask

    f = open("blur_processors", "w")
    size = len(activeHosts)
    
    if(maxMask < 3):
    	f.write("ub2:" + str(maxMask%size))
    	f.close()
    	return

    for i in range(size):
        if i == size-1:
            activeHosts[i] += ":" + str(maxMask//size + maxMask%size)
        else:
            activeHosts[i] += ":" + str(maxMask//size)
        
        f.write(activeHosts[i] + "\n")

    f.close()

def checkSpecificHost(hostname):
    f = open("check_hosts", "w")
    f.write(f"{hostname}:1")
    f.close()

    os.system("timeout 3 mpiexec -n 1 -f check_hosts ./mpi_active_hosts")

    if(os.path.isfile("active_hosts.txt")):
        os.remove("active_hosts.txt")
        return True
    return False

def getActiveHosts():
    active = ["ub0"]

    if (checkSpecificHost("ub1")):
        active.append("ub1")
    if (checkSpecificHost("ub2")):
        active.append("ub2")

    assignProcesses(active)
    
    return active



# ---------- UI CODE ---------- #
class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Drop Image Here \n\n')
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')

    def setPixmap(self, image):
        super().setPixmap(image)

class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 800)
        self.setAcceptDrops(True)

        self.theImage = ""

        mainLayout = QVBoxLayout()

        self.photoViewer = ImageLabel()
        mainLayout.addWidget(self.photoViewer)
        
        global maxMask
        self.masksNumber = QLabel("Number of images to blur: " + str(maxMask))
        self.masksNumber.setFixedHeight(30)
        self.masksNumber.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.masksNumber)
        
        self.maskSelector = QSpinBox()
        self.maskSelector.setMinimum(1)
        self.maskSelector.setMaximum(50)
        self.maskSelector.setValue(5)
        self.maskSelector.setAlignment(Qt.AlignCenter)
        font = self.maskSelector.font()
        font.setPointSize(18)
        self.maskSelector.setFont(font)
        self.maskSelector.valueChanged.connect(self.onValueChange)
        mainLayout.addWidget(self.maskSelector)
        
        self.activeHostsTitle = QLabel("Active hosts:")
        self.activeHostsTitle.setFixedHeight(30)
        self.activeHostsTitle.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.activeHostsTitle)
        
        self.activeHostsList = QLabel("[Click the blur button]")
        self.activeHostsList.setFixedHeight(50)
        self.activeHostsList.setAlignment(Qt.AlignCenter)
        mainLayout.addWidget(self.activeHostsList)

        button = QPushButton('BLUR!', self)
        # button.setToolTip('This is an example button')
        button.setStyleSheet(
            "QPushButton{"
            "background-color : lightblue;"
            "}"
            "QPushButton::pressed"
            "{"
            "background-color : red;"
            "}"
        )
        button.setFont(QFont("Arial", 22))
        button.clicked.connect(self.on_click)
        mainLayout.addWidget(button)
        
        self.setLayout(mainLayout)


    # LO QUE SE EJECUTA CUANDO SE PRESIONA EL BOTÓN
    @pyqtSlot()
    def on_click(self):
        print(self.theImage)
        self.activeHostsList.setText('\n'.join(getActiveHosts()))
        QtWidgets.qApp.processEvents()
        print("\nHosts ready!\n")
        moveImage(self.theImage)
        print("Image moved successfully!\n")
        startBlurring()
        print("Image blurred successfully!")
    
    # SE EJECUTA CUANDO SE CAMBIA EL VALOR DEL NUMERO DE MASCARAS    
    def onValueChange(self):
    	global maxMask
    	maxMask = self.maskSelector.value()
    	self.masksNumber.setText("Number of images to blur: " + str(maxMask))

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()

            # print(file_path)
            self.theImage = file_path

            self.set_image(file_path)

            event.accept()
        else:
            event.ignore()

    def set_image(self, file_path):
        pixmap = QPixmap(file_path)
        scaled_pixmap = pixmap.scaled(self.photoViewer.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.photoViewer.setPixmap(scaled_pixmap)
        
        self.resize(self.photoViewer.sizeHint())


# 1. Sobreescribimos el archivo con los hosts activos para que tenga el master, por defecto
try:
    os.remove("active_hosts.txt")
except:
    print("active_host.txt does not exist")
# open("active_hosts.txt", "w").write("ub0").close()



app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())

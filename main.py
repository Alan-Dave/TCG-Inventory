import sys
import os
import time
from PyQt6.QtWidgets import QApplication


def inicio():
    global usuario

    from Frontend import login
    app = QApplication(sys.argv)
    ventana_login = login.LoginWindow()
    ventana_login.show()
    app.exec()
    usuario = login.LoginWindow.regresarNombre()



def menu():
    from Frontend import Index
    app = QApplication(sys.argv)
    ventana_login = Index.MainWindow(usuario)
    ventana_login.show()
    sys.exit(app.exec())  



def opciones():
    opcion = ''
    pass



    match opcion:
        case 1:
            pass
        case 2:
            pass
        case 3:
            pass
        case 4:
            inicio()
        case 5:
            pass
        case _:
            print("Ha ocurrido un error 100")





if __name__ == "__main__":
    pass

    

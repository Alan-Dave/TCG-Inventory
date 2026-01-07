import sys
from PyQt6.QtWidgets import QApplication
from MyQtApp.ui.Login import LoginWindow
from MyQtApp.ui.Index import MainWindow

def main():
    app = QApplication(sys.argv)

    login = LoginWindow()
    login.show()
    app.exec()

    usuario = login.get_usuario()
    if usuario is None:
        print("No se inició sesión, cerrando programa.")
        sys.exit()

    ventana = MainWindow(usuario)
    ventana.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

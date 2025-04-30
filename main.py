import sys
from PyQt6.QtWidgets import QApplication
from frontend.dash import ModernDashboard
from Backend.main import back_main
import time

def main():
    back_main()
    app = QApplication(sys.argv)
    
    try:
        with open("./frontend/styles.qss", "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("Error loading stylesheet:", e)
    window = ModernDashboard()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


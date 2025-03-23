import sys
from PyQt6.QtWidgets import QApplication
from dash import ModernDashboard

def main():
    app = QApplication(sys.argv)
    
    try:
        with open("styles.qss", "r") as f:
            app.setStyleSheet(f.read())
    except Exception as e:
        print("Error loading stylesheet:", e)
    
    window = ModernDashboard()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


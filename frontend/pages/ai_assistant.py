from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QScrollArea,
                             QWidget, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon
import ollama
import markdown

class AIAssistantWorker(QThread):
    """Worker thread for AI operations with streaming to prevent UI freezing"""
    token_ready = pyqtSignal(str)
    response_complete = pyqtSignal()
    error_occurred = pyqtSignal(str)
    
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt
        
    def run(self):
        try:
            stream = ollama.chat(
                model='gemma3:1b-it-q4_K_M', 
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a helpful health and medical assistant. Focus on providing accurate information about diseases, treatments, and general health advice. When appropriate, suggest search terms for further research and recommend reliable sources like .gov, .edu, or respected medical journals. Never provide definitive medical diagnosis or treatment plans, always encourage consulting with healthcare professionals. Format your responses using Markdown.'
                    },
                    {
                        'role': 'user',
                        'content': self.prompt
                    }
                ],
                stream=True  
            )
            
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    token = chunk['message']['content']
                    if token:
                        self.token_ready.emit(token)
            
            self.response_complete.emit()
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")


class MessageBubble(QFrame):
    """Custom widget for chat message bubbles with Markdown support"""
    def __init__(self, text, is_user=False, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.full_text = text
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.message_label.setOpenExternalLinks(True)
        self.message_label.setTextFormat(Qt.TextFormat.RichText)
        
        if is_user:
            self.setStyleSheet("""
                MessageBubble {
                    background-color: #444561;
                    border-radius: 15px;
                    border-top-right-radius: 5px;
                    margin-left: 50px;
                }
                QLabel {
                    color: #FFFFFF;
                }
            """)
            self.message_label.setText(text)
        else:
            self.setStyleSheet("""
                MessageBubble {
                    background-color: #2F3044;
                    border-radius: 15px;
                    border-top-left-radius: 5px;
                    margin-right: 50px;
                }
                QLabel {
                    color: #FFFFFF;
                }
            """)
            html_content = markdown.markdown(text)
            self.message_label.setText(html_content)
        
        layout.addWidget(self.message_label)
        self.setLayout(layout)
    
    def update_text(self, text):
        """Update the text and reformat with Markdown if needed"""
        self.full_text = text
        if not self.is_user:
            html_content = markdown.markdown(text)
            self.message_label.setText(html_content)
        else:
            self.message_label.setText(text)


def create_ai_assistant_page():
    """Creates and returns the AI Assistant page widget"""
    page_frame = QFrame()
    page_frame.setObjectName("AIAssistantPage")
    
    main_layout = QVBoxLayout(page_frame)
    main_layout.setContentsMargins(20, 20, 20, 20)
    
    page_frame.setStyleSheet("""
        #AIAssistantPage {
            background-color: #1E1E2F;
            color: #FFFFFF;
        }
        QLabel {
            color: #FFFFFF;
        }
        QLineEdit {
            background-color: #2F3044;
            border-radius: 15px;
            padding: 10px;
            color: #FFFFFF;
            border: 1px solid #444561;
        }
        QLineEdit:focus {
            border: 1px solid #6c63ff;
        }
        QPushButton {
            background-color: #2F3044;
            color: #FFFFFF;
            border-radius: 15px;
            padding: 10px;
            border: none;
        }
        QPushButton:hover {
            background-color: #444561;
        }
        QPushButton:pressed {
            background-color: #6c63ff;
        }
        QScrollArea {
            border: none;
            background-color: #1E1E2F;
        }
    """)
    
    header_layout = QVBoxLayout()
    
    title_label = QLabel("AI Health Assistant")
    title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
    title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_layout.addWidget(title_label)
    
    description = QLabel()
    description.setWordWrap(True)
    description.setAlignment(Qt.AlignmentFlag.AlignCenter)
    header_layout.addWidget(description)
    
    main_layout.addLayout(header_layout)
    
    chat_scroll = QScrollArea()
    chat_scroll.setWidgetResizable(True)
    chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    chat_container = QWidget()
    chat_layout = QVBoxLayout(chat_container)
    chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
    chat_layout.setSpacing(15)
    
    chat_scroll.setWidget(chat_container)
    main_layout.addWidget(chat_scroll, 1)
    
    greeting_message = MessageBubble("**Hello!**. *How can I help you with health or medical information today?*", is_user=False)
    chat_layout.addWidget(greeting_message)
    
    input_layout = QHBoxLayout()
    
    message_input = QLineEdit()
    message_input.setPlaceholderText("Type your health question here...")
    message_input.setMinimumHeight(50)
    
    send_button = QPushButton("Send")
    send_button.setIcon(QIcon("./frontend/icons/send.svg") if QIcon("./frontend/icons/send.svg").availableSizes() else QIcon())
    send_button.setMinimumHeight(50)
    send_button.setMinimumWidth(80)
    
    input_layout.addWidget(message_input, 1)
    input_layout.addWidget(send_button)
    
    main_layout.addLayout(input_layout)
    
    status_label = QLabel("")
    status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    main_layout.addWidget(status_label)
    
    worker = None
    current_ai_message = None
    accumulated_text = ""
    
    def send_message():
        text = message_input.text().strip()
        if not text:
            return
            
        user_message = MessageBubble(text, is_user=True)
        chat_layout.addWidget(user_message)
        
        message_input.clear()
        status_label.setText("AI is thinking...")
        
        message_input.setEnabled(False)
        send_button.setEnabled(False)
        
        nonlocal current_ai_message, accumulated_text
        accumulated_text = ""
        current_ai_message = MessageBubble("", is_user=False)
        chat_layout.addWidget(current_ai_message)
        
        nonlocal worker
        worker = AIAssistantWorker(text)
        worker.token_ready.connect(handle_token)
        worker.response_complete.connect(handle_response_complete)
        worker.error_occurred.connect(handle_error)
        worker.start()
        
        QApplication.processEvents()
        chat_scroll.verticalScrollBar().setValue(
            chat_scroll.verticalScrollBar().maximum()
        )
    
    def handle_token(token):
        """Handle each token as it comes in from the streaming response"""
        nonlocal accumulated_text
        accumulated_text += token
        
        if current_ai_message:
            current_ai_message.update_text(accumulated_text)
            
        QApplication.processEvents()
        chat_scroll.verticalScrollBar().setValue(
            chat_scroll.verticalScrollBar().maximum()
        )
    
    def handle_response_complete():
        """Handle completion of the AI response"""
        status_label.setText("")
        message_input.setEnabled(True)
        send_button.setEnabled(True)
        message_input.setFocus()
        
        QApplication.processEvents()
        chat_scroll.verticalScrollBar().setValue(
            chat_scroll.verticalScrollBar().maximum()
        )
    
    def handle_error(error_text):
        nonlocal current_ai_message
        
        if current_ai_message:
            current_ai_message.setParent(None)
            current_ai_message = None
        
        error_message = MessageBubble(f"**Error:** {error_text}\n\n*Please check if Ollama is running and gemma3:1b model is installed.*", is_user=False)
        chat_layout.addWidget(error_message)
        
        status_label.setText("")
        message_input.setEnabled(True)
        send_button.setEnabled(True)
        
        QApplication.processEvents()
        chat_scroll.verticalScrollBar().setValue(
            chat_scroll.verticalScrollBar().maximum()
        )
    
    message_input.returnPressed.connect(send_message)
    send_button.clicked.connect(send_message)
    
    return page_frame
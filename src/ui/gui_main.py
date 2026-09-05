import sys
import os
import threading
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox,
    QGroupBox, QFormLayout, QSpinBox, QDoubleSpinBox, QStatusBar,
    QTabWidget, QListWidget, QListWidgetItem, QMessageBox, QDialog,
    QFileDialog, QProgressBar, QSplitter, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QSize, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QTextCursor, QTextCharFormat
from src import i18n
from src.settings.settings_manager import SettingsManager
from src.client.minecraft_bot_client import MinecraftBotClient
from src.logger import strip_ansi


class ClientThread(QThread):
    """Thread for running the Minecraft bot client"""
    output_signal = pyqtSignal(str, str)  # message, message_type
    connection_status_signal = pyqtSignal(bool)  # connected
    error_signal = pyqtSignal(str)  # error message
    
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.is_running = True
        
    def run(self):
        try:
            # Monkey-patch the UI to emit signals
            original_print_info = self.client.ui.print_info
            original_print_success = self.client.ui.print_success
            original_print_error = self.client.ui.print_error
            original_print_chat = self.client.ui.print_chat
            original_print_sent = self.client.ui.print_sent
            original_print_alert = self.client.ui.print_alert
            original_print_warning = self.client.ui.print_warning
            original_print_section = self.client.ui.print_section
            
            self.client.ui.print_info = lambda msg: self.output_signal.emit(strip_ansi(msg), 'info')
            self.client.ui.print_success = lambda msg: self.output_signal.emit(strip_ansi(msg), 'success')
            self.client.ui.print_error = lambda msg: self.output_signal.emit(strip_ansi(msg), 'error')
            self.client.ui.print_chat = lambda msg: self.output_signal.emit(strip_ansi(msg), 'chat')
            self.client.ui.print_sent = lambda msg: self.output_signal.emit(strip_ansi(msg), 'sent')
            self.client.ui.print_alert = lambda msg: self.output_signal.emit(strip_ansi(msg), 'alert')
            self.client.ui.print_warning = lambda msg: self.output_signal.emit(strip_ansi(msg), 'warning')
            self.client.ui.print_section = lambda msg: self.output_signal.emit(msg, 'section')
            
            self.client.run()
        except Exception as e:
            self.error_signal.emit(str(e))


class MinecraftBotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        i18n.set_language(self.settings.get_language())
        self.client = None
        self.client_thread = None
        self.connected = False
        self.init_ui()
        self.setWindowTitle("Minecraft Bot Client (MBC) v1.3.1 - GUI")
        self.resize(1000, 750)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                padding: 6px;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left panel - Control panel
        left_panel = self.create_left_panel()
        
        # Right panel - Output console
        right_panel = self.create_right_panel()
        
        # Splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        central_widget.setLayout(main_layout)
        
        # Status bar
        self.status_label = QLabel("Status: Disconnected")
        self.status_bar_widget = QStatusBar()
        self.status_bar_widget.addWidget(self.status_label)
        self.setStatusBar(self.status_bar_widget)
        
    def create_left_panel(self):
        """Create the left control panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Connection section
        connection_group = QGroupBox("Connection Settings")
        connection_form = QFormLayout()
        
        self.server_input = QLineEdit()
        self.server_input.setText(self.settings.get_server_address())
        self.server_input.setPlaceholderText("localhost:25565")
        connection_form.addRow("Server Address:", self.server_input)
        
        self.version_combo = QComboBox()
        versions = ["1.8.9", "1.9.4", "1.10.2", "1.11.2", "1.12.2", "1.13.2", "1.14.4", 
                   "1.15.2", "1.16.5", "1.17.1", "1.18.2", "1.19.4", "1.20.1", "1.21"]
        self.version_combo.addItems(versions)
        current_version = self.settings.get_minecraft_version()
        idx = self.version_combo.findText(current_version)
        if idx >= 0:
            self.version_combo.setCurrentIndex(idx)
        connection_form.addRow("Minecraft Version:", self.version_combo)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Leave empty for random")
        self.username_input.setText(self.settings.get_username())
        connection_form.addRow("Username:", self.username_input)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.on_connect)
        self.connect_btn.setStyleSheet("QPushButton { background-color: #2196F3; }")
        self.connect_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
            QPushButton:pressed {
                background-color: #0056b3;
            }
        """)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.on_disconnect)
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #ba0000;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
        connection_buttons = QHBoxLayout()
        connection_buttons.addWidget(self.connect_btn)
        connection_buttons.addWidget(self.disconnect_btn)
        connection_form.addRow(connection_buttons)
        
        connection_group.setLayout(connection_form)
        layout.addWidget(connection_group)
        
        # Features section
        features_group = QGroupBox("Features")
        features_form = QFormLayout()
        
        self.auto_eat_check = QCheckBox()
        self.auto_eat_check.setChecked(self.settings.get("auto_eat", True))
        features_form.addRow("Auto Eat:", self.auto_eat_check)
        
        self.auto_walk_check = QCheckBox()
        self.auto_walk_check.setChecked(self.settings.get("auto_walk", False))
        features_form.addRow("Auto Walk:", self.auto_walk_check)
        
        self.proximity_check = QCheckBox()
        self.proximity_check.setChecked(self.settings.get("proximity_alerts", True))
        features_form.addRow("Proximity Alerts:", self.proximity_check)
        
        self.human_check = QCheckBox()
        self.human_check.setChecked(self.settings.get("human_actions", True))
        features_form.addRow("Human-like Actions:", self.human_check)
        
        self.log_check = QCheckBox()
        self.log_check.setChecked(self.settings.get_log_enabled())
        features_form.addRow("Enable Logging:", self.log_check)
        
        features_group.setLayout(features_form)
        layout.addWidget(features_group)
        
        # Spam section
        spam_group = QGroupBox("Auto Spam")
        spam_form = QFormLayout()
        
        self.spam_check = QCheckBox()
        self.spam_check.setChecked(self.settings.get_spam_enabled())
        spam_form.addRow("Enable Spam:", self.spam_check)
        
        self.spam_rate_spin = QDoubleSpinBox()
        self.spam_rate_spin.setValue(self.settings.get_spam_rate())
        self.spam_rate_spin.setMinimum(0.1)
        self.spam_rate_spin.setMaximum(10.0)
        self.spam_rate_spin.setSingleStep(0.1)
        self.spam_rate_spin.setSuffix(" msg/s")
        spam_form.addRow("Spam Rate:", self.spam_rate_spin)
        
        self.spam_msg_input = QLineEdit()
        self.spam_msg_input.setPlaceholderText("Enter spam message")
        spam_form.addRow("Message:", self.spam_msg_input)
        
        self.add_spam_btn = QPushButton("Add Message")
        self.add_spam_btn.clicked.connect(self.on_add_spam_message)
        spam_form.addRow(self.add_spam_btn)
        
        self.spam_list_widget = QListWidget()
        self.update_spam_list()
        spam_form.addRow("Messages:", self.spam_list_widget)
        
        spam_group.setLayout(spam_form)
        layout.addWidget(spam_group)
        
        # Chat section
        chat_group = QGroupBox("Chat & Commands")
        chat_layout = QVBoxLayout()
        
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Enter message or command (. or /)")
        self.chat_input.returnPressed.connect(self.on_send_message)
        chat_layout.addWidget(self.chat_input)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.on_send_message)
        chat_layout.addWidget(self.send_btn)
        
        chat_group.setLayout(chat_layout)
        layout.addWidget(chat_group)
        
        layout.addStretch()
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """Create the right output panel"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Output console
        console_label = QLabel("Console Output:")
        console_font = QFont()
        console_font.setPointSize(10)
        console_label.setFont(console_font)
        layout.addWidget(console_label)
        
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setFont(QFont("Courier New", 9))
        self.console_output.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.console_output)
        
        # Button row
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("Clear Console")
        self.clear_btn.clicked.connect(self.on_clear_console)
        button_layout.addWidget(self.clear_btn)
        
        self.help_btn = QPushButton("Show Help")
        self.help_btn.clicked.connect(self.on_show_help)
        button_layout.addWidget(self.help_btn)
        
        layout.addLayout(button_layout)
        
        panel.setLayout(layout)
        return panel
    
    def update_spam_list(self):
        """Update the spam messages list display"""
        self.spam_list_widget.clear()
        messages = self.settings.get_spam_messages()
        for i, msg in enumerate(messages):
            self.spam_list_widget.addItem(f"[{i}] {msg}")
    
    def on_connect(self):
        """Handle connection button click"""
        try:
            # Update settings
            self.settings.set("server_address", self.server_input.text())
            self.settings.set("minecraft_version", self.version_combo.currentText())
            self.settings.set("username", self.username_input.text())
            self.settings.set("auto_eat", self.auto_eat_check.isChecked())
            self.settings.set("auto_walk", self.auto_walk_check.isChecked())
            self.settings.set("proximity_alerts", self.proximity_check.isChecked())
            self.settings.set("human_actions", self.human_check.isChecked())
            self.settings.set("log_enabled", self.log_check.isChecked())
            self.settings.save_spam_config(
                self.spam_check.isChecked(),
                self.spam_rate_spin.value(),
                self.settings.get_spam_messages()
            )
            
            # Create client and start connection thread
            self.client = MinecraftBotClient()
            self.client_thread = ClientThread(self.client)
            self.client_thread.output_signal.connect(self.on_output)
            self.client_thread.error_signal.connect(self.on_error)
            self.client_thread.start()
            
            # Update UI
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.connected = True
            self.update_status("Connecting...")
            self.log_to_console("Connecting to server...", "info")
            
        except Exception as e:
            self.log_to_console(f"Connection error: {str(e)}", "error")
            QMessageBox.critical(self, "Connection Error", str(e))
    
    def on_disconnect(self):
        """Handle disconnect button click"""
        if self.client and self.client.connected:
            try:
                self.client.disconnect()
                self.log_to_console("Disconnected from server", "warning")
            except Exception as e:
                self.log_to_console(f"Disconnect error: {str(e)}", "error")
        
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.connected = False
        self.update_status("Disconnected")
    
    def on_send_message(self):
        """Handle sending a message"""
        message = self.chat_input.text().strip()
        if not message:
            return
        
        if self.client and self.client.connected:
            try:
                if message.startswith("."):
                    # Client command
                    self.client.handle_client_command(message, allow_connect=False)
                    self.log_to_console(f"Command: {message}", "info")
                elif message.startswith("/"):
                    # Server command
                    self.client.connection_manager.send_chat(message)
                    self.log_to_console(f"Command sent: {message}", "sent")
                else:
                    # Chat message
                    self.client.connection_manager.send_chat(message)
                    self.log_to_console(f"You: {message}", "sent")
            except Exception as e:
                self.log_to_console(f"Error sending message: {str(e)}", "error")
        else:
            self.log_to_console("Not connected to server", "warning")
        
        self.chat_input.clear()
    
    def on_add_spam_message(self):
        """Handle adding a spam message"""
        message = self.spam_msg_input.text().strip()
        if not message:
            QMessageBox.warning(self, "Empty Message", "Please enter a message")
            return
        
        messages = self.settings.get_spam_messages()
        if message not in messages:
            messages.append(message)
            self.settings.save_spam_config(
                self.spam_check.isChecked(),
                self.spam_rate_spin.value(),
                messages
            )
            self.log_to_console(f"Added spam message: {message}", "success")
            self.spam_msg_input.clear()
            self.update_spam_list()
        else:
            QMessageBox.info(self, "Duplicate", "This message already exists")
    
    def on_clear_console(self):
        """Clear the console output"""
        self.console_output.clear()
    
    def on_show_help(self):
        """Show help dialog"""
        help_text = """Minecraft Bot Client (MBC) v1.3.1 - GUI Help

Commands:
  . prefix   - Client commands (not sent to server)
  / prefix   - Server commands
  Plain text - Chat messages

Client Commands:
  .help           - Show help and open website
  .esc            - Leave server (stay in GUI)
  .exit           - Exit client
  .connect        - Reconnect to server
  .respawn        - Send respawn packet
  .log on/off     - Toggle logging
  .spam on/off    - Toggle spam
  .spam rate N    - Set spam rate
  .spam add MSG   - Add spam message
  .spam list      - List spam messages
  .walk on/off    - Toggle auto walk
  .walk add X,Y,Z - Add waypoint
  .eat on/off     - Toggle auto eat
  .config K V     - Set config value

Features:
  - Auto Eat: Automatically eat when health is low
  - Auto Walk: Random walking or custom waypoints
  - Proximity Alerts: Get notified when players are nearby
  - Human-like Actions: Random head turns and arm swings
  - Auto Spam: Send messages at configured rate
  - Logging: Save session logs

Server Versions Supported:
  1.8.9 to 1.21

Notes:
  - Works on offline-mode servers (online-mode=false)
  - Supports SRV record domains
  - All settings saved to config.json
        """
        QMessageBox.information(self, "Help", help_text)
    
    def on_output(self, message, message_type):
        """Handle output from the client thread"""
        self.log_to_console(message, message_type)
        if message_type == 'success' and 'connected' in message.lower():
            self.update_status("Connected")
    
    def on_error(self, error_message):
        """Handle error from the client thread"""
        self.log_to_console(f"ERROR: {error_message}", "error")
        self.update_status("Error")
        QMessageBox.critical(self, "Client Error", error_message)
    
    def update_status(self, status_text):
        """Update status bar"""
        self.status_label.setText(f"Status: {status_text}")
    
    def log_to_console(self, message, message_type="info"):
        """Log a message to the console with proper formatting"""
        cursor = self.console_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Create text format based on message type
        char_format = QTextCharFormat()
        if message_type == "info":
            char_format.setForeground(QColor(100, 180, 255))  # Light Blue
        elif message_type == "success":
            char_format.setForeground(QColor(100, 255, 100))  # Light Green
        elif message_type == "error":
            char_format.setForeground(QColor(255, 100, 100))  # Light Red
        elif message_type == "warning":
            char_format.setForeground(QColor(255, 200, 100))  # Light Orange
        elif message_type == "chat":
            char_format.setForeground(QColor(200, 200, 200))  # Light Gray
        elif message_type == "sent":
            char_format.setForeground(QColor(100, 255, 150))  # Light Green-Cyan
        elif message_type == "alert":
            char_format.setForeground(QColor(255, 150, 200))  # Hot Pink
        elif message_type == "section":
            char_format.setForeground(QColor(100, 200, 255))  # Cyan
        
        self.console_output.setTextCursor(cursor)
        self.console_output.setCurrentCharFormat(char_format)
        self.console_output.insertPlainText(f"[{message_type.upper()}] {message}\n")
        
        # Auto-scroll to bottom
        cursor.movePosition(QTextCursor.End)
        self.console_output.setTextCursor(cursor)


def run_gui():
    app = QApplication(sys.argv)
    gui = MinecraftBotGUI()
    gui.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()

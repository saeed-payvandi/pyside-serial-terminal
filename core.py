import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit, QLineEdit
)
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from PySide6.QtCore import QIODevice

class SerialTerminal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide Serial Terminal")
        self.resize(500, 400)        

        self.serial = QSerialPort()
        self.serial.readyRead.connect(self.read_data)

        layout = QVBoxLayout()

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        self.port_combo = QComboBox()
        for port in QSerialPortInfo.availablePorts():
            self.port_combo.addItem(port.portName())
        port_layout.addWidget(self.port_combo)

        self.connect_button = QPushButton("connect")
        self.connect_button.clicked.connect(self.connect_serial)
        port_layout.addWidget(self.connect_button)

        layout.addLayout(port_layout)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        send_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Enter message to send...")
        self.input_box.returnPressed.connect(self.send_data)
        send_layout.addWidget(self.input_box)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_data)
        send_layout.addWidget(self.send_button)

        layout.addLayout(send_layout)

        self.setLayout(layout)

    def connect_serial(self):
        if not self.serial.isOpen():
            port = self.port_combo.currentText()
            self.serial.setPortName(port)
            self.serial.setBaudRate(9600)

            if self.serial.open(QIODevice.ReadWrite):
                self.log.append(f"Connected to {port}")
                self.connect_button.setText("Disconnect")
            else:
                self.log.append("Failed to open port")
        else:
            self.serial.close()
            self.connect_button.setText("Connect")
            self.log.append("Disconnected")
            
    def read_data(self):
        if not hasattr(self, "buffer"):
            self.buffer = ""
        self.buffer += self.serial.readAll().data().decode(errors="ignore")
                
        if "\r" in self.buffer:
            line, self.buffer = self.buffer.split("\r", 1)
            self.log.append(f"<-- {line}")

    def send_data(self):
        if self.serial.isOpen():
            text = self.input_box.text() + "\n"
            self.serial.write(text.encode())
            self.log.append(f"--> {text.strip()}")
            self.input_box.clear()
        else:
            self.log.append("Port is not open")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SerialTerminal()
    window.show()
    sys.exit(app.exec())

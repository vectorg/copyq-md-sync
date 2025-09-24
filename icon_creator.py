from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from PyQt5.QtCore import Qt

def create_tray_icon():
    """动态创建一个简单的托盘图标"""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # 背景
    painter.setBrush(QColor("#4CAF50")) # 绿色背景
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 60, 60)
    
    # 文字
    font = QFont("Arial", 32, QFont.Bold)
    painter.setFont(font)
    painter.setPen(QColor("white"))
    painter.drawText(pixmap.rect(), Qt.AlignCenter, "S")
    
    painter.end()
    
    return QIcon(pixmap) 
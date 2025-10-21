"""
Theme management for UMTK UI
Provides light and dark theme styles
"""

from PyQt6 import QtCore, QtGui, QtWidgets


class ThemeManager:
    """Manages light and dark themes for the UMTK application."""
    
    def __init__(self):
        self.current_theme = "dark"  # Default to dark theme
        
    def get_theme_styles(self, theme_name: str) -> dict:
        """Get all styles for the specified theme."""
        if theme_name == "dark":
            return self._get_dark_theme()
        elif theme_name == "light":
            return self._get_light_theme()
        else:
            return self._get_dark_theme()  # Default fallback
    
    def _get_dark_theme(self) -> dict:
        """Dark theme styles."""
        return {
            "main_window": """
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
            """,
            
            "button_green": """
                QPushButton {
                    background-color: #4CAF50;
                    border: 2px solid #45a049;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:pressed {
                    background-color: #3d8b40;
                }
            """,
            
            "button_red": """
                QPushButton {
                    background-color: #f44336;
                    border: 2px solid #da190b;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
                QPushButton:pressed {
                    background-color: #c1170a;
                }
            """,
            
            "button_blue": """
                QPushButton {
                    background-color: #2196F3;
                    border: 2px solid #1976D2;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
            """,
            
            "button_neutral": """
                QPushButton {
                    background-color: #757575;
                    border: 2px solid #616161;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #616161;
                }
                QPushButton:pressed {
                    background-color: #424242;
                }
            """,
            
            "input_field": """
                QLineEdit {
                    background-color: #424242;
                    border: 2px solid #616161;
                    border-radius: 4px;
                    color: #ffffff;
                    padding: 4px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """,
            
            "combo_box": """
                QComboBox {
                    background-color: #424242;
                    border: 2px solid #616161;
                    border-radius: 4px;
                    color: #ffffff;
                    padding: 4px;
                }
                QComboBox:hover {
                    border: 2px solid #757575;
                }
                QComboBox::drop-down {
                    border: none;
                    background-color: #424242;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #ffffff;
                }
                QComboBox QAbstractItemView {
                    background-color: #424242;
                    border: 2px solid #616161;
                    color: #ffffff;
                    selection-background-color: #616161;
                }
            """,
            
            "text_browser": """
                QTextBrowser {
                    background-color: #424242;
                    border: 2px solid #616161;
                    border-radius: 4px;
                    color: #ffffff;
                }
            """,
            
            "label": """
                QLabel {
                    color: #ffffff;
                    background-color: transparent;
                }
            """,
            
            "checkbox": """
                QCheckBox {
                    color: #ffffff;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #424242;
                    border: 2px solid #616161;
                    border-radius: 3px;
                }
                QCheckBox::indicator:checked {
                    background-color: #2196F3;
                    border: 2px solid #1976D2;
                    border-radius: 3px;
                }
            """,
            
            "groupbox": """
                QGroupBox {
                    color: #ffffff;
                    font-weight: bold;
                    border: 2px solid #616161;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 5px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """,
            
            "theme_switcher": """
                QPushButton {
                    background-color: #424242;
                    border: 2px solid #616161;
                    border-radius: 20px;
                    color: #ffffff;
                    font-weight: bold;
                    padding: 8px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #525252;
                    border: 2px solid #757575;
                }
                QPushButton:pressed {
                    background-color: #2196F3;
                    border: 2px solid #1976D2;
                }
            """
        }
    
    def _get_light_theme(self) -> dict:
        """Light theme styles."""
        return {
            "main_window": """
                QMainWindow {
                    background-color: #f5f5f5;
                    color: #212121;
                }
            """,
            
            "button_green": """
                QPushButton {
                    background-color: #66BB6A;
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #4CAF50;
                }
                QPushButton:pressed {
                    background-color: #388E3C;
                }
            """,
            
            "button_red": """
                QPushButton {
                    background-color: #EF5350;
                    border: 2px solid #F44336;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #F44336;
                }
                QPushButton:pressed {
                    background-color: #D32F2F;
                }
            """,
            
            "button_blue": """
                QPushButton {
                    background-color: #42A5F5;
                    border: 2px solid #2196F3;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #2196F3;
                }
                QPushButton:pressed {
                    background-color: #1976D2;
                }
            """,
            
            "button_neutral": """
                QPushButton {
                    background-color: #BDBDBD;
                    border: 2px solid #9E9E9E;
                    border-radius: 8px;
                    color: #212121;
                    font-weight: bold;
                    padding: 8px;
                }
                QPushButton:hover {
                    background-color: #9E9E9E;
                }
                QPushButton:pressed {
                    background-color: #757575;
                    color: white;
                }
            """,
            
            "input_field": """
                QLineEdit {
                    background-color: #ffffff;
                    border: 2px solid #BDBDBD;
                    border-radius: 4px;
                    color: #212121;
                    padding: 4px;
                }
                QLineEdit:focus {
                    border: 2px solid #2196F3;
                }
            """,
            
            "combo_box": """
                QComboBox {
                    background-color: #ffffff;
                    border: 2px solid #BDBDBD;
                    border-radius: 4px;
                    color: #212121;
                    padding: 4px;
                }
                QComboBox:hover {
                    border: 2px solid #9E9E9E;
                }
                QComboBox::drop-down {
                    border: none;
                    background-color: #ffffff;
                }
                QComboBox::down-arrow {
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid #212121;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    border: 2px solid #BDBDBD;
                    color: #212121;
                    selection-background-color: #E0E0E0;
                }
            """,
            
            "text_browser": """
                QTextBrowser {
                    background-color: #ffffff;
                    border: 2px solid #BDBDBD;
                    border-radius: 4px;
                    color: #212121;
                }
            """,
            
            "label": """
                QLabel {
                    color: #212121;
                    background-color: transparent;
                }
            """,
            
            "checkbox": """
                QCheckBox {
                    color: #212121;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:unchecked {
                    background-color: #ffffff;
                    border: 2px solid #BDBDBD;
                    border-radius: 3px;
                }
                QCheckBox::indicator:checked {
                    background-color: #2196F3;
                    border: 2px solid #1976D2;
                    border-radius: 3px;
                }
            """,
            
            "groupbox": """
                QGroupBox {
                    color: #212121;
                    font-weight: bold;
                    border: 2px solid #BDBDBD;
                    border-radius: 6px;
                    margin-top: 10px;
                    padding-top: 5px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """,
            
            "theme_switcher": """
                QPushButton {
                    background-color: #ffffff;
                    border: 2px solid #BDBDBD;
                    border-radius: 20px;
                    color: #212121;
                    font-weight: bold;
                    padding: 8px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                    border: 2px solid #9E9E9E;
                }
                QPushButton:pressed {
                    background-color: #2196F3;
                    border: 2px solid #1976D2;
                    color: white;
                }
            """
        }
    
    def apply_theme_to_widget(self, widget, theme_name: str, style_key: str):
        """Apply a specific style from the theme to a widget."""
        styles = self.get_theme_styles(theme_name)
        if style_key in styles:
            widget.setStyleSheet(styles[style_key])
    
    def get_amp_alert_styles(self, theme_name: str, opacity: float = 0.0) -> str:
        """Get amp alert style for the theme with specified opacity."""
        if theme_name == "dark":
            text_color = "#ffffff"
        else:  # light theme
            text_color = "#212121"
            
        if opacity > 0:
            return f"""
                QLabel {{
                    color: {text_color};
                    background-color: rgba(244, 67, 54, {opacity});
                    border-radius: 8px;
                    padding: 4px;
                }}
            """
        else:
            return f"""
                QLabel {{
                    color: {text_color};
                    background-color: transparent;
                    border-radius: 8px;
                    padding: 4px;
                }}
            """
# main.py

import sys
import json
import os
from datetime import datetime

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QHBoxLayout, QLineEdit,
                             QMessageBox, QScrollArea, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QCheckBox, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

# Import EditWindow from edit_window.py
from edit_window import EditWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Practice App")
        self.resize(1000, 600)  # Set initial window size but allow resizing

        # Set dark theme
        self.set_dark_theme()

        # Load data
        self.data_file = self.get_data_file()
        self.data = self.load_data()

        # Set up the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        # Add the header label for 'Music Practice'
        header_label = QLabel("Music Practice")
        header_font = QFont()
        header_font.setPointSize(24)  # Adjust the font size as needed
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("color: white;")  # Optional: Set text color to white

        # Add the header label to the main layout
        self.main_layout.addWidget(header_label)

        # Create a QTableWidget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(
            ["Name", "Practice Count", "Last Practiced", "Was Performed", "Edit"])

        # Ensure the grid is visible
        self.table_widget.setShowGrid(True)

        # Set the grid line color to a very dark grey
        self.table_widget.setStyleSheet("QTableWidget { gridline-color: rgb(50, 50, 50); }")

        # Set grid style to solid line (optional)
        self.table_widget.setGridStyle(Qt.PenStyle.SolidLine)

        # Remove or comment out this line if present
        # self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setSortingEnabled(True)  # Enable sorting

        # Populate the table
        self.populate_table()

        # Add the table to the main layout
        self.main_layout.addWidget(self.table_widget)

        # Add buttons for Add Record and Reset Table
        self.button_layout = QHBoxLayout()
        self.add_record_button = QPushButton("Add Record")
        self.add_record_button.clicked.connect(self.show_add_dialog)
        self.reset_table_button = QPushButton("Reset Table")
        self.reset_table_button.clicked.connect(self.reset_table)
        self.button_layout.addWidget(self.add_record_button)
        self.button_layout.addWidget(self.reset_table_button)
        self.main_layout.addLayout(self.button_layout)

        # Connect cell click event
        self.table_widget.cellClicked.connect(self.on_cell_clicked)

    def set_dark_theme(self):
        """Set the dark theme using a stylesheet."""
        dark_palette = QPalette()

        dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))

        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        self.setPalette(dark_palette)

    def get_data_file(self):
        """Return the path to the data file."""
        directory = os.path.join(os.path.expanduser("~"), '.PracticeApp')
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, 'data.json')

    def load_data(self):
        """Load the data from the JSON file."""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                # Ensure all records have 'was_performed' key
                for record in data:
                    if 'was_performed' not in record:
                        record['was_performed'] = False
                return data
        return []

    def save_data(self):
        """Save the current data to the JSON file."""
        with open(self.data_file, 'w') as file:
            json.dump(self.data, file)

    def populate_table(self):
        """Populate the table with the current data."""
        # Clear the table
        self.table_widget.setRowCount(0)

        # Combine song and non-song records
        all_records = self.data.copy()

        # Sort the records based on the current sorting column and order
        header = self.table_widget.horizontalHeader()
        sort_column = header.sortIndicatorSection()
        sort_order = header.sortIndicatorOrder()
        reverse = sort_order == Qt.SortOrder.DescendingOrder

        # Determine the key for sorting based on the column
        if sort_column == 0:  # Name
            key_func = lambda x: x['name']
        elif sort_column == 1:  # Practice Count
            key_func = lambda x: x['practice_count']
        elif sort_column == 2:  # Last Practiced
            key_func = lambda x: x['last_practiced'] or ''
        elif sort_column == 3:  # Was Performed
            key_func = lambda x: x.get('was_performed', False)
        else:
            key_func = lambda x: x['name']

        all_records.sort(key=key_func, reverse=reverse)

        for record in all_records:
            self.add_record_to_table(record)

        # Remove the call to resizeColumnsToContents(), as it interferes with stretching
        # self.table_widget.resizeColumnsToContents()  # Comment out or remove this line

        # After populating the table, set the section resize mode for each column to Stretch
        for i in range(self.table_widget.columnCount()):
            self.table_widget.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

    def add_record_to_table(self, record):
        """Add a record to the table."""
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        # Determine the text color based on 'was_performed' status
        if record.get('was_performed', False):
            text_color = QColor('green')
        else:
            text_color = self.palette().color(QPalette.ColorRole.Text)

        # Name
        name_item = QTableWidgetItem(record['name'])
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        name_item.setForeground(text_color)  # Set text color
        self.table_widget.setItem(row_position, 0, name_item)

        # Practice Count
        practice_count_item = QTableWidgetItem(str(record['practice_count']))
        practice_count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        practice_count_item.setForeground(text_color)  # Set text color
        self.table_widget.setItem(row_position, 1, practice_count_item)

        # Last Practiced
        if record['last_practiced'] is None:
            last_practiced_text = "Never"
        else:
            last_practiced_date = datetime.strptime(record['last_practiced'], '%Y-%m-%d').date()
            today = datetime.now().date()

            if last_practiced_date == today:
                last_practiced_text = "Today"
            else:
                days_elapsed = (today - last_practiced_date).days
                last_practiced_text = f"{days_elapsed} day(s) ago"

        last_practiced_item = QTableWidgetItem(last_practiced_text)
        last_practiced_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        last_practiced_item.setForeground(text_color)  # Set text color
        self.table_widget.setItem(row_position, 2, last_practiced_item)

        # Was Performed
        was_performed_text = "Yes" if record.get('was_performed', False) else "No"
        was_performed_item = QTableWidgetItem(was_performed_text)
        was_performed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        was_performed_item.setForeground(text_color)  # Set text color
        self.table_widget.setItem(row_position, 3, was_performed_item)

        # Edit Button
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda checked, rec=record: self.show_edit_dialog(rec))
        self.table_widget.setCellWidget(row_position, 4, edit_button)

    def add_record(self, name, isSong=False, was_performed=False):
        """Add a new record to the data."""
        new_record = {
            'name': name,
            'practice_count': 0,
            'last_practiced': None,
            'isSong': isSong,
            'was_performed': was_performed
        }
        self.data.append(new_record)
        self.save_data()
        self.populate_table()

    def show_add_dialog(self):
        """Show a dialog to prompt the user for a new record."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Record")

        layout = QVBoxLayout(dialog)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter name")
        layout.addWidget(name_input)

        # Checkbox for isSong
        is_song_checkbox = QCheckBox("Is Song")
        is_song_checkbox.setChecked(True)
        layout.addWidget(is_song_checkbox)

        # Checkbox for Was Performed
        was_performed_checkbox = QCheckBox("Was Performed")
        was_performed_checkbox.setChecked(False)
        layout.addWidget(was_performed_checkbox)

        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add")
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        def on_add():
            name = name_input.text().strip()
            is_song = is_song_checkbox.isChecked()
            was_performed = was_performed_checkbox.isChecked()
            if name:
                new_record = {
                    'name': name,
                    'practice_count': 0,
                    'last_practiced': None,
                    'isSong': is_song,
                    'was_performed': was_performed
                }
                self.data.append(new_record)
                self.save_data()
                self.populate_table()
                dialog.accept()

        add_button.clicked.connect(on_add)
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()

    def show_edit_dialog(self, record):
        """Show a dialog to edit a record."""
        edit_window = EditWindow(self, record)
        edit_window.exec()

    def reset_table(self):
        """Reset the table by clearing the data with double confirmation dialog."""
        # First confirmation
        reply = QMessageBox.question(self, 'Confirm Reset',
                                     "Are you sure you want to reset all data?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Second confirmation
            reply = QMessageBox.question(self, 'Final Confirmation',
                                         "Are you absolutely sure?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                # Perform reset
                self.data = []
                self.save_data()
                self.populate_table()

    def on_cell_clicked(self, row, column):
        """Handle cell click events."""
        if column == 0:
            # Name column clicked, add practice session
            record = self.data[row]
            self.on_name_button_click(record)

    def on_name_button_click(self, record):
        """Handle clicks on the name column to add a practice session."""
        reply = QMessageBox.question(self, 'Add Practice Session',
                                     f"Add a practice session for {record['name']}?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            record['practice_count'] += 1
            record['last_practiced'] = datetime.now().strftime('%Y-%m-%d')
            self.save_data()
            self.populate_table()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

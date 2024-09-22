# main.py

import sys
import json
import os
from datetime import datetime

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QPushButton,
                             QVBoxLayout, QGridLayout, QHBoxLayout, QLineEdit,
                             QMessageBox, QScrollArea, QSpacerItem, QSizePolicy,
                             QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor

# Import EditWindow from edit_window.py
from edit_window import EditWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Practice App")
        self.setFixedSize(1000, 600)  # Set window size to 1000x600

        # Set dark theme
        self.set_dark_theme()

        # Load data
        self.data_file = self.get_data_file()
        self.data = self.load_data()

        # Set up the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Add a scroll area for the grid
        self.scroll_area = QScrollArea()
        self.scroll_area_widget = QWidget()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget)

        self.grid_layout = QGridLayout(self.scroll_area_widget)
        self.grid_layout.setColumnStretch(0, 1)  # Name column stretches
        self.grid_layout.setColumnStretch(1, 1)
        self.grid_layout.setColumnStretch(2, 1)
        self.grid_layout.setColumnStretch(3, 1)
        self.grid_layout.setColumnStretch(4, 1)

        # Add the scroll area to the main layout
        self.main_layout.addWidget(self.scroll_area)

        # Populate the table
        self.populate_table()

        # Add buttons for Add Record and Reset Table
        self.button_layout = QHBoxLayout()
        self.add_record_button = QPushButton("Add Record")
        self.add_record_button.clicked.connect(self.show_add_dialog)
        self.reset_table_button = QPushButton("Reset Table")
        self.reset_table_button.clicked.connect(self.reset_table)
        self.button_layout.addWidget(self.add_record_button)
        self.button_layout.addWidget(self.reset_table_button)
        self.main_layout.addLayout(self.button_layout)

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
        # Clear the grid
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Separate records into two groups: isSong = True and isSong = False
        song_records = [r for r in self.data if r.get('isSong', False)]
        non_song_records = [r for r in self.data if not r.get('isSong', False)]

        # Sort records within each group
        song_records.sort(key=lambda x: (x['last_practiced'] is not None, x['last_practiced'] or ''))
        non_song_records.sort(key=lambda x: (x['last_practiced'] is not None, x['last_practiced'] or ''))

        row = 0  # Start at row 0

        # Add headers
        header_font = QFont()
        header_font.setBold(True)
        name_header = QLabel("Name")
        name_header.setFont(header_font)
        name_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(name_header, row, 0)
        practice_count_header = QLabel("Practice Count")
        practice_count_header.setFont(header_font)
        practice_count_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(practice_count_header, row, 1)
        last_practiced_header = QLabel("Last Practiced")
        last_practiced_header.setFont(header_font)
        last_practiced_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(last_practiced_header, row, 2)
        was_performed_header = QLabel("Was Performed")
        was_performed_header.setFont(header_font)
        was_performed_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(was_performed_header, row, 3)
        edit_header = QLabel("Edit")
        edit_header.setFont(header_font)
        edit_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(edit_header, row, 4)

        row += 1

        # Add song records first
        for record in song_records:
            self.add_record_to_grid(record, row)
            row += 1

        # Add a separator if there are non-song records
        if non_song_records:
            self.add_separator(row)
            row += 1

        # Add non-song records
        for record in non_song_records:
            self.add_record_to_grid(record, row)
            row += 1

        # Add spacer to fill space
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.grid_layout.addItem(spacer, row, 0)

    def add_separator(self, row):
        """Add a visual separator between song and practice records."""
        separator = QLabel(" ")
        self.grid_layout.addWidget(separator, row, 0)
        # Fill other columns
        for col in range(1, 5):
            self.grid_layout.addWidget(QLabel(" "), row, col)

    def add_record_to_grid(self, record, row):
        """Add a record to the grid."""
        # Create the button for the "Name" column
        name_button = QPushButton(record['name'])
        name_button.clicked.connect(lambda checked, rec=record: self.on_name_button_click(rec))
        name_button.setStyleSheet("text-align: center;")
        self.grid_layout.addWidget(name_button, row, 0)

        # Add the practice count label, centered
        practice_count_label = QLabel(str(record['practice_count']))
        practice_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(practice_count_label, row, 1)

        # Evaluate the last practiced date
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

        # Add the last practiced label, centered
        last_practiced_label = QLabel(last_practiced_text)
        last_practiced_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(last_practiced_label, row, 2)

        # Add the 'Was Performed' label, centered
        was_performed_text = "Yes" if record.get('was_performed', False) else "No"
        was_performed_label = QLabel(was_performed_text)
        was_performed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid_layout.addWidget(was_performed_label, row, 3)

        # Add an "Edit" button
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(lambda checked, rec=record: self.show_edit_dialog(rec))
        self.grid_layout.addWidget(edit_button, row, 4)

    def add_record(self, name, isSong=False):
        """Add a new record to the data."""
        new_record = {
            'name': name,
            'practice_count': 0,
            'last_practiced': None,
            'isSong': isSong,
            'was_performed': False
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

    def on_name_button_click(self, record):
        """Handle button presses on the name column to add a practice session."""
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

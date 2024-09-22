# main.py

import sys
import json
import os
from datetime import datetime, timedelta
from functools import partial

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QCheckBox, QDialog, QStyle, QStyledItemDelegate
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

# Import EditWindow from edit_window.py
from edit_window import EditWindow


class PaddedItemDelegate(QStyledItemDelegate):
    """Custom delegate to add padding to table items."""
    def __init__(self, left_padding=10, parent=None):
        super().__init__(parent)
        self.left_padding = left_padding

    def paint(self, painter, option, index):
        # Adjust the rectangle to add left padding
        option.rect = option.rect.adjusted(self.left_padding, 0, 0, 0)
        super().paint(painter, option, index)


class LastPracticedItem(QTableWidgetItem):
    """Custom QTableWidgetItem for 'Last Practiced' column to handle sorting."""
    def __init__(self, text):
        super().__init__(text)
        self.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

    def __lt__(self, other):
        # Define less than for sorting
        self_text = self.text()
        other_text = other.text()

        # Define a function to convert text to elapsed days
        def get_elapsed_days(text):
            if text == "Never":
                return float('inf')  # Treat 'Never' as the maximum elapsed time
            elif text == "Today":
                return 0
            elif "day(s) ago" in text:
                try:
                    days_ago = int(text.split()[0])
                    return days_ago
                except ValueError:
                    return float('inf')  # Treat invalid formats as 'Never'
            else:
                return float('inf')  # Treat unexpected formats as 'Never'

        self_elapsed = get_elapsed_days(self_text)
        other_elapsed = get_elapsed_days(other_text)

        return self_elapsed < other_elapsed


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Practice App")
        self.resize(1200, 700)  # Increased window size for better UI

        # Set dark theme
        self.set_dark_theme()

        # Load data
        self.data_file = self.get_data_file()
        self.data = self.load_data()

        # Set up the central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(15, 15, 15, 15)  # Increased margins
        self.main_layout.setSpacing(15)  # Increased spacing

        # Add the header label for 'Music Practice'
        header_label = QLabel("Music Practice")
        header_font = QFont()
        header_font.setPointSize(28)  # Larger font size for header
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("color: white;")  # Text color remains white

        self.main_layout.addSpacing(10)  # Add vertical space beneath the header
        # Add the header label to the main layout
        self.main_layout.addWidget(header_label)
        self.main_layout.addSpacing(25)  # Add vertical space beneath the header

        # Create a QTableWidget
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(6)
        self.table_widget.setHorizontalHeaderLabels(
            ["Name", "Practice Count", "Last Practiced", "Was Performed", "Is Song", "Edit"]
        )

        # Set the font size for column headers
        header = self.table_widget.horizontalHeader()
        header_font = QFont()
        header_font.setPointSize(16)  # Adjust the size as needed
        header.setFont(header_font)
        header.setStyleSheet("QHeaderView::section { color: #969393; background-color: #444444; }")

        # Ensure the grid is visible
        self.table_widget.setShowGrid(True)

        # Set the grid line color to a very dark grey
        self.table_widget.setStyleSheet("QTableWidget { gridline-color: rgb(50, 50, 50); }")

        # Set grid style to solid line (optional)
        self.table_widget.setGridStyle(Qt.PenStyle.SolidLine)

        self.table_widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_widget.setSortingEnabled(True)  # Enable sorting

        # Load the edit icon
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, 'edit_icon.png')
        if os.path.exists(icon_path):
            self.edit_icon = QIcon(icon_path)
        else:
            # Use a standard icon if custom icon not found
            self.edit_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView)

        # Set custom delegate for the 'Name' column to add padding
        padded_delegate = PaddedItemDelegate(left_padding=20, parent=self.table_widget)  # Increased padding
        self.table_widget.setItemDelegateForColumn(0, padded_delegate)

        # Populate the table
        self.populate_table()

        # Add the table to the main layout
        self.main_layout.addWidget(self.table_widget)

        # Add buttons for Add Record and Reset Table
        self.button_layout = QHBoxLayout()

        self.button_layout.addStretch()  # Add stretch to the left to center the buttons

        self.button_layout.setSpacing(30)  # Increased spacing between buttons for better separation

        self.add_record_button = QPushButton("Add Record")
        self.add_record_button.setStyleSheet("""
            background-color: #0067a3;  /* Dark Gray */
            border-radius: 10px;
            border: none;
            color: white;  /* Text color for better contrast */
        """)
        self.add_record_button.setMinimumHeight(50)  # Increased button height
        self.add_record_button.setMinimumWidth(200)  # Increased button width
        self.add_record_button.setFont(QFont("Arial", 16))  # Larger font size
        self.add_record_button.clicked.connect(self.show_add_dialog)

        self.reset_table_button = QPushButton("Reset Table")
        self.reset_table_button.setStyleSheet("""
            background-color: #732929;  /* Dark Gray */
            border-radius: 10px;
            border: none;
            color: white;  /* Text color for better contrast */
        """)
        self.reset_table_button.setMinimumHeight(50)  # Increased button height
        self.reset_table_button.setMinimumWidth(200)  # Increased button width
        self.reset_table_button.setFont(QFont("Arial", 16))  # Larger font size
        self.reset_table_button.clicked.connect(self.reset_table)

        self.button_layout.addWidget(self.add_record_button)
        self.button_layout.addWidget(self.reset_table_button)

        self.button_layout.addStretch()  # Add stretch to the right to center the buttons

        self.main_layout.addLayout(self.button_layout)

        # Connect cell click event
        self.table_widget.cellClicked.connect(self.on_cell_clicked)

    def set_dark_theme(self):
        """Set the dark theme using a palette."""
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
                # Ensure all records have 'was_performed' and 'isSong' keys
                for record in data:
                    if 'was_performed' not in record:
                        record['was_performed'] = False
                    if 'isSong' not in record:
                        record['isSong'] = False
                return data
        return []

    def save_data(self):
        """Save the current data to the JSON file."""
        with open(self.data_file, 'w') as file:
            json.dump(self.data, file)

    def populate_table(self):
        """Populate the table with the current data."""
        # Disable sorting while populating to prevent interference
        self.table_widget.setSortingEnabled(False)

        # Clear the table
        self.table_widget.setRowCount(0)

        # Copy and sort the data
        all_records = self.data.copy()

        # Sort the records based on the current sorting column and order
        header = self.table_widget.horizontalHeader()
        sort_column = header.sortIndicatorSection()
        sort_order = header.sortIndicatorOrder()
        reverse = sort_order == Qt.SortOrder.DescendingOrder

        # Determine the key for sorting based on the column
        if sort_column == 0:  # Name
            key_func = lambda x: x['name'].lower()  # Case-insensitive
        elif sort_column == 1:  # Practice Count
            key_func = lambda x: x['practice_count']
        elif sort_column == 2:  # Last Practiced
            def last_practiced_key(record):
                if record['last_practiced'] is None:
                    # 'Never' records, assign maximum elapsed time
                    return float('inf')
                else:
                    try:
                        last_practiced_date = datetime.strptime(record['last_practiced'], '%Y-%m-%d').date()
                        elapsed_days = (datetime.now().date() - last_practiced_date).days
                        return elapsed_days
                    except ValueError:
                        return float('inf')  # Treat invalid dates as 'Never'

            key_func = last_practiced_key
        elif sort_column == 3:  # Was Performed
            key_func = lambda x: x.get('was_performed', False)
        elif sort_column == 4:  # Is Song
            key_func = lambda x: x.get('isSong', False)
        else:
            key_func = lambda x: x['name'].lower()

        # Sort the records
        all_records.sort(key=key_func, reverse=reverse)

        # Keep track of displayed records
        self.displayed_records = all_records

        # Add records to the table
        for record in all_records:
            self.add_record_to_table(record)

        # Adjust column widths
        # Set the 'Name' column (column index 0) to Fixed and set its width
        self.table_widget.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table_widget.setColumnWidth(0, 300)  # Set to desired width in pixels

        # Set the rest of the columns to Stretch
        for i in range(1, self.table_widget.columnCount()):
            self.table_widget.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

        # Re-enable sorting
        self.table_widget.setSortingEnabled(True)

    def add_record_to_table(self, record):
        """Add a record to the table."""
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        # Create a font with increased size for the Name column
        name_font = QFont()
        name_font.setPointSize(18)  # Larger font size for name

        # Determine the text color based on 'was_performed' and 'isSong' status
        isSong = record.get('isSong', False)
        wasPerformed = record.get('was_performed', False)

        text_color = QColor("#c9c9c9")

        if not isSong:
            text_color = QColor("#a1633a")
        elif wasPerformed:
            text_color = QColor("#02a3a3")

        # Name
        name_item = QTableWidgetItem(record['name'])
        name_item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        name_item.setForeground(text_color)  # Set text color
        name_item.setFont(name_font)  # Set font size
        self.table_widget.setItem(row_position, 0, name_item)

        # Adjust font size for other columns
        other_font = QFont()
        other_font.setPointSize(14)  # Larger font size for other columns

        # Practice Count
        practice_count_item = QTableWidgetItem(str(record['practice_count']))
        practice_count_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        practice_count_item.setForeground(text_color)
        practice_count_item.setFont(other_font)
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

        # Use the custom LastPracticedItem
        last_practiced_item = LastPracticedItem(last_practiced_text)
        last_practiced_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        last_practiced_item.setForeground(text_color)
        last_practiced_item.setFont(other_font)
        self.table_widget.setItem(row_position, 2, last_practiced_item)

        # Was Performed
        was_performed_text = "Yes" if wasPerformed else "No"
        was_performed_item = QTableWidgetItem(was_performed_text)
        was_performed_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        was_performed_item.setForeground(text_color)
        was_performed_item.setFont(other_font)
        self.table_widget.setItem(row_position, 3, was_performed_item)

        # Is Song
        is_song_text = "Yes" if isSong else "No"
        is_song_item = QTableWidgetItem(is_song_text)
        is_song_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        is_song_item.setForeground(text_color)
        is_song_item.setFont(other_font)
        self.table_widget.setItem(row_position, 4, is_song_item)

        # Edit Button with custom icon
        edit_button = QPushButton()
        edit_button.setIcon(self.edit_icon)
        edit_button.setIconSize(QSize(24, 24))  # Increased icon size
        edit_button.setFixedSize(50, 32)  # Increased button size
        edit_button.setStyleSheet("QPushButton { border: none; }")  # Make button borderless
        # Connect the edit button click to a handler with the current row
        edit_button.clicked.connect(partial(self.on_edit_button_click, row_position))
        self.table_widget.setCellWidget(row_position, 5, edit_button)

    def on_edit_button_click(self, row):
        """Handle clicks on the edit button."""
        record = self.displayed_records[row]
        self.show_edit_dialog(record)

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
        dialog.resize(500, 350)  # Make the dialog larger (width=500, height=350)
        # Alternatively, set a minimum size
        # dialog.setMinimumSize(500, 350)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(20)  # Increased spacing between widgets

        # Create a larger font for input fields and buttons
        input_font = QFont("Arial", 16)  # Larger font size for inputs
        button_font = QFont("Arial", 14)  # Larger font size for buttons

        # Name Input
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter name")
        name_input.setFont(input_font)  # Set larger font
        name_input.setMinimumHeight(40)  # Increased height
        layout.addWidget(name_input)
        name_input.setFocus()  # Set focus to the name_input field when the dialog opens

        # Checkbox for isSong
        is_song_checkbox = QCheckBox("Is Song")
        is_song_checkbox.setFont(input_font)  # Set larger font
        is_song_checkbox.setChecked(True)
        layout.addWidget(is_song_checkbox)

        # Checkbox for Was Performed
        was_performed_checkbox = QCheckBox("Was Performed")
        was_performed_checkbox.setFont(input_font)  # Set larger font
        was_performed_checkbox.setChecked(False)
        layout.addWidget(was_performed_checkbox)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(30)  # Increased spacing between buttons

        add_button = QPushButton("Add")
        add_button.setStyleSheet("""
            background-color: #0067a3;  /* Dark Gray */
            border-radius: 10px;
            border: none;
        """)
        add_button.setFont(button_font)  # Set larger font
        add_button.setMinimumHeight(50)  # Increased button height
        add_button.setMinimumWidth(150)  # Increased button width

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            background-color: #696969;  /* Dark Gray */
            border-radius: 10px;
            border: none;
        """)
        cancel_button.setFont(button_font)  # Set larger font
        cancel_button.setMinimumHeight(50)  # Increased button height
        cancel_button.setMinimumWidth(150)  # Increased button width

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
            record = self.displayed_records[row]
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

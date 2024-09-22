# edit_window.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QCheckBox, QMessageBox,
    QLabel, QHBoxLayout, QCalendarWidget, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont
from datetime import datetime


class EditWindow(QDialog):
    def __init__(self, app, record):
        """Initialize the EditWindow with the main app and the record."""
        super().__init__(app)
        self.app = app
        self.record = record
        self.setWindowTitle(f"Edit: {self.record['name']}")
        self.setFixedSize(400, 300)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Create a sub-layout for checkboxes
        checkbox_layout = QHBoxLayout()
        checkbox_layout.setSpacing(10)

        # Create the 'Is Song' checkbox and store it as an instance variable
        self.is_song_checkbox = QCheckBox("Is Song")
        self.is_song_checkbox.setChecked(self.record.get('isSong', True))
        self.is_song_checkbox.stateChanged.connect(self.toggle_is_song)
        checkbox_layout.addWidget(self.is_song_checkbox)

        # Create the 'Was Performed' checkbox and store it as an instance variable
        self.was_performed_checkbox = QCheckBox("Was Performed")
        self.was_performed_checkbox.setChecked(self.record.get('was_performed', False))
        self.was_performed_checkbox.stateChanged.connect(self.toggle_was_performed)
        checkbox_layout.addWidget(self.was_performed_checkbox)

        main_layout.addLayout(checkbox_layout)
        
        # Create a sub-layout for buttons
        button_layout = QVBoxLayout()
        button_layout.addItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))  # Add space at top

        # Create the buttons
        add_practice_session_btn = QPushButton("Add Practice Session")
        add_practice_session_btn.setStyleSheet("""
            background-color: #0067a3;  /* Dark Gray */
            border-radius: 10px;
            border: none;
        """)
        edit_last_practiced_btn = QPushButton("Edit Last Practiced")
        edit_last_practiced_btn.setStyleSheet("""
            background-color: #585959;  /* Dark Gray */
            border-radius: 10px;
            border: none;
        """)
        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("""
            background-color: #8f1d00;  /* Dark Gray */
            border-radius: 10px;
            border: none;
        """)

        # Set fixed heights to match the original Kivy code
        edit_last_practiced_btn.setFixedHeight(50)
        add_practice_session_btn.setFixedHeight(50)
        delete_btn.setFixedHeight(50)

        # Connect button events
        edit_last_practiced_btn.clicked.connect(self.on_edit_last_practiced)
        add_practice_session_btn.clicked.connect(self.on_add_practice_session)
        delete_btn.clicked.connect(self.on_delete)

        # Add buttons to the button layout
        button_layout.addWidget(add_practice_session_btn)
        button_layout.addWidget(edit_last_practiced_btn)
        button_layout.addWidget(delete_btn)
        #button_layout.addItem(
        #    QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))  # Add space at bottom

        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    def toggle_is_song(self, state):
        """Update the isSong field when the checkbox is toggled."""
        self.record['isSong'] = self.is_song_checkbox.isChecked()
        self.app.save_data()
        self.app.populate_table()

    def toggle_was_performed(self, state):
        """Update the was_performed field when the checkbox is toggled."""
        self.record['was_performed'] = self.was_performed_checkbox.isChecked()
        self.app.save_data()
        self.app.populate_table()

    def on_edit_last_practiced(self):
        """Open the custom date picker."""
        date_dialog = QDialog(self)
        date_dialog.setWindowTitle("Select Date")
        date_dialog.setFixedSize(400, 400)

        layout = QVBoxLayout(date_dialog)
        calendar = QCalendarWidget()
        if self.record['last_practiced']:
            last_date = datetime.strptime(self.record['last_practiced'], '%Y-%m-%d')
            calendar.setSelectedDate(QDate(last_date.year, last_date.month, last_date.day))
        else:
            calendar.setSelectedDate(QDate.currentDate())

        layout.addWidget(calendar)

        # Buttons
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        # Connect buttons
        def on_ok():
            selected_date = calendar.selectedDate().toString('yyyy-MM-dd')
            self.record['last_practiced'] = selected_date
            if self.record['practice_count'] == 0:
                self.record['practice_count'] = 1
            self.app.save_data()
            self.app.populate_table()
            date_dialog.accept()
            self.accept()

        def on_cancel():
            date_dialog.reject()

        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(on_cancel)

        date_dialog.exec()

    def on_add_practice_session(self):
        """Show a confirmation dialog before incrementing the practice session."""
        reply = QMessageBox.question(
            self, "Confirm Add Session",
            "Are you sure you want to add a practice session?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.record['practice_count'] += 1
            self.record['last_practiced'] = datetime.now().strftime('%Y-%m-%d')
            self.app.save_data()
            self.app.populate_table()
            self.accept()

    def on_delete(self):
        """Confirm and delete the record."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this record?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.app.data.remove(self.record)
            self.app.save_data()
            self.app.populate_table()
            self.accept()

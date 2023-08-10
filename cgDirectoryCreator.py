from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
                             QSpinBox, QLabel, QFormLayout, QScrollArea, QFrame, QMessageBox,
                             QMenuBar, QMenu, QDialog, QFileDialog, QTextEdit)
from PyQt5.QtCore import Qt
import os

PREFERENCES_FILE = "preferences.txt"


def parse_directory_structure(file_content):
    """Parse directory scaffold from the .txt content into a nested dictionary."""
    lines = file_content.split("\n")
    dir_structure = {"JOB#_ProjectName": {}}
    stack = [dir_structure["JOB#_ProjectName"]]

    for line in lines:
        if not line.strip():
            continue

        depth = line.count("|  ")
        name = line.split("--")[-1].strip()

        while depth + 1 < len(stack):
            stack.pop()

        current_dict = stack[-1]
        new_dict = {}
        current_dict[name] = new_dict

        stack.append(new_dict)

    return dir_structure



def create_directories(base_path, structure):
    """Recursively create directories based on the nested dictionary."""
    for name, subdirs in structure.items():
        new_path = os.path.join(base_path, name)
        os.makedirs(new_path, exist_ok=True)
        create_directories(new_path, subdirs)


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        layout = QVBoxLayout()

        # Root Directory Setting
        self.root_dir_input = QLineEdit(self)
        layout.addWidget(QLabel("Root Project Directory:"))
        layout.addWidget(self.root_dir_input)

        # Browse button
        browse_btn = QPushButton("Browse", self)
        browse_btn.clicked.connect(self.browse_directory)
        layout.addWidget(browse_btn)

        # Save button
        save_btn = QPushButton("Save", self)
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)

        # Load current setting
        self.load_settings()

    def browse_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Root Project Directory")
        if dir_path:
            self.root_dir_input.setText(dir_path)

    def load_settings(self):
        try:
            with open(PREFERENCES_FILE, 'r') as file:
                root_dir = file.readline().strip()
                self.root_dir_input.setText(root_dir)
        except FileNotFoundError:
            pass

    def save_settings(self):
        with open(PREFERENCES_FILE, 'w') as file:
            file.write(self.root_dir_input.text())
        QMessageBox.information(self, "Information", "Settings saved!")
        self.close()

class VFXProjectSetup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CG Directory Creator")  # Setting the window title
        self.shot_spinboxes = []
        self.prev_shot_values = []  # List to store shot spin boxes
        self.initUI()
        self.resize(400, 800)

    def initUI(self):
        layout = QVBoxLayout()

        # Menu bar with "Settings" menu
        menu_bar = QMenuBar(self)
        settings_menu = QMenu("Settings", self)
        set_dir_action = settings_menu.addAction("Set Root Project Directory")
        set_dir_action.triggered.connect(self.open_settings)
        menu_bar.addMenu(settings_menu)
        layout.addWidget(menu_bar)

        # Project Number
        self.project_num_input = QLineEdit(self)
        self.project_num_input.setPlaceholderText("Manually enter project number or generate")
        layout.addWidget(self.project_num_input)

        # Generate Random Number Button
        self.generate_btn = QPushButton("Generate Project Number", self)
        self.generate_btn.clicked.connect(self.generate_random_num)
        layout.addWidget(self.generate_btn)

        # Project Name
        self.project_name_input = QLineEdit(self)
        self.project_name_input.setPlaceholderText("Enter project name (e.g., Awesome_CG)")
        layout.addWidget(self.project_name_input)

        # Number of Sequences
        self.num_seq_label = QLabel("Number of Sequences:", self)
        self.num_seq_input = QSpinBox(self)
        self.num_seq_input.valueChanged.connect(self.update_shot_inputs)
        layout.addWidget(self.num_seq_label)
        layout.addWidget(self.num_seq_input)

        # Dynamic input for the number of shots per sequence
        self.shot_inputs_container = QFrame(self)
        self.shot_inputs_layout = QFormLayout()
        self.shot_inputs_container.setLayout(self.shot_inputs_layout)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.shot_inputs_container)
        layout.addWidget(scroll)

        # Project Notes Input
        self.project_notes_input = QTextEdit(self)
        self.project_notes_input.setPlaceholderText("Enter project notes here...")
        layout.addWidget(QLabel("Project Notes:"))
        layout.addWidget(self.project_notes_input)

        # Setup Button
        self.setup_btn = QPushButton("Setup Project", self)
        self.setup_btn.clicked.connect(self.setup_project)
        layout.addWidget(self.setup_btn)

        # Open Existing Project Button
        self.open_existing_btn = QPushButton("Open Existing Project", self)
        self.open_existing_btn.clicked.connect(self.open_existing_project)
        layout.addWidget(self.open_existing_btn)

        # Update Project Button (initially hidden)
        self.update_project_btn = QPushButton("Update Project", self)
        self.update_project_btn.clicked.connect(self.update_project)  # Connect to a method we'll implement next
        self.update_project_btn.hide()  # Hidden initially
        layout.addWidget(self.update_project_btn)

        self.setLayout(layout)

    def open_settings(self):
        settings_dialog = SettingsDialog()
        settings_dialog.exec_()

    def generate_random_num(self):
        import random
        random_num = str(random.randint(10000000, 99999999))
        self.project_num_input.setText(random_num)

    def update_shot_inputs(self):
        # Store the current values before clearing
        current_values = [spinbox.value() for spinbox in self.shot_spinboxes]

        # Clear existing shot inputs
        for i in reversed(range(self.shot_inputs_layout.count())):
            widget = self.shot_inputs_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        # Clear the list of shot spinboxes
        self.shot_spinboxes.clear()

        # Create new shot inputs
        num_seqs = self.num_seq_input.value()
        for i in range(num_seqs):
            spinbox = QSpinBox(self)
            spinbox.setMaximum(999)
            spinbox.setValue(1)  # Default to 1 shot
            # Set value to the stored value if it exists
            if i < len(current_values):
                spinbox.setValue(current_values[i])
            self.shot_inputs_layout.addRow(f"Shots in Sequence {i + 1}:", spinbox)

            # Add the spinbox to the list
            self.shot_spinboxes.append(spinbox)

    def setup_project(self):
        # Determine the directory where cgDirectoryCreator.py is located
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # Construct the path to directory_scaffold.txt relative to cgDirectoryCreator.py
        scaffold_path = os.path.join(base_dir, "directory_scaffold.txt")

        # Reading and parsing the directory structure
        with open(scaffold_path, "r") as file:
            directory_scaffold = file.read()

        parsed_structure = parse_directory_structure(directory_scaffold)

        # Replacing placeholders and constructing the directories
        project_name = f"{self.project_num_input.text()}_{self.project_name_input.text()}"
        parsed_structure = parsed_structure["JOB#_ProjectName"]
        parsed_structure.pop("JOB#_ProjectName", None)

        num_seqs = self.num_seq_input.value()
        for i in range(num_seqs):
            seq_name = f"seq_{i + 1:04d}"
            num_shots = self.shot_spinboxes[i].value()  # Use the list directly
            shots = {f"sh_{j + 1:04d}": parsed_structure["work"]["sequences"]["seq_0001"]["sh_0001"]
                     for j in range(num_shots)}
            parsed_structure["work"]["sequences"][seq_name] = shots
            parsed_structure["renders"]["sequences"][seq_name] = shots

        # Create the directories
        try:
            print(f"Checking preferences file at: {PREFERENCES_FILE}")
            if os.path.exists(PREFERENCES_FILE):
                with open(PREFERENCES_FILE, 'r') as file:
                    print("Content of preferences file:", file.read())
            else:
                print(f"Preferences file not found at: {PREFERENCES_FILE}")

            with open(PREFERENCES_FILE, 'r') as file:
                root_dir = file.readline().strip()
                print(f"Using root directory: {root_dir}")
            project_folder_path = os.path.join(root_dir, project_name)
            create_directories(project_folder_path, parsed_structure)

            # Save project notes to the production\docs subfolder
            docs_path = os.path.join(root_dir, project_name, "work", "production", "docs", "project_notes.txt")
            with open(docs_path, 'w') as notes_file:
                notes_file.write(self.project_notes_input.toPlainText())

            QMessageBox.information(self, "Information", "Project setup completed!")
        except FileNotFoundError:
            QMessageBox.warning(self, "Warning", "Root Project Directory not set. Use the Settings menu to set it.")

    def open_existing_project(self):
        # Load root directory from preferences.txt
        root_dir = ""
        try:
            with open(PREFERENCES_FILE, 'r') as file:
                root_dir = file.readline().strip()
        except FileNotFoundError:
            QMessageBox.warning(self, "Warning", "Root Project Directory not set. Use the Settings menu to set it.")
            return

        # Open dialog to select project directory
        project_dir = QFileDialog.getExistingDirectory(self, "Select Project Directory", root_dir)
        if not project_dir:
            return

        # Extract project number and name
        project_name = os.path.basename(project_dir)
        if '_' in project_name:
            project_num, project_name = project_name.split('_', 1)
            self.project_num_input.setText(project_num)
            self.project_name_input.setText(project_name)

        # Parse sequences and shots
        sequences_dir = os.path.join(project_dir, "work", "sequences")
        if os.path.exists(sequences_dir):
            sequences = [d for d in os.listdir(sequences_dir) if os.path.isdir(os.path.join(sequences_dir, d)) and d.startswith("seq_")]
            self.num_seq_input.setValue(len(sequences))
            for i, seq in enumerate(sequences):
                shots = [s for s in os.listdir(os.path.join(sequences_dir, seq)) if s.startswith("sh_")]
                if i < len(self.shot_spinboxes):
                    self.shot_spinboxes[i].setValue(len(shots))

        # Load project notes
        notes_path = os.path.join(project_dir, "work", "production", "docs", "project_notes.txt")
        if os.path.exists(notes_path):
            with open(notes_path, 'r') as notes_file:
                self.project_notes_input.setPlainText(notes_file.read())
        self.original_project_notes = self.project_notes_input.toPlainText()

        # Show the Update Project button
        self.update_project_btn.show()
        # After selecting the folder and storing input field values:
        self.setup_btn.hide()

        # Storing the initial state
        self.original_num_seqs = self.num_seq_input.value()
        self.original_seq_shot_values = [spinbox.value() for spinbox in self.shot_spinboxes]

    def reset_to_original_values(self):
        self.num_seq_input.setValue(self.original_num_seqs)
        self.project_notes_input.setPlainText(self.original_project_notes)
        for i, spinbox in enumerate(self.shot_spinboxes):
            if i < len(self.original_seq_shot_values):
                spinbox.setValue(self.original_seq_shot_values[i])

    def update_project(self):
        changes_made = False

        # Reading and parsing the directory structure from directory_scaffold.txt
        with open("directory_scaffold.txt", "r") as file:
            directory_scaffold = file.read()
        parsed_structure = parse_directory_structure(directory_scaffold)

        # Replacing placeholders and constructing the directories
        project_name = f"{self.project_num_input.text()}_{self.project_name_input.text()}"
        parsed_structure = parsed_structure["JOB#_ProjectName"]
        parsed_structure.pop("JOB#_ProjectName", None)

        # Identify new sequences and shots based on stored values
        new_sequences = []
        new_shots = []
        current_num_seqs = self.num_seq_input.value()

        # Check for sequence reduction
        if self.num_seq_input.value() < self.original_num_seqs:
            QMessageBox.warning(self, "Warning", "Sequence deletion or shot removal is not allowed. Reverting back all changes including notes.")
            self.reset_to_original_values()
            return

        # Check for shot reduction within sequences
        for i in range(self.original_num_seqs):
            if self.shot_spinboxes[i].value() < self.original_seq_shot_values[i]:
                QMessageBox.warning(self, "Warning", "Sequence deletion or shot removal is not allowed. Reverting back all changes including notes.")
                self.reset_to_original_values()
                return

        # Identifying new sequences
        for i in range(self.original_num_seqs, current_num_seqs):
            new_sequences.append(f"seq_{i + 1:04d}")

        # Identifying new shots within existing sequences
        for i in range(self.original_num_seqs):
            seq_name = f"seq_{i + 1:04d}"
            for j in range(self.original_seq_shot_values[i], self.shot_spinboxes[i].value()):
                new_shots.append(f"{seq_name}/sh_{j + 1:04d}")

        # Prepare the confirmation message
        changes_msg = "The following changes will be made:\n\n"

        if new_sequences:
            changes_msg += "New Sequences:\n" + "\n".join(new_sequences) + "\n\n"
        if new_shots:
            changes_msg += "New Shots:\n" + "\n".join(new_shots) + "\n\n"
        if self.project_notes_input.toPlainText() != self.original_project_notes:
            changes_made = True
            changes_msg += "Project notes will be updated.\n\n"

        # If there are changes, show the confirmation message
        if changes_made:
            changes_msg += "Do you want to continue?"
            reply = QMessageBox.question(self, 'Review Changes', changes_msg, QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.No:
                # Reset to original values
                self.reset_to_original_values()
                return
        else:
            QMessageBox.information(self, "Info", "No changes have been made.")
            return

        # Define project_folder_path before using it for directory creation
        with open(PREFERENCES_FILE, 'r') as file:
            root_dir = file.readline().strip()
        project_folder_path = os.path.join(root_dir, project_name)

        # Update the project_notes.txt
        if self.project_notes_input.toPlainText() != self.original_project_notes:
            # Define the correct path to project_notes.txt
            notes_filepath = os.path.join(project_folder_path, "work", "production", "docs", "project_notes.txt")
            with open(notes_filepath, 'w') as notes_file:
                notes_file.write(self.project_notes_input.toPlainText())
            self.original_project_notes = self.project_notes_input.toPlainText()

        # Create the directories for new sequences and shots
        base_paths = [os.path.join(project_folder_path, dir_name) for dir_name in ["renders", "work"]]
        for base_path in base_paths:
            # Create new sequences
            for seq in new_sequences:
                seq_path = os.path.join(base_path, "sequences", seq)
                os.makedirs(seq_path, exist_ok=True)

                # Create shots for the new sequences from sh_0001 to specified number
                for shot_num in range(1, self.shot_spinboxes[int(seq.split('_')[-1]) - 1].value() + 1):
                    shot_name = f"sh_{shot_num:04d}"
                    shot_path = os.path.join(seq_path, shot_name)
                    os.makedirs(shot_path, exist_ok=True)

            # Create new shots within existing sequences
            for shot in new_shots:
                seq_name, shot_name = shot.split("/")
                shot_path = os.path.join(base_path, "sequences", seq_name, shot_name)
                os.makedirs(shot_path, exist_ok=True)

        try:
            create_directories(project_folder_path, parsed_structure)
            QMessageBox.information(self, "Success", "Updates made successfully!")

            # After directories are successfully created:
            self.original_num_seqs = self.num_seq_input.value()
            self.original_seq_shot_values = [spinbox.value() for spinbox in self.shot_spinboxes]

        except Exception as e:
            print(f"Error creating directories: {e}")
            QMessageBox.warning(self, "Warning",
                                "There was an error creating the directories. Please check the application logs for details.")


if __name__ == '__main__':
    app = QApplication([])
    window = VFXProjectSetup()
    window.show()
    app.exec_()

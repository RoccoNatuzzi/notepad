import customtkinter as ctk
import os
import sys
import tkinter as tk
from tkinter import filedialog
from character_differ import get_character_diffs
from diff_viewer import DiffViewer
from ui_components import TextEditorWithLineNumbers

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class TextDiffApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_default_color_theme(resource_path("theme.json"))
        ctk.set_appearance_mode("light")

        self.title("DiffNote")
        self.geometry("1200x800")

        # configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Main Content Frame ---
        # The top frame with buttons is removed, the menu is used instead.
        self.main_content = ctk.CTkFrame(self)
        self.main_content.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        self._create_editor_view()
        self._create_comparison_view()

        self.show_editor_view()

    def _create_editor_view(self):
        self.editor_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.editor_frame.grid(row=0, column=0, sticky="nsew")
        self.editor_frame.grid_rowconfigure(1, weight=1)
        self.editor_frame.grid_columnconfigure(0, weight=1)

        # The editor toolbar has been replaced by the main menu bar.

        self.tab_view = ctk.CTkTabview(self.editor_frame, anchor="w") # Align tabs to the left
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # Data structures to manage tabs
        self.editor_textboxes = {}
        self.tab_filepaths = {}
        self.new_file_count = 0

        self._create_menu()
        self.add_new_tab() # Start with a blank tab

    def _create_menu(self):
        """Creates the main window menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)

        file_menu.add_command(label="New File", command=lambda: self.add_new_tab())
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", command=self.close_current_tab)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Compare Files...", command=self.start_comparison)

    def _create_comparison_view(self):
        self.comparison_frame = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.comparison_frame.grid(row=0, column=0, sticky="nsew")
        self.comparison_frame.grid_rowconfigure(0, weight=1)
        self.comparison_frame.grid_columnconfigure(0, weight=1)

        self.diff_viewer = DiffViewer(self.comparison_frame, merge_callback=self._perform_merge)
        self.diff_viewer.pack(fill="both", expand=True)

    def show_editor_view(self):
        self.editor_frame.tkraise()

    def show_comparison_view(self):
        self.comparison_frame.tkraise()

    def add_new_tab(self, filepath=None):
        """Creates a new tab, either for a new file or an existing one."""
        if filepath:
            filename = os.path.basename(filepath)
            # Prevent opening the same file in multiple tabs
            if filepath in self.tab_filepaths.values():
                for tab_name, f_path in self.tab_filepaths.items():
                    if f_path == filepath:
                        self.tab_view.set(tab_name)
                        return
            tab_name = filename
        else:
            self.new_file_count += 1
            tab_name = f"Untitled-{self.new_file_count}"

        tab_frame = self.tab_view.add(tab_name)
        editor_with_linenumbers = TextEditorWithLineNumbers(tab_frame)
        editor_with_linenumbers.pack(fill="both", expand=True)

        textbox = editor_with_linenumbers

        self.editor_textboxes[tab_name] = textbox
        self.tab_filepaths[tab_name] = filepath

        if filepath:
            with open(filepath, 'r', encoding='utf-8') as f:
                textbox.insert("1.0", f.read())

        self.tab_view.set(tab_name)

    def open_file(self):
        """Opens one or more files in new tabs."""
        filepaths = filedialog.askopenfilenames()
        for filepath in filepaths:
            self.add_new_tab(filepath=filepath)

    def save_file(self):
        """Saves the content of the currently active tab."""
        current_tab = self.tab_view.get()
        if not current_tab:
            return

        filepath = self.tab_filepaths.get(current_tab)
        if filepath:
            content = self.editor_textboxes[current_tab].get("1.0", "end-1c")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        else:
            self.save_file_as()

    def save_file_as(self):
        """Saves the current tab's content to a new file."""
        current_tab = self.tab_view.get()
        if not current_tab:
            return

        new_filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=current_tab if not self.tab_filepaths.get(current_tab) else None
        )
        if not new_filepath:
            return

        content = self.editor_textboxes[current_tab].get("1.0", "end-1c")
        with open(new_filepath, "w", encoding="utf-8") as f:
            f.write(content)

        # Workaround for no tab rename: close old, open new
        textbox_content = self.editor_textboxes[current_tab].get("1.0", "end-1c")
        self.close_current_tab(force=True)
        self.add_new_tab(filepath=new_filepath)
        self.editor_textboxes[os.path.basename(new_filepath)].delete("1.0", "end")
        self.editor_textboxes[os.path.basename(new_filepath)].insert("1.0", textbox_content)


    def close_current_tab(self, force=False):
        """Closes the currently active tab."""
        current_tab = self.tab_view.get()
        if not current_tab:
            return

        # In a real app, we'd check for unsaved changes here.

        self.tab_view.delete(current_tab)
        del self.editor_textboxes[current_tab]
        if self.tab_filepaths.get(current_tab):
            del self.tab_filepaths[current_tab]

        if len(self.tab_view._name_list) == 0:
            self.add_new_tab()

    def start_comparison(self):
        """
        Prompts the user to select two files and initiates the character-level comparison.
        """
        file1_path = filedialog.askopenfilename(title="Select the First File")
        if not file1_path:
            return

        file2_path = filedialog.askopenfilename(title="Select the Second File")
        if not file2_path:
            return

        self.file1_path = file1_path
        self.file2_path = file2_path

        with open(file1_path, 'r', encoding='utf-8') as f:
            self.text1 = f.read()
        with open(file2_path, 'r', encoding='utf-8') as f:
            self.text2 = f.read()

        opcodes = get_character_diffs(self.text1, self.text2)
        self.diff_viewer.display_diff(self.text1, self.text2, opcodes)
        self.show_comparison_view()

    def _perform_merge(self, direction, op_idx):
        """Applies a change from one file to the other based on character diff opcodes."""
        opcodes = self.diff_viewer.opcodes
        _, i1, i2, j1, j2 = opcodes[op_idx]

        if direction == 'to_left':  # Apply change from right to left
            self.text1 = self.text1[:i1] + self.text2[j1:j2] + self.text1[i2:]
        elif direction == 'to_right':  # Apply change from left to right
            self.text2 = self.text2[:j1] + self.text1[i1:i2] + self.text2[j2:]

        # Save the modified content back to the original files
        with open(self.file1_path, 'w', encoding='utf-8') as f:
            f.write(self.text1)
        with open(self.file2_path, 'w', encoding='utf-8') as f:
            f.write(self.text2)

        # Rerun the comparison and refresh the view
        new_opcodes = get_character_diffs(self.text1, self.text2)
        self.diff_viewer.display_diff(self.text1, self.text2, new_opcodes)


if __name__ == "__main__":
    app = TextDiffApp()
    app.mainloop()

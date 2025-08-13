import customtkinter as ctk
import os
import sys
import tkinter as tk
from tkinter import filedialog
from src.file_differ import compare_files_to_unified_diff
from src.ui_components import TextEditorWithLineNumbers

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
        self.comparison_frame = ctk.CTkFrame(self.main_content)
        self.comparison_frame.grid(row=0, column=0, sticky="nsew")
        self.comparison_frame.grid_rowconfigure(0, weight=1)
        self.comparison_frame.grid_columnconfigure(0, weight=1)
        self.comparison_frame.grid_columnconfigure(1, weight=1)

        self.file1_scroll_frame = ctk.CTkScrollableFrame(self.comparison_frame, label_text="File 1")
        self.file1_scroll_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

        self.file2_scroll_frame = ctk.CTkScrollableFrame(self.comparison_frame, label_text="File 2")
        self.file2_scroll_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)

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
        Prompts the user to select two files and initiates the comparison.
        """
        file1_path = filedialog.askopenfilename(title="Select the First File")
        if not file1_path:
            return

        file2_path = filedialog.askopenfilename(title="Select the Second File")
        if not file2_path:
            return

        diff_results = compare_files_to_unified_diff(file1_path, file2_path)

        # This will be implemented in the next step.
        self._display_diff(file1_path, file2_path, diff_results)

        self.show_comparison_view()

    def _display_diff(self, file1_path, file2_path, diff_results):
        """Displays the diff with interactive merge buttons by tracking line numbers."""
        self.file1_path = file1_path
        self.file2_path = file2_path
        self.file1_lines = [line.rstrip('\n') for line in open(file1_path, 'r', encoding='utf-8').readlines()]
        self.file2_lines = [line.rstrip('\n') for line in open(file2_path, 'r', encoding='utf-8').readlines()]

        for widget in self.file1_scroll_frame.winfo_children(): widget.destroy()
        for widget in self.file2_scroll_frame.winfo_children(): widget.destroy()

        f1_idx, f2_idx = 0, 0

        for line in diff_results:
            if line.startswith('@@'):
                # Extract line numbers from hunk header, e.g., @@ -1,5 +1,5 @@
                parts = line.split(' ')
                f1_start = int(parts[1].split(',')[0].replace('-', '')) - 1
                f2_start = int(parts[2].split(',')[0].replace('+', '')) - 1
                f1_idx, f2_idx = f1_start, f2_start
                continue
            if line.startswith('---') or line.startswith('+++'):
                continue

            line_type = line[0]
            line_content = line[1:]

            if line_type == ' ':
                self._render_line('common', line_content)
                f1_idx += 1
                f2_idx += 1
            elif line_type == '-':
                self._render_line('deletion', line_content, f1_idx, f2_idx)
                f1_idx += 1
            elif line_type == '+':
                self._render_line('addition', line_content, f1_idx, f2_idx)
                f2_idx += 1

    def _render_line(self, line_type, content, f1_idx=None, f2_idx=None):
        """Renders a single line and a merge button if it's a diff."""
        DELETION_COLOR, ADDITION_COLOR, EMPTY_COLOR = "#FADBD8", "#D4EFDF", "#F2F3F4"
        mono_font = ctk.CTkFont(family="Courier", size=12)

        if line_type == 'common':
            ctk.CTkLabel(self.file1_scroll_frame, text=content, anchor="w", font=mono_font).pack(fill="x", expand=True)
            ctk.CTkLabel(self.file2_scroll_frame, text=content, anchor="w", font=mono_font).pack(fill="x", expand=True)
        elif line_type == 'deletion':
            f = ctk.CTkFrame(self.file1_scroll_frame, fg_color=DELETION_COLOR)
            f.pack(fill="x", expand=True)
            ctk.CTkLabel(f, text=content, anchor="w", font=mono_font, fg_color="transparent").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(f, text="→", width=30, command=lambda i1=f1_idx, i2=f2_idx: self._perform_merge('to_right', i1, i2)).pack(side="right")
            ctk.CTkLabel(self.file2_scroll_frame, text="", fg_color=EMPTY_COLOR, anchor="w", font=mono_font).pack(fill="x", expand=True)
        elif line_type == 'addition':
            ctk.CTkLabel(self.file1_scroll_frame, text="", fg_color=EMPTY_COLOR, anchor="w", font=mono_font).pack(fill="x", expand=True)
            f = ctk.CTkFrame(self.file2_scroll_frame, fg_color=ADDITION_COLOR)
            f.pack(fill="x", expand=True)
            ctk.CTkLabel(f, text=content, anchor="w", font=mono_font, fg_color="transparent").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(f, text="←", width=30, command=lambda i1=f1_idx, i2=f2_idx: self._perform_merge('to_left', i1, i2)).pack(side="right")

    def _perform_merge(self, direction, f1_idx, f2_idx):
        """Applies a change from one file to the other and refreshes the view."""
        if direction == 'to_left':
            # An addition on the right is merged left.
            # We take the line from file 2 and insert it into file 1's model.
            if f2_idx < len(self.file2_lines):
                line_to_add = self.file2_lines[f2_idx]
                self.file1_lines.insert(f1_idx, line_to_add)

        elif direction == 'to_right':
            # A deletion on the left is merged right.
            # This means we "undo" the deletion by adding the line to file 2's model.
            if f1_idx < len(self.file1_lines):
                line_to_add = self.file1_lines[f1_idx]
                self.file2_lines.insert(f2_idx, line_to_add)

        # Save the modified content back to the original files to make the change persistent
        with open(self.file1_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.file1_lines))
        with open(self.file2_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.file2_lines))

        # Rerun the comparison on the modified files and refresh the view
        diff_results = compare_files_to_unified_diff(self.file1_path, self.file2_path)
        self._display_diff(self.file1_path, self.file2_path, diff_results)


if __name__ == "__main__":
    app = TextDiffApp()
    app.mainloop()

import customtkinter as ctk
from tkinter import filedialog
from src.file_differ import compare_files_to_unified_diff

class TextDiffApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Modern Text Editor & Diff Tool")
        self.geometry("1200x800")

        # configure grid layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- Top Frame for Buttons ---
        self.top_frame = ctk.CTkFrame(self, height=40)
        self.top_frame.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="ew")

        self.editor_button = ctk.CTkButton(self.top_frame, text="Editor", command=self.show_editor_view)
        self.editor_button.pack(side="left", padx=5, pady=5)

        self.compare_button = ctk.CTkButton(self.top_frame, text="Compare Files", command=self.start_comparison)
        self.compare_button.pack(side="left", padx=5, pady=5)

        # --- Main Content Frame ---
        self.main_content = ctk.CTkFrame(self)
        self.main_content.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.main_content.grid_rowconfigure(0, weight=1)
        self.main_content.grid_columnconfigure(0, weight=1)

        self._create_editor_view()
        self._create_comparison_view()

        self.show_editor_view()

    def _create_editor_view(self):
        self.editor_frame = ctk.CTkFrame(self.main_content)
        self.editor_frame.grid(row=0, column=0, sticky="nsew")
        self.editor_frame.grid_rowconfigure(1, weight=1)
        self.editor_frame.grid_columnconfigure(0, weight=1)

        editor_toolbar = ctk.CTkFrame(self.editor_frame)
        editor_toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        open_btn = ctk.CTkButton(editor_toolbar, text="Open File", command=self.open_file)
        open_btn.pack(side="left", padx=5)

        save_btn = ctk.CTkButton(editor_toolbar, text="Save File", command=self.save_file)
        save_btn.pack(side="left", padx=5)

        self.editor_textbox = ctk.CTkTextbox(self.editor_frame)
        self.editor_textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

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

    def open_file(self):
        filepath = filedialog.askopenfilename()
        if not filepath:
            return
        with open(filepath, "r", encoding="utf-8") as f:
            self.editor_textbox.delete("1.0", "end")
            self.editor_textbox.insert("1.0", f.read())
        self.title(f"Editor - {filepath}")

    def save_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filepath:
            return
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.editor_textbox.get("1.0", "end"))
        self.title(f"Editor - {filepath}")

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
                self._render_line('deletion', line_content, f1_idx)
                f1_idx += 1
            elif line_type == '+':
                self._render_line('addition', line_content, f2_idx)
                f2_idx += 1

    def _render_line(self, line_type, content, line_num=None):
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
            ctk.CTkButton(f, text="→", width=30, command=lambda i=line_num: self._perform_merge('to_right', i)).pack(side="right")
            ctk.CTkLabel(self.file2_scroll_frame, text="", fg_color=EMPTY_COLOR, anchor="w", font=mono_font).pack(fill="x", expand=True)
        elif line_type == 'addition':
            ctk.CTkLabel(self.file1_scroll_frame, text="", fg_color=EMPTY_COLOR, anchor="w", font=mono_font).pack(fill="x", expand=True)
            f = ctk.CTkFrame(self.file2_scroll_frame, fg_color=ADDITION_COLOR)
            f.pack(fill="x", expand=True)
            ctk.CTkLabel(f, text=content, anchor="w", font=mono_font, fg_color="transparent").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(f, text="←", width=30, command=lambda i=line_num: self._perform_merge('to_left', i)).pack(side="right")

    def _perform_merge(self, direction, index):
        """Applies a change from one file to the other and refreshes the view."""
        if direction == 'to_left': # Apply addition from right to left
            line_to_add = self.file2_lines[index]
            # Find where to insert in file 1. This is tricky.
            # A simple approach is to insert it at the same index.
            self.file1_lines.insert(index, line_to_add)
        elif direction == 'to_right': # Apply deletion from left to right (by deleting from right)
            # This means we are accepting the deletion that happened on the left.
            # So we delete the corresponding line from the right side.
            if index < len(self.file2_lines):
                del self.file2_lines[index]

        # Save the modified content back to the original files
        with open(self.file1_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.file1_lines))
        with open(self.file2_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.file2_lines))

        # Rerun the comparison
        diff_results = compare_files_to_unified_diff(self.file1_path, self.file2_path)
        self._display_diff(self.file1_path, self.file2_path, diff_results)


if __name__ == "__main__":
    app = TextDiffApp()
    app.mainloop()

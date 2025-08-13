import customtkinter as ctk
import tkinter as tk

class TextEditorWithLineNumbers(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.line_numbers = tk.Canvas(self, width=40, bg='#2B2B2B', highlightthickness=0)
        self.line_numbers.grid(row=0, column=0, sticky='ns')

        self.textbox = ctk.CTkTextbox(self, wrap='none', corner_radius=0, font=ctk.CTkFont(family="Courier", size=12))
        self.textbox.grid(row=0, column=1, sticky='nsew')

        # Synchronize scrolling
        self.textbox.vbar.configure(command=self.on_scrollbar_scroll)
        self.line_numbers.configure(yscrollcommand=self.textbox.vbar.set)
        self.textbox.bind("<MouseWheel>", self.on_mouse_wheel, add=True)
        self.textbox.bind("<<Modified>>", self.on_text_modified, add=True)

        self._on_resize()

    def on_scrollbar_scroll(self, *args):
        """Called when the textbox's scrollbar is moved."""
        self.line_numbers.yview(*args)
        self._update_line_numbers()

    def on_mouse_wheel(self, event):
        """Called on mouse wheel scroll to sync line numbers."""
        self.after(10, self._update_line_numbers) # Use after to wait for textbox to scroll
        return # Let the event propagate

    def on_text_modified(self, event=None):
        """Called when the text in the textbox is modified."""
        self._update_line_numbers()
        self.textbox.edit_modified(False) # Reset the modified flag

    def _update_line_numbers(self, event=None):
        """Redraws the line numbers."""
        self.line_numbers.delete("all")

        # Get the range of visible lines
        first_visible_line = self.textbox.index("@0,0")
        last_visible_line = self.textbox.index(f"@0,{self.textbox.winfo_height()}")

        first_line_num = int(first_visible_line.split('.')[0])
        last_line_num = int(last_visible_line.split('.')[0])

        # Get the total number of lines
        total_lines = int(self.textbox.index('end-1c').split('.')[0])

        for i in range(first_line_num, last_line_num + 2):
            if i > total_lines:
                break

            # Get the y-coordinate of the line's top-left corner
            dline = self.textbox.dlineinfo(f"{i}.0")
            if dline is None:
                continue

            x, y, _, _, _ = dline
            self.line_numbers.create_text(38, y, anchor='ne', text=str(i), fill='gray')

    def _on_resize(self, event=None):
        """Periodically check for resize and update line numbers."""
        self._update_line_numbers()
        self.after(100, self._on_resize)

    # --- Methods to delegate to the underlying textbox ---
    def insert(self, *args, **kwargs):
        return self.textbox.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.textbox.delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.textbox.get(*args, **kwargs)

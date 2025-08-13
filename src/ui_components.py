import customtkinter as ctk
import tkinter as tk

class TextEditorWithLineNumbers(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Line Numbers Canvas
        self.line_numbers = tk.Canvas(self, width=45, bg='#2B2B2B', highlightthickness=0)
        self.line_numbers.grid(row=0, column=0, sticky='ns')

        # Textbox Widget
        self.textbox = ctk.CTkTextbox(self, wrap='none', corner_radius=0, font=ctk.CTkFont(family="Courier", size=12), border_width=0, activate_scrollbars=False)
        self.textbox.grid(row=0, column=1, sticky='nsew')

        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(self, command=self.on_scrollbar_scroll)
        self.scrollbar.grid(row=0, column=2, sticky='ns')

        # Connect textbox and scrollbar
        self.textbox.configure(yscrollcommand=self.scrollbar.set)

        # --- Event Bindings ---
        self.textbox.bind("<<Modified>>", self._on_text_modified, add=True)
        self.textbox.bind("<Configure>", self._on_scroll, add=True)
        self.textbox.bind("<KeyRelease>", self._on_scroll, add=True)

        # Initial drawing of line numbers
        self.after(200, self._update_line_numbers)

    def on_scrollbar_scroll(self, *args):
        """Called when the scrollbar is moved."""
        self.textbox.yview(*args)
        self._update_line_numbers()

    def _on_scroll(self, event=None):
        self.after(10, self._update_line_numbers)

    def _on_text_modified(self, event=None):
        self._update_line_numbers()
        self.textbox.edit_modified(False)

    def _update_line_numbers(self):
        """Redraws the line number canvas."""
        self.line_numbers.delete("all")

        try:
            # Get the first visible line index
            first_line_index = self.textbox.index("@0,0")

            # Get the y-coordinate of the first visible line. If it's not visible, dlineinfo is None.
            dline = self.textbox.dlineinfo(first_line_index)
            if dline is None: return

            y = dline[1]
            line_num = int(first_line_index.split('.')[0])

            # Draw line numbers for all potentially visible lines
            while y < self.textbox.winfo_height():
                self.line_numbers.create_text(40, y, anchor='ne', text=str(line_num), fill='gray', font=self.textbox.font)

                # Get the y-coordinate of the next line
                next_line_info = self.textbox.dlineinfo(f"{line_num + 1}.0")
                if not next_line_info:
                    break

                y = next_line_info[1]
                line_num += 1
        except Exception:
            # This can fail if the widget is not ready, just ignore
            pass

    # --- Delegated methods ---
    def insert(self, *args, **kwargs):
        return self.textbox.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.textbox.delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.textbox.get(*args, **kwargs)

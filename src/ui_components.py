import customtkinter as ctk
import tkinter as tk

class TextEditorWithLineNumbers(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Main frame configuration
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Line numbers canvas
        self.line_numbers = tk.Canvas(self, width=45, bg='#ECECEC', highlightthickness=0)
        self.line_numbers.grid(row=0, column=0, sticky='ns')

        # Textbox widget
        self.textbox = ctk.CTkTextbox(self, wrap='none', corner_radius=0, font=ctk.CTkFont(family="Courier", size=12), border_width=0, activate_scrollbars=False)
        self.textbox.grid(row=0, column=1, sticky='nsew')

        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(self, command=self._on_scroll)
        self.scrollbar.grid(row=0, column=2, sticky='ns')

        # Connect widgets to the scrollbar
        self.textbox.configure(yscrollcommand=self.scrollbar.set)
        self.line_numbers.configure(yscrollcommand=self.scrollbar.set)

        # Event bindings
        self.textbox.bind("<<Modified>>", self._on_text_modified, add=True)
        self.textbox.bind("<MouseWheel>", self._on_mouse_wheel, add=True)
        self.line_numbers.bind("<MouseWheel>", self._on_mouse_wheel, add=True)

        self.after(100, self._update_line_numbers)

    def _on_scroll(self, *args):
        """Unified scroll command."""
        self.textbox.yview(*args)
        self.line_numbers.yview(*args)
        self.after(10, self._update_line_numbers)

    def _on_mouse_wheel(self, event):
        """Proxy mouse wheel events to the scrollbar."""
        self.scrollbar.set(self.textbox.yview()[0], self.textbox.yview()[1])
        if event.delta > 0:
            self.textbox.yview_scroll(-1, "units")
            self.line_numbers.yview_scroll(-1, "units")
        else:
            self.textbox.yview_scroll(1, "units")
            self.line_numbers.yview_scroll(1, "units")
        self._update_line_numbers()
        return "break" # Prevents the event from propagating further

    def _on_text_modified(self, event=None):
        self.after(10, self._update_line_numbers)
        self.textbox.edit_modified(False)

    def _update_line_numbers(self):
        self.line_numbers.delete("all")

        try:
            # Get the y-position of the top of the visible text
            y_position = self.textbox.yview()[0]

            # Get the line index at the top of the visible area
            first_line_index = self.textbox.index(f"@0,{int(y_position * self.textbox.winfo_height())}")

            # Get line details
            dline = self.textbox.dlineinfo(first_line_index)
            if dline is None: return

            y, line_num = dline[1], int(first_line_index.split('.')[0])

            # Adjust y to be relative to the canvas, not the entire textbox content
            visible_y = y - (y_position * self.textbox.winfo_height())

            # Draw numbers for all visible lines
            while visible_y < self.textbox.winfo_height():
                self.line_numbers.create_text(40, visible_y, anchor='ne', text=str(line_num), fill='#6A6A6A', font=self.textbox.font)

                next_line = f"{line_num + 1}.0"
                dline = self.textbox.dlineinfo(next_line)
                if not dline: break

                visible_y += dline[3] # Add line height to y
                line_num += 1
        except (tk.TclError, ValueError):
            # Can happen if the widget is not ready or text is empty
            pass

    # --- Delegated methods ---
    def insert(self, *args, **kwargs):
        return self.textbox.insert(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.textbox.delete(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.textbox.get(*args, **kwargs)

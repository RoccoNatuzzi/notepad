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

        # Connect only textbox to the scrollbar
        self.textbox.configure(yscrollcommand=self.scrollbar.set)
        # Do not connect line_numbers to scrollbar as we want it to stay fixed

        # Event bindings
        self.textbox.bind("<<Modified>>", self._on_text_modified, add=True)
        self.textbox.bind("<MouseWheel>", self._on_mouse_wheel, add=True)
        self.line_numbers.bind("<MouseWheel>", self._on_mouse_wheel, add=True)

        self.after(100, self._update_line_numbers)

    def _on_scroll(self, *args):
        """Scroll only the textbox, then update line numbers."""
        self.textbox.yview(*args)
        self.after(10, self._update_line_numbers)

    def _on_mouse_wheel(self, event):
        """Proxy mouse wheel events to the scrollbar for textbox only."""
        self.scrollbar.set(self.textbox.yview()[0], self.textbox.yview()[1])
        if event.delta > 0:
            self.textbox.yview_scroll(-1, "units")
        else:
            self.textbox.yview_scroll(1, "units")
        self._update_line_numbers()
        return "break" # Prevents the event from propagating further

    def _on_text_modified(self, event=None):
        self.after(10, self._update_line_numbers)
        self.textbox.edit_modified(False)

    def _update_line_numbers(self):
        self.line_numbers.delete("all")

        try:
            # Get the total number of lines in the text
            total_lines = int(self.textbox.index('end-1c').split('.')[0])
            if total_lines < 1: return
            
            # Get the first visible line
            first_visible = self.textbox.index('@0,0')
            first_line_num = int(first_visible.split('.')[0])
            
            # Get the last visible line
            last_visible = self.textbox.index(f'@0,{self.textbox.winfo_height()}')
            last_line_num = int(last_visible.split('.')[0])
            
            # Create a font object for line numbers
            line_font = self.textbox.cget('font')
            
            # Draw line numbers for all visible lines
            for line_num in range(first_line_num, min(last_line_num + 2, total_lines + 1)):
                # Get the y-coordinate of the line
                dline = self.textbox.dlineinfo(f"{line_num}.0")
                if not dline: continue
                
                # Draw the line number
                self.line_numbers.create_text(
                    30, dline[1], 
                    anchor='e', 
                    text=str(line_num), 
                    fill='#6A6A6A', 
                    font=line_font
                )
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

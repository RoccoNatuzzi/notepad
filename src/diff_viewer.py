import customtkinter as ctk
import tkinter as tk

class DiffViewer(ctk.CTkFrame):
    def __init__(self, master, merge_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.merge_callback = merge_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame1 = ctk.CTkScrollableFrame(self, label_text="File 1")
        self.frame1.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

        self.frame2 = ctk.CTkScrollableFrame(self, label_text="File 2")
        self.frame2.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)

        self.font = ctk.CTkFont(family="Courier", size=12)
        self.deletion_color = "#FADBD8"
        self.addition_color = "#D4EFDF"
        self.empty_color = "#F2F3F4"

    def display_diff(self, text1, text2, opcodes):
        self.text1 = text1
        self.text2 = text2
        self.opcodes = opcodes

        for widget in self.frame1.winfo_children():
            widget.destroy()
        for widget in self.frame2.winfo_children():
            widget.destroy()

        for op_idx, (tag, i1, i2, j1, j2) in enumerate(opcodes):
            if tag == 'equal':
                self._add_text_segment(self.frame1, text1[i1:i2], None)
                self._add_text_segment(self.frame2, text2[j1:j2], None)
            elif tag == 'delete':
                self._add_interactive_segment(self.frame1, text1[i1:i2], self.deletion_color, 'to_right', op_idx)
                self._add_placeholder(self.frame2)
            elif tag == 'insert':
                self._add_placeholder(self.frame1)
                self._add_interactive_segment(self.frame2, text2[j1:j2], self.addition_color, 'to_left', op_idx)
            elif tag == 'replace':
                self._add_interactive_segment(self.frame1, text1[i1:i2], self.deletion_color, 'to_right', op_idx)
                self._add_interactive_segment(self.frame2, text2[j1:j2], self.addition_color, 'to_left', op_idx)

    def _add_text_segment(self, parent, text, color):
        # Using a textbox to allow text selection
        text_widget = ctk.CTkTextbox(parent, font=self.font, fg_color=color if color else "transparent", wrap="word", activate_scrollbars=False)
        text_widget.insert("1.0", text)
        text_widget.configure(state="disabled", height=self._estimate_widget_height(text))
        text_widget.pack(fill="x", expand=True)
        return text_widget

    def _estimate_widget_height(self, text):
        # Simple estimation, might need refinement
        lines = text.count('\n') + 1
        return lines * 20

    def _add_interactive_segment(self, parent, text, color, direction, op_idx):
        frame = ctk.CTkFrame(parent, fg_color=color)
        frame.pack(fill="x", expand=True)

        text_widget = ctk.CTkTextbox(frame, font=self.font, fg_color="transparent", wrap="word", activate_scrollbars=False)
        text_widget.insert("1.0", text)
        text_widget.configure(state="disabled", height=self._estimate_widget_height(text))
        text_widget.pack(side="left", fill="x", expand=True)

        arrow = "→" if direction == 'to_right' else "←"
        button = ctk.CTkButton(frame, text=arrow, width=30,
                               command=lambda d=direction, i=op_idx: self._on_merge(d, i))
        button.pack(side="right", padx=5, pady=5)

    def _add_placeholder(self, parent):
        ctk.CTkLabel(parent, text="", fg_color=self.empty_color, anchor="w", font=self.font).pack(fill="x", expand=True, ipady=5)

    def _on_merge(self, direction, op_idx):
        if self.merge_callback:
            self.merge_callback(direction, op_idx)

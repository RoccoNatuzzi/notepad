import customtkinter as ctk
import tkinter as tk

class DiffViewer(ctk.CTkFrame):
    def __init__(self, master, merge_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self.merge_callback = merge_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0) # Column for merge buttons
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.font = ctk.CTkFont(family="Courier", size=12)

        self.text_widget1 = ctk.CTkTextbox(self, font=self.font, wrap="none", state="disabled")
        self.text_widget1.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

        self.merge_button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.merge_button_frame.grid(row=0, column=1, sticky="ns")

        self.text_widget2 = ctk.CTkTextbox(self, font=self.font, wrap="none", state="disabled")
        self.text_widget2.grid(row=0, column=2, sticky="nsew", padx=(2, 5), pady=5)

        # Configure tags for highlighting
        self.text_widget1.tag_config("deletion", background="#FADBD8")
        self.text_widget2.tag_config("addition", background="#D4EFDF")
        self.text_widget1.tag_config("replace_old", background="#FADBD8")
        self.text_widget2.tag_config("replace_new", background="#D4EFDF")

        # Synchronize scrolling
        self.text_widget1.bind("<MouseWheel>", self._on_mouse_wheel)
        self.text_widget2.bind("<MouseWheel>", self._on_mouse_wheel)
        self.text_widget1.bind("<Configure>", self._on_configure)
        self.text_widget2.bind("<Configure>", self._on_configure)

    def _on_mouse_wheel(self, event):
        self.text_widget1.yview_scroll(-1 * (event.delta // 120), "units")
        self.text_widget2.yview_scroll(-1 * (event.delta // 120), "units")
        return "break"

    def _on_configure(self, event):
        # This is a placeholder for potential future scroll synchronization logic
        pass

    def display_diff(self, text1, text2, opcodes):
        self.text_widget1.configure(state="normal")
        self.text_widget2.configure(state="normal")
        self.text_widget1.delete("1.0", "end")
        self.text_widget2.delete("1.0", "end")

        # Clear existing merge buttons
        for widget in self.merge_button_frame.winfo_children():
            widget.destroy()

        # Store original texts for merge operations
        self.original_text1 = text1
        self.original_text2 = text2
        self.opcodes = opcodes

        self.text_widget1.insert("1.0", text1)
        self.text_widget2.insert("1.0", text2)

        # Apply tags for highlighting and add merge buttons
        for op_idx, (tag, i1, i2, j1, j2) in enumerate(opcodes):
            if tag == 'delete':
                self.text_widget1.tag_add("deletion", f"1.0+{i1}c", f"1.0+{i2}c")
                # Add merge button for deletion
                self._add_merge_buttons(self.merge_button_frame, op_idx, f"1.0+{i1}c", f"1.0+{i2}c", 'to_right')
            elif tag == 'insert':
                self.text_widget2.tag_add("addition", f"1.0+{j1}c", f"1.0+{j2}c")
                # Add merge button for insertion
                self._add_merge_buttons(self.merge_button_frame, op_idx, f"1.0+{j1}c", f"1.0+{j2}c", 'to_left')
            elif tag == 'replace':
                self.text_widget1.tag_add("replace_old", f"1.0+{i1}c", f"1.0+{i2}c")
                self.text_widget2.tag_add("replace_new", f"1.0+{j1}c", f"1.0+{j2}c")
                # Add merge buttons for replacement
                self._add_merge_buttons(self.merge_button_frame, op_idx, f"1.0+{i1}c", f"1.0+{i2}c", 'to_right')
                self._add_merge_buttons(self.merge_button_frame, op_idx, f"1.0+{j1}c", f"1.0+{j2}c", 'to_left')

        self.text_widget1.configure(state="disabled")
        self.text_widget2.configure(state="disabled")

    def _on_merge(self, direction, op_idx):
        if self.merge_callback:
            # Get the opcodes for the current diff
            tag, i1, i2, j1, j2 = self.opcodes[op_idx]

            if direction == 'to_right':  # Merge from left to right (File 1 to File 2)
                # Replace the content in text2 with content from text1
                # This is a simplified merge, a real merge would be more complex
                new_text2 = list(self.original_text2)
                new_text2[j1:j2] = list(self.original_text1[i1:i2])
                self.original_text2 = "".join(new_text2)
                self.merge_callback(self.original_text1, self.original_text2)
            elif direction == 'to_left':  # Merge from right to left (File 2 to File 1)
                # Replace the content in text1 with content from text2
                new_text1 = list(self.original_text1)
                new_text1[i1:i2] = list(self.original_text2[j1:j2])
                self.original_text1 = "".join(new_text1)
                self.merge_callback(self.original_text1, self.original_text2)

            # Re-display the diff with the updated texts
            from character_differ import get_character_diffs
            new_opcodes = get_character_diffs(self.original_text1, self.original_text2)
            self.display_diff(self.original_text1, self.original_text2, new_opcodes)

    def _add_merge_buttons(self, parent_frame, op_idx, start_index, end_index, direction):
        # Create a frame for the button to control its placement
        button_container = ctk.CTkFrame(parent_frame, fg_color="transparent")
        button_container.pack(fill="x", pady=1) # Use pack for vertical stacking in the merge_button_frame

        arrow = "→" if direction == 'to_right' else "←"
        button = ctk.CTkButton(button_container, text=arrow, width=30, font=self.font,
                               command=lambda d=direction, i=op_idx: self._on_merge(d, i))
        button.pack(side="top", padx=5, pady=5)

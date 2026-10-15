import customtkinter as ctk

class LabeledRadioRow(ctk.CTkFrame):
    def __init__(self, master, label_text="Group", option1_text="Yes", option2_text="No", command=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self._command = command
        
        # Instance-specific variable so multiple copies don't interfere with each other
        self.var = ctk.StringVar(value=option1_text)
        
        # Main label
        self.main_label = ctk.CTkLabel(self, text=label_text)
        self.main_label.pack(side="left", padx=(10, 15))
        
        # Radio Button 1
        self.radio1 = ctk.CTkRadioButton(
            self, 
            text=option1_text, 
            variable=self.var, 
            value=option1_text,
            command=self._on_change
        )
        self.radio1.pack(side="left", padx=10)
        
        # Radio Button 2
        self.radio2 = ctk.CTkRadioButton(
            self, 
            text=option2_text, 
            variable=self.var, 
            value=option2_text,
            command=self._on_change
        )
        self.radio2.pack(side="left", padx=10)

    def _on_change(self):
        if self._command:
            self._command(self.var.get())

    def get_value(self):
        """Returns the text of the currently selected radio button."""
        return self.var.get()

    def set_value(self, value):
        """Programmatically select a radio button by its text value."""
        self.var.set(value)
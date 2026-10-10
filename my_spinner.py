#my_spinner.py
#customtkinter custom spinner
# contains a label, text input, and up/down buttons
# version 1, you give a list that it can chose from
import customtkinter as ctk

class MySpinner:
    def __init__(self, ctx_instance, spin_list, start_value, large_font, 
                 lbl_text, command=None, padx=20, minsize=20):
        self.ctx = ctx_instance
        if start_value not in spin_list:
            print(f'ERROR: {start_value} not in list')
            raise ValueError
        self.spin_list = spin_list
        self.cur_index = self.spin_list.index(start_value)
        self.large_font = large_font
        self.lbl_text = lbl_text
        self.command = command
        self.padx = padx
        self.minsize = minsize

    def draw(self):
        # container frame
        row_frame = ctk.CTkFrame(self.ctx, fg_color="transparent")
        row_frame.pack(pady=5, padx=self.padx, fill="x")
        
        # Configure the grid columns inside the frame
        row_frame.grid_columnconfigure(0, weight=0, minsize=self.minsize) 
        row_frame.grid_columnconfigure(1, weight=1) 
        row_frame.grid_columnconfigure(2, weight=0)
        row_frame.grid_columnconfigure(3, weight=1)
        
        label = ctk.CTkLabel(row_frame, text=self.lbl_text, font=self.large_font)
        label.grid(row=0, column=0, pady=5, padx=(0, 10), sticky="e")
        
        self.entry = ctk.CTkEntry(row_frame, width=100, font=self.large_font)
        self.entry.grid(row=0, column=1, sticky="w") #
        self._set_value(self.spin_list[self.cur_index])                         
        
        down_button = ctk.CTkButton(row_frame, text="▼", font=self.large_font, width=45, 
                height=45, command=self.decrease)
        down_button.grid(row=0, column=2, padx=(10, 5), sticky="w")
        up_button = ctk.CTkButton(row_frame, text="▲", font=self.large_font, width=45, 
                height=45, command=self.increase)
        up_button.grid(row=0, column=3, sticky="w")

    def _set_value(self, val: str):
        self.entry.delete(0, "end")
        self.entry.insert(0, val)

    def increase(self):
        selected_value = self.entry.get()
        index = self.spin_list.index(selected_value)
        if index < len(self.spin_list) -1:
            self.cur_index += 1
            self._set_value(self.spin_list[self.cur_index])
            if self.command:
                self.command(self.spin_list[self.cur_index])

    def decrease(self):
        selected_value = self.entry.get()
        index = self.spin_list.index(selected_value)
        if index > 0:
            self.cur_index -= 1
            self._set_value(self.spin_list[self.cur_index])
            if self.command:
                self.command(self.spin_list[self.cur_index])

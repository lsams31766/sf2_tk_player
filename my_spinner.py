#my_spinner.py
#customtkinter custom spinner
# contains a label, text input, and up/down buttons
# version 1, you give a list that it can chose from
import customtkinter as ctk
import bisect
import time
from repeat_button import RepeatButton


class MySpinner:
    def __init__(self, ctx_instance, spin_list, start_value, large_font, 
                 lbl_text, command=None, padx=20, minsize=20, entry_width=100):
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
        self.entry_width = entry_width
        
        # Debounce tracking to prevent double-firing on quick taps
        self.last_change_time = 0
        self.min_interval = 0.08  # 80ms minimum gap between steps

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
        
        self.entry = ctk.CTkEntry(row_frame, width=self.entry_width, font=self.large_font)
        self.entry.grid(row=0, column=1, sticky="w") 
        self._set_value(self.spin_list[self.cur_index])                             
        
        ctx = self.ctx.winfo_toplevel()
        down_button = RepeatButton(
            row_frame, touch=ctx.touch, text="▼", width=45, height=45,
            font=self.large_font, command=lambda: self.on_press(-1))
        down_button.grid(row=0, column=2, padx=(10, 5), sticky="w")
        
        up_button = RepeatButton(
            row_frame, touch=ctx.touch, text="▲", width=45, height=45,
            font=self.large_font, command=lambda: self.on_press(+1))
        up_button.grid(row=0, column=3, sticky="w")

    def _set_value(self, val: str):
        self.entry.delete(0, "end")
        self.entry.insert(0, val)

    def increase(self):
        now = time.time()
        # Ignore calls that happen too close together (filters out quick-tap double triggers)
        if now - self.last_change_time < self.min_interval:
            return
        self.last_change_time = now

        selected_value = self.entry.get()
        index = self.spin_list.index(selected_value)
        if index < len(self.spin_list) - 1:
            self.cur_index += 1
            self._set_value(self.spin_list[self.cur_index])
            if self.command:
                self.command(self.spin_list[self.cur_index])

    def decrease(self):
        now = time.time()
        # Ignore calls that happen too close together
        if now - self.last_change_time < self.min_interval:
            return
        self.last_change_time = now

        selected_value = self.entry.get()
        index = self.spin_list.index(selected_value)
        if index > 0:
            self.cur_index -= 1
            self._set_value(self.spin_list[self.cur_index])
            if self.command:
                self.command(self.spin_list[self.cur_index])

    def on_press(self, delta):
        if delta == 1:
            self.increase()
        else:
            self.decrease()

    @staticmethod
    def check_number_type(value_str):
        try:
            val = int(value_str)
            if str(val) == value_str:
                return "Integer"
        except ValueError:
            pass  

        try:
            val = float(value_str)
            return "Float"
        except ValueError:
            pass  

        return "String"

    @staticmethod
    def insert_unique_sorted(sorted_list, val):
        idx = bisect.bisect_left(sorted_list, val)
        if idx < len(sorted_list) and sorted_list[idx] == val:
            return False         
        sorted_list.insert(idx, val)
        return True

    @staticmethod
    def make_spinner_list(controls, default):
        cur_val = controls["min"]
        l = [cur_val]
        sInc = controls["inc"]
        if MySpinner.check_number_type(sInc) == "Integer":
            while cur_val <= controls["max"]:
                cur_val += controls["inc"]
                l.append(cur_val)
        else: # float
            while cur_val <= controls["max"]:
                cur_val += controls["inc"]
                l.append(round(cur_val, 2))
        MySpinner.insert_unique_sorted(l, default)
        l = [str(n) for n in l]
        return l
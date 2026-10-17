# sf2_combi_edit.py

import customtkinter as ctk
from my_spinner import MySpinner
from sf2_player_fs import fs_get_program_list, layer_sounds, split_keyboard,\
    fs_turn_off_layering, turn_off_split_keyboard

saved_prog1 = 0 # will be set after selection
saved_prog1_name = "?"
saved_prog2 = 1 # will be set after selection
saved_prog2_name = "?"

class CombiEdit:
    def __init__(self, ctx_instance):
        self.ctx = ctx_instance
        # Store mode_var in __init__ so selection persists across redraws
        self.mode_var = ctk.StringVar(value="Layer")
        self.split_point_var = "60"  # Default split point (e.g., Middle C)
        self.program_list = fs_get_program_list()

    def _on_split_change(self, val):
        self.split_point_var = val
        prog1 = saved_prog1_name if 'saved_prog1_name' in globals() else "Piano 1"
        prog2 = saved_prog2_name if 'saved_prog2_name' in globals() else "Honkey Tonk"
        
        layer_sounds(1, 0, saved_prog1, 2, 0, saved_prog2)
        split_keyboard(int(self.split_point_var))

    def draw(self):
        self.ctx.clear_window()
        
        # 1. Menu Button (Pack FIRST with side="bottom" to anchor it at the bottom)
        self.menu_btn = ctk.CTkButton(
            self.ctx, text="Menu", width=180, command=self.ctx.menu_screen
        )
        self.menu_btn.pack(side="bottom", pady=8)

        # 2. Title
        self.title_label = ctk.CTkLabel(
            self.ctx, text="COMBI Edit", font=self.ctx.font
        )
        self.title_label.pack(side="top", pady=(8, 4))

        large_font = ("Helvetica", 24)

        # Helper variables for saved programs
        prog1 = saved_prog1_name if 'saved_prog1_name' in globals() else "Piano 1"
        prog2 = saved_prog2_name if 'saved_prog2_name' in globals() else "Honkey Tonk"

        # 3. Mode Frame (Layer / Split / None)
        self.mode_frame = ctk.CTkFrame(self.ctx, fg_color="transparent")
        self.mode_frame.pack(anchor="w", pady=(15, 10), padx=10)        
        
        self.mode_label = ctk.CTkLabel(
            self.mode_frame, text="Mode:", font=large_font
        )
        self.mode_label.pack(side="left", padx=(20, 15))    

        def select_mode(m):
            self.mode_var.set(m)
            
            # Trigger backend functions based on selected mode
            if m == "None":
                fs_turn_off_layering()
            elif m == "Layer":
                layer_sounds(1, 0, saved_prog1, 2, 0, saved_prog2)
                turn_off_split_keyboard()
            elif m == "Split":
                layer_sounds(1, 0, saved_prog1, 2, 0, saved_prog2)
                split_keyboard(int(self.split_point_var))
                
            self.draw()

        current_mode = self.mode_var.get()

        for mode_name in ["Layer", "Split", "None"]:
            is_selected = (current_mode == mode_name)
            btn = ctk.CTkButton(
                self.mode_frame,
                text=mode_name,
                font=large_font,
                width=100,
                height=40,
                corner_radius=20,
                fg_color="#1f6aa5" if is_selected else "transparent",
                border_width=2,
                border_color="#1f6aa5",
                text_color="white" if is_selected else ("black", "white"),
                command=lambda m=mode_name: select_mode(m)
            )
            btn.pack(side="left", padx=5)

        # 4. Conditional Split Spinner Row (Drawn only if "Split" is selected)
        if self.mode_var.get() == "Split":
            split_list = [str(i) for i in range(21, 109)]
            if self.split_point_var not in split_list:
                self.split_point_var = "60"
            
            self.split_frame = ctk.CTkFrame(self.ctx, fg_color="transparent")
            self.split_frame.pack(anchor="w", padx=10, pady=(0, 10))        
            
            self.split_spinner = MySpinner(
                ctx_instance=self.split_frame,
                spin_list=split_list,
                start_value=self.split_point_var,
                large_font=large_font,
                lbl_text="Split Pt:",
                command=self._on_split_change,
                padx=20,
                minsize=90
            )
            self.split_spinner.draw()

        # 5. Prog1 Selection Frame
        self.prog1_frame = ctk.CTkFrame(self.ctx, fg_color="transparent")
        self.prog1_frame.pack(anchor="w", pady=(10, 10), padx=10)
        self.prog1_label = ctk.CTkLabel(
            self.prog1_frame, text="Prog1:", font=large_font
        )
        self.prog1_label.pack(side="left", padx=(20, 15))
        
        self.prog1_entry = ctk.CTkEntry(self.prog1_frame, width=220, font=large_font)
        self.prog1_entry.insert(0, self.program_list[saved_prog1])
        self.prog1_entry.pack(side="left")
        
        self.prog1_button = ctk.CTkButton(
            self.prog1_frame, text="Change", command=self.change_prog1, width=90
        )
        self.prog1_button.pack(side="left", padx=15)

        # 6. Prog2 Selection Frame
        self.prog2_frame = ctk.CTkFrame(self.ctx, fg_color="transparent")
        self.prog2_frame.pack(anchor="w", pady=(0, 10), padx=10)
        self.prog2_label = ctk.CTkLabel(
            self.prog2_frame, text="Prog2:", font=large_font
        )
        self.prog2_label.pack(side="left", padx=(20, 15))
        
        self.prog2_entry = ctk.CTkEntry(self.prog2_frame, width=220, font=large_font)
        self.prog2_entry.insert(0, self.program_list[saved_prog2])
        self.prog2_entry.pack(side="left")
        
        self.prog2_button = ctk.CTkButton(
            self.prog2_frame, text="Change", command=self.change_prog2, width=90
        )
        self.prog2_button.pack(side="left", padx=15)


    def change_prog1(self):
        if self.mode_var.get() == "Split":
            split = int(self.split_point_var)
        else:
            split = -1
        p = ProgSelect(self.ctx, True, split)
        p.draw()

    def change_prog2(self):
        if self.mode_var.get() == "Split":
            split = int(self.split_point_var)
        else:
            split = -1
        p = ProgSelect(self.ctx, False, split)
        p.draw()

class ProgSelect:
    def __init__(self, ctx_instance, prog1=True, split=-1):
        self.ctx = ctx_instance
        self.prog1 = prog1 # true if prog1, false if prog2
        self.font = ctk.CTkFont(family="Helvetica", size=24, weight="bold")
        self.font_small = ctk.CTkFont(family="Helvetica", size=14, weight="bold")
        self.program_list = fs_get_program_list()
        self.current_program_index = 0
        self.split = split
 
    def draw(self):
        self.ctx.clear_window()

        # 1. Title at the top
        if self.prog1 == True:
           txt_title = "Program 1 Select"
        else:
           txt_title = "Program 2 Select"
        title_label = ctk.CTkLabel(self.ctx, text=txt_title, font=self.font)
        title_label.pack(side="top", pady=(8, 4))

        # 4. Save button at the bottom of the screen
        btn_save = ctk.CTkButton(
            self.ctx,
            text="Save & Return",
            command=self.save_program_selection,
            width=180,
        )
        btn_save.pack(side="bottom", pady=8)

        # Middle container frame
        middle_frame = ctk.CTkFrame(self.ctx, fg_color="transparent")
        middle_frame.pack(expand=True, pady=2)

        # Horizontally centered label: "Select a Program:"
        label_select = ctk.CTkLabel(
            middle_frame, text="Select a Program:", font=self.font_small
        )
        label_select.pack(anchor="center", pady=(0, 4))

        # Row frame to hold the 340px scrollable list and the up/down buttons side-by-side
        row_frame = ctk.CTkFrame(middle_frame, fg_color="transparent")
        row_frame.pack()

        # Scrollable selection box (340px width, 200px height)
        self.list_frame = ctk.CTkScrollableFrame(
            row_frame, width=340, height=200, fg_color="transparent"
        )
        self.list_frame.pack(side="left", padx=(0, 6))

        # Vertical container for Arrow Up and Arrow Down buttons
        btn_col_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
        btn_col_frame.pack(side="left", fill="y")

        btn_up = ctk.CTkButton(
            btn_col_frame,
            text="▲",
            font=self.font_small,
            width=40,
            height=95,
            command=lambda: self.scroll_list(-3),
        )
        btn_up.pack(side="top", pady=(0, 5))

        btn_down = ctk.CTkButton(
            btn_col_frame,
            text="▼",
            font=self.font_small,
            width=40,
            height=95,
            command=lambda: self.scroll_list(3),
        )
        btn_down.pack(side="top")

        initial_program = self.program_list[self.current_program_index]
        self.selected_program_var = ctk.StringVar(value=initial_program)

        self.program_buttons = []
        for prog in self.program_list:
            is_selected = prog == initial_program
            btn_color = "green" if is_selected else "blue"
            hover_color = "darkgreen" if is_selected else "darkblue"

            btn = ctk.CTkButton(
                self.list_frame,
                text=prog,
                font=self.font_small,
                fg_color=btn_color,
                hover_color=hover_color,
                height=32,
                command=lambda p=prog: self.select_program(p),
            )
            btn.pack(fill="x", pady=2)
            self.program_buttons.append((prog, btn))

        self.ctx.update_idletasks()

        # Automatically scroll the list so self.current_program_index is at the top
        try:
            total_items = len(self.program_list)
            if total_items > 0:
                # Calculate approximate position ratio (each button is ~32px + 4px vertical padding = 36px)
                item_height = 36
                total_height = total_items * item_height
                target_y = self.current_program_index * item_height
                scroll_fraction = min(max(target_y / total_height, 0.0), 1.0)
                self.list_frame._parent_canvas.yview_moveto(scroll_fraction)
        except Exception as e:
            print(f"Could not auto-scroll list: {e}")

    def save_program_selection(self):
        global saved_prog1, saved_prog2, saved_prog1_name, saved_prog2_name
        # Get the value from our StringVar
        selected = self.selected_program_var.get()

        if selected in self.program_list:
            self.current_program_index = self.program_list.index(selected)
            print(f"Saved Program Index: {self.current_program_index} ({selected})")
            # TODO set the combi layer/split
            if self.prog1 == True:
                saved_prog1 = self.current_program_index
                saved_prog1_name = selected
            else:
                saved_prog2 = self.current_program_index
                saved_prog2_name = selected
            layer_sounds(1, 0, saved_prog1, 2, 0, saved_prog2)
            if self.split > 0:
                split_keyboard(self.split)
            c = CombiEdit(self.ctx)
            c.draw()

    def select_program(self, program_name):
        self.selected_program_var.set(program_name)
        if program_name in self.program_list:
            self.current_program_index = self.program_list.index(program_name)

            # Update button colors: selected = green, others = blue
            for prog, btn in self.program_buttons:
                if prog == program_name:
                    btn.configure(fg_color="green", hover_color="darkgreen")
                else:
                    btn.configure(fg_color="blue", hover_color="darkblue")

    def scroll_list(self, direction):
        """Scrolls the list up or down when arrow buttons are pressed."""
        try:
            self.list_frame._parent_canvas.yview_scroll(direction, "units")
        except Exception:
            pass
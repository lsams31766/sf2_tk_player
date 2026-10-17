# sf2_single_edit.py

import customtkinter as ctk
from my_spinner import MySpinner
from sf2_player_fs import fs_get_program_list, list_instruments_in_bank, \
    set_preset

class SingleEdit:
    def __init__(self, ctx_instance):
        self.ctx = ctx_instance
        self.font = getattr(ctx_instance, "font", ctk.CTkFont(family="Helvetica", size=24, weight="bold"))
        self.font_small = getattr(ctx_instance, "font_small", ctk.CTkFont(family="Helvetica", size=18, weight="bold"))
        self.current_program_index = 0

    def draw(self):
        print("SINGLE Mode selected!")
        self.ctx.clear_window()

        title_label = ctk.CTkLabel(self.ctx, text="SINGLE Mode", font=self.font)
        title_label.pack(side="top", pady=20)
        
        btn_home = ctk.CTkButton(
            self.ctx, text="MENU", command=self.ctx.menu_screen, width=200
        )
        btn_home.pack(side="bottom", pady=20)

        container_frame = ctk.CTkFrame(self.ctx, fg_color="transparent")
        container_frame.pack(expand=True, padx=20, pady=10)
        
        center_frame = ctk.CTkFrame(container_frame, fg_color="transparent",
            border_width=2, border_color="black")
        center_frame.pack(pady=(0, 15), padx=10)
        
        label1 = ctk.CTkLabel(center_frame, text="BANK: 0", font=self.font)
        label1.pack(pady=4, padx=30)

        # Fetch the currently saved index and corresponding program name
        list_instruments_in_bank()
        self.program_list = fs_get_program_list()
        prog_index = getattr(self, "current_program_index", 0)
        prog_name = self.program_list[prog_index] if self.program_list else "Default"

        # Dynamically update labels based on saved selection
        label2 = ctk.CTkLabel(center_frame, text=f"Program {prog_index}", font=self.font)
        label2.pack(pady=4, padx=30)
        
        label3 = ctk.CTkLabel(center_frame, text=prog_name, font=self.font)
        label3.pack(pady=4, padx=30)

        self.btn_single_select = ctk.CTkButton(container_frame, text="Change Program",
            command=self.single_select, width=200)
        self.btn_single_select.pack()

    def single_select(self):
        print("SINGLE Select selected!")
        self.ctx.clear_window()

        # 1. Title at the top
        title_label = ctk.CTkLabel(self.ctx, text="SINGLE Select", font=self.font)
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
        
        list_instruments_in_bank()
        self.program_list = fs_get_program_list()
        initial_program = self.program_list[self.current_program_index] if self.program_list else ""
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
                item_height = 36
                total_height = total_items * item_height
                target_y = self.current_program_index * item_height
                scroll_fraction = min(max(target_y / total_height, 0.0), 1.0)
                self.list_frame._parent_canvas.yview_moveto(scroll_fraction)
        except Exception as e:
            print(f"Could not auto-scroll list: {e}")

    def save_program_selection(self):
        selected = self.selected_program_var.get()

        if selected in self.program_list:
            self.current_program_index = self.program_list.index(selected)
            print(f"Saved Program Index: {self.current_program_index} ({selected})")

        set_preset(self.current_program_index)
        # Return to single mode
        self.draw()

    def select_program(self, program_name):
        self.selected_program_var.set(program_name)
        if program_name in self.program_list:
            self.current_program_index = self.program_list.index(program_name)

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
        
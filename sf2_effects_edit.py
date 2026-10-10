#sf2_effects_edit.py
#screens to enable/disable effects and edit them
import customtkinter as ctk
from sf2_player_controls import load_default_reverb_settings
from sf2_player_controls import load_default_chorus_settings
from my_spinner import MySpinner

class EffectsEnable:
    def __init__(self, ctx_instance):
        self.ctx = ctx_instance

        # Persistent state variables
        self.reverb_state = "off"
        self.chorus_state = "off"

    def draw(self):
        print('ENABLE effects screen')
        self.ctx.clear_window()
        
        large_font = ("Helvetica", 16)
        # Title at the top
        title_label = ctk.CTkLabel(self.ctx, text="EFFECTS Enable", font=self.ctx.font)
        title_label.pack(side="top", pady=(8, 4))

        # Save button at the bottom
        btn_save = ctk.CTkButton(
            self.ctx, text="MENU", command=self.ctx.menu_screen, width=180
        )
        btn_save.pack(side="bottom", pady=8)
        
        # Row 1: Reverb enable:
        reverb_container = ctk.CTkFrame(self.ctx, fg_color="transparent")
        reverb_container.pack(pady=20)

        reverb_label = ctk.CTkLabel(
            reverb_container, text="Enable Reverb:", font=("Helvetica", 16)
        )
        reverb_label.pack(side="left", padx=(0, 15))  # padx adds spacing between label and switch

        self.reverb_switch_var = ctk.StringVar(value=self.reverb_state)
        reverb_toggle_switch = ctk.CTkSwitch(
            reverb_container,
            text="",  
            switch_width=60,
            switch_height=30,
            command=self.reverb_switch_event,
            variable=self.reverb_switch_var,
            onvalue="on",
            offvalue="off",
        )
        reverb_toggle_switch.pack(side="left")
        btn_edit_reverb = ctk.CTkButton(
            reverb_container, text="EDIT", command=self.edit_reverb, width=100
        )
        btn_edit_reverb.pack(side="right")

        # Row 2: Chorus enable:
        self.chorus_switch_var = ctk.StringVar(value=self.chorus_state)
        chorus_container = ctk.CTkFrame(self.ctx, fg_color="transparent")
        chorus_container.pack(pady=10)
        chorus_label = ctk.CTkLabel(
            chorus_container, text="Enable Chorus:", font=("Helvetica", 16)
        )
        chorus_label.pack(side="left", padx=(0, 15))
        chorus_toggle_switch = ctk.CTkSwitch(
            chorus_container,
            text="",
            switch_width=60,
            switch_height=30,
            command=self.chorus_switch_event,
            variable=self.chorus_switch_var,
            onvalue="on",
            offvalue="off",
        )
        chorus_toggle_switch.pack(side="left")        
        btn_edit_reverb = ctk.CTkButton(
            chorus_container, text="EDIT", command=self.edit_chorus, width=100
        )
        btn_edit_reverb.pack(side="right")
        self.ctx.update_idletasks()

    def reverb_switch_event(self):
        self.reverb_state = self.reverb_switch_var.get()
        print("Reverb Switch state:", self.reverb_state)

    def chorus_switch_event(self):
        self.chorus_state = self.chorus_switch_var.get()
        print("Chorus Switch state:", self.chorus_state)

    def edit_reverb(self):
        if self.reverb_state == 'off':
            return
        edit_screen = EffectsEdit(self.ctx,'Reverb')
        edit_screen.draw()

    def edit_chorus(self):
        if self.chorus_state == 'off':
            return
        edit_screen = EffectsEdit(self.ctx,'Chorus')
        edit_screen.draw()

class EffectsEdit:
    def __init__(self, ctx_instance, effects_type):
        self.ctx = ctx_instance

        # Persistent state variables
        self.effect_type = effects_type
        self.page = 0
        self.items_per_page = 4
        if self.effect_type == 'Reverb':
            self.settings = load_default_reverb_settings()
        else:
            self.settings = load_default_chorus_settings()


    def draw(self):
        # TODO fix the effects_settings_list
        # TODO fix the default value
        # TODO handle each control change
        print('EDIT effects screen')
        self.ctx.clear_window()
        
        large_font = ("Helvetica", 16)
        # Title at the top
        t = self.effect_type + ' Settings'
        title_label = ctk.CTkLabel(self.ctx, text=t, font=self.ctx.font)
        title_label.pack(side="top", pady=(8, 4))

        # Save button at the bottom
        btn_save = ctk.CTkButton(
            self.ctx, text="MENU", command=self.ctx.menu_screen, width=180
        )
        btn_save.pack(side="bottom", pady=8)

        i = 0
        spinners = []
        effect_settings_list = [str(n) for n in range(0, 101, 10)]
        self.nbr_effect_settings = len(effect_settings_list)
        # Outer frame contains the settings spinners and up/down buttons
        outer_frame = ctk.CTkFrame(self.ctx, fg_color="transparent")
        outer_frame.pack(expand=True, pady=2)
        # Middle container frame
        middle_frame = ctk.CTkFrame(outer_frame,  
            width=300,
            height=400,
            border_width=3,        
            border_color="black", 
            fg_color="transparent")

        middle_frame.pack(side="left", padx=(0, 10))

        btn_container = ctk.CTkFrame(outer_frame, fg_color="transparent")
        btn_container.pack(side="left", fill="y")
        btn_page_up = ctk.CTkButton(
            btn_container, text="▲", font=large_font, width=50, height=80,
            command=self.page_up_event
        )
        btn_page_up.pack(pady=(0, 10))
        btn_page_down = ctk.CTkButton(
            btn_container, text="▼", font=large_font, width=50, height=80,
            command=self.page_down_event
        )
        btn_page_down.pack(pady=(10, 0))

        # determine what to display
        first_index = self.page * self.items_per_page
        last_index = min(first_index + self.items_per_page, len(self.settings))
        print(f'first_index {first_index} last_index {last_index}')
        i = first_index
        j = 0 # track the viewable spinners
        while True:
            item = self.settings[self.page * self.items_per_page + j]
            lbl_name = item[0]
            lbl_val = item[1]
            temp_spinner = MySpinner(
                    middle_frame, effect_settings_list, "50", large_font, lbl_name,
                    command=self.temp_effect_edit, padx=10
                )
            spinners.append(temp_spinner)
            spinners[j].draw()
            i += 1
            j += 1
            if i >= last_index:
                break

    def temp_effect_edit(self):
        return

    def page_up_event(self):
        print(f'page down self.page {self.page}')
        if self.page > 0:
            self.page -= 1
            self.draw()

    def page_down_event(self):
        max_page = len(self.settings) // self.items_per_page
        print(f'page up max_page {max_page}, self.page {self.page}')
        if self.page < max_page:
            self.page += 1 
            self.draw()




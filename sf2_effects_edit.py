#sf2_effects_edit.py
#screens to enable/disable effects and edit them
import customtkinter as ctk
from sf2_player_controls import load_default_reverb_settings, load_default_chorus_settings, reverb_controls, chorus_controls
from sf2_player_effects import set_effect_configuration, set_effect_parameter
from my_spinner import MySpinner

class EffectsEnable:
    def __init__(self, ctx_instance):
        self.ctx = ctx_instance

        # Persistent state variables
        self.reverb_state = "off"
        self.chorus_state = "off"

        # --- FIX 1: Store the settings persistently here so they survive screen changes ---
        self.reverb_settings = load_default_reverb_settings()
        self.chorus_settings = load_default_chorus_settings()

    def draw(self):
        print('ENABLE effects screen')
        self.ctx.clear_window()
        
        large_font = ("Helvetica", 16)
        title_label = ctk.CTkLabel(self.ctx, text="EFFECTS Enable", font=self.ctx.font)
        title_label.pack(side="top", pady=(8, 4))

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
        reverb_label.pack(side="left", padx=(0, 15))

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
        btn_edit_chorus = ctk.CTkButton(
            chorus_container, text="EDIT", command=self.edit_chorus, width=100
        )
        btn_edit_chorus.pack(side="right")
        self.ctx.update_idletasks()

    def reverb_switch_event(self):
        self.reverb_state = self.reverb_switch_var.get()
        print("Reverb Switch state:", self.reverb_state)
        self.update_effects_state()

    def chorus_switch_event(self):
        self.chorus_state = self.chorus_switch_var.get()
        print("Chorus Switch state:", self.chorus_state)
        self.update_effects_state()

    def edit_reverb(self):
        if self.reverb_state == 'off':
            return
        edit_screen = EffectsEdit(self.ctx, 'Reverb', self.reverb_settings)
        edit_screen.draw()

    def edit_chorus(self):
        if self.chorus_state == 'off':
            return
        edit_screen = EffectsEdit(self.ctx, 'Chorus', self.chorus_settings)
        edit_screen.draw()

    def update_effects_state(self):
        if self.reverb_state == 'off' and self.chorus_state == 'off':
            set_effect_configuration('none')
        if self.reverb_state == 'on' and self.chorus_state == 'off':
            set_effect_configuration('reverb')
        if self.reverb_state == 'off' and self.chorus_state == 'on':
            set_effect_configuration('chorus')
        if self.reverb_state == 'on' and self.chorus_state == 'on':
            set_effect_configuration('chorus_reverb')


class EffectsEdit:
    def __init__(self, ctx_instance, effects_type, settings_list):
        self.ctx = ctx_instance
        self.effect_type = effects_type
        self.settings = settings_list  
        
        self.page = 0
        self.items_per_page = 4
        self.reverb_controls = reverb_controls 
        self.chorus_controls = chorus_controls 

    def draw(self):
        print('EDIT effects screen')
        self.ctx.clear_window()        
        large_font = ("Helvetica", 16)
        title_label = ctk.CTkLabel(self.ctx, text=f"{self.effect_type} Settings", font=self.ctx.font)
        title_label.pack(side="top", pady=(8, 4))

        btn_save = ctk.CTkButton(
            self.ctx, text="MENU", command=self.ctx.menu_screen, width=180
        )
        btn_save.pack(side="bottom", pady=8)

        if self.effect_type == 'Reverb':
            controls = self.reverb_controls
        else:
            controls = self.chorus_controls

        outer_frame = ctk.CTkFrame(self.ctx, fg_color="transparent")
        outer_frame.pack(expand=True, pady=2)
        
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

        first_index = self.page * self.items_per_page
        last_index = min(first_index + self.items_per_page, len(self.settings))
        
        spinners = []
        j = 0 
        while True:
            index = self.page * self.items_per_page + j
            if index >= len(self.settings):
                break
                
            cur_controls = controls[index]
            lbl_name = cur_controls["name"]
            default = cur_controls["default"]
            effect_settings_list = MySpinner.make_spinner_list(cur_controls, default)
            
            temp_spinner = MySpinner(
                    middle_frame, effect_settings_list, str(self.settings[index][1]), large_font, lbl_name,
                    command=lambda val, idx=index: self.do_effect_edit(val, idx),
                    padx=10, minsize=100
                )
            spinners.append(temp_spinner)
            spinners[j].draw()
            j += 1
            if j >= self.items_per_page or index + 1 >= len(self.settings):
                break

    def do_effect_edit(self, value, index):
        #print(f"Control at index {index} changed to value: {value}")
        name = self.settings[index][0]
        self.settings[index] = (name, value)
        if self.effect_type == 'Reverb':
            effect_type = 'reverb'
        else:
            effect_type = 'chorus'
        set_effect_parameter(effect_type, name, value)

    def page_up_event(self):
        print(f'page up self.page {self.page}')
        if self.page > 0:
            self.page -= 1
            self.draw()

    def page_down_event(self):
        max_page = (len(self.settings) - 1) // self.items_per_page
        print(f'page down max_page {max_page}, self.page {self.page}')
        if self.page < max_page:
            self.page += 1 
            self.draw()
    
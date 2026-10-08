import platform
import customtkinter as ctk
from sf2_player_fs import init_fluidsynth, fs_get_program_list, set_preset
from sf2_player_effects import start_effects_containers, set_effect_configuration
import sys
# Force all print statements to instantly write out without caching
sys.stdout.reconfigure(line_buffering=True)


# Set global appearance settings
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk): 

  def __init__(self):
    super().__init__()

    self.title("SF2 Player")
    self.resizable(False, False)
    self.font = ctk.CTkFont(family="Helvetica", size=24, weight="bold")
    self.font_small = ctk.CTkFont(family="Helvetica", size=14, weight="bold")

    self.current_program_index = 0

    # --- Platform Detection & Window Setup ---
    current_os = platform.system()
    machine_arch = platform.machine().lower()

    # Check if running on Raspberry Pi (Linux + ARM architecture)
    is_raspberry_pi = current_os == "Linux" and (
        "arm" in machine_arch or "aarch" in machine_arch
    )

    if is_raspberry_pi:
      print("Running on Raspberry Pi: Enabling Full Screen")
      self.geometry("480x320+0+0")
      self.resizable(False, False)
      
      # Removes window title bars and borders for a true kiosk/fullscreen look
      self.overrideredirect(True)
      #init_fluidsynth(effect_callback=start_effects_containers)
      init_fluidsynth()
      self.program_list = fs_get_program_list()

    else:
      print("Running on Mac (or non-Pi): Setting fixed window size")
      self.geometry("450x550")
      self.resizable(False, False)


    # Launch Function 1 (Splash Screen) on startup
    self.splash()

  def clear_window(self):
    """Destroys all active widgets currently in the window."""
    for widget in self.winfo_children():
      widget.destroy()

  def splash(self):
    """Draws the splash screen and sets a 3-second timer."""
    self.clear_window()

    # Splash screen layout
    splash_label1 = ctk.CTkLabel(self, text="SF2 PLAYER", font=self.font)
    splash_label1.pack(pady=12, padx=10, expand=True)
    splash_label2 = ctk.CTkLabel(self, text="Version 1.1", font=self.font)
    splash_label2.pack(pady=12, padx=10, expand=True)
    # Wait for 3000 milliseconds (3 seconds) then call function2
    self.after(3000, self.menu_screen)

  def menu_screen(self):
    """Erases the splash screen and draws the main menu with selection buttons."""
    self.clear_window()

    # Main menu header
    title_label = ctk.CTkLabel(self, text="Main Menu", font=self.font)
    title_label.pack(pady=(15, 5))

    # Container frame for the buttons arranged in a grid
    grid_frame = ctk.CTkFrame(self, fg_color="transparent")
    grid_frame.pack(expand=True, pady=10)

    # Row 1: SINGLE Mode & COMBI Mode
    btn_single = ctk.CTkButton(
        grid_frame, text="SINGLE Mode", command=self.action_single_mode, width=160
    )
    btn_single.grid(row=0, column=0, padx=40, pady=10)

    btn_combi = ctk.CTkButton(
        grid_frame, text="COMBI Mode", command=self.action_combi_mode, width=160
    )
    btn_combi.grid(row=0, column=1, padx=40, pady=10)

    # Row 2: GLOBAL Settings & EFFECTS
    btn_global = ctk.CTkButton(
        grid_frame,
        text="GLOBAL Settings",
        command=self.global_edit,
        width=160,
    )
    btn_global.grid(row=1, column=0, padx=40, pady=10)

    btn_effects = ctk.CTkButton(
        grid_frame, text="EFFECTS", command=self.action_combi_mode, width=160
    )
    btn_effects.grid(row=1, column=1, padx=40, pady=10)

    # Row 3: MIDI SONG PLAYER, USER PATCHES
    btn_midi_player = ctk.CTkButton(
        grid_frame,
        text="MIDI SONG PLAYER",
        command=self.action_combi_mode,
        width=160,
    )
    btn_midi_player.grid(row=2, column=0, padx=40, pady=10)
    
    btn_user_patches = ctk.CTkButton(
        grid_frame,
        text="USER PATCHES",
        command=self.action_combi_mode,
        width=160,
    )
    btn_user_patches.grid(row=2, column=1, padx=40, pady=10)

    # Exit button at the very bottom of the screen
    btn_exit = ctk.CTkButton(
        self, text="Exit App", command=self.destroy, width=200, height=40
    )
    btn_exit.pack(side="bottom", pady=20)


  def action_single_mode(self):
    print("SINGLE Mode selected!")
    self.clear_window()

    title_label = ctk.CTkLabel(self, text="SINGLE Mode", font=self.font)
    title_label.pack(side="top", pady=20)
    
    btn_home = ctk.CTkButton(
        self, text="MENU", command=self.menu_screen, width=200
    )
    btn_home.pack(side="bottom", pady=20)

    container_frame = ctk.CTkFrame(self, fg_color="transparent")
    container_frame.pack(expand=True, padx=20, pady=10)
    
    center_frame = ctk.CTkFrame(container_frame, fg_color="transparent",
        border_width=2, border_color="black")
    center_frame.pack(pady=(0, 15), padx=10)
    
    label1 = ctk.CTkLabel(center_frame, text="BANK: 0", font=self.font)
    label1.pack(pady=4, padx=30)

    # Fetch the currently saved index and corresponding program name
    prog_index = getattr(self, "current_program_index", 0)
    prog_name = self.program_list[prog_index]

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
    self.clear_window()

    # 1. Title at the top
    title_label = ctk.CTkLabel(self, text="SINGLE Select", font=self.font)
    title_label.pack(side="top", pady=(8, 4))

    # 4. Save button at the bottom of the screen
    btn_save = ctk.CTkButton(
        self,
        text="Save & Return",
        command=self.save_program_selection,
        width=180,
    )
    btn_save.pack(side="bottom", pady=8)

    # Middle container frame
    middle_frame = ctk.CTkFrame(self, fg_color="transparent")
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

    self.update_idletasks()

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
    # Get the value from our StringVar
    selected = self.selected_program_var.get()

    if selected in self.program_list:
      self.current_program_index = self.program_list.index(selected)
      print(f"Saved Program Index: {self.current_program_index} ({selected})")

    set_preset(self.current_program_index)
    # Return to single mode
    self.action_single_mode()

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

  def action_combi_mode(self):
    print("COMBI Mode selected!")
    # Add your logic for feature two here

  def global_edit(self):
    print("GLOBAL EDIT selected!")
    self.clear_window()

    # Title at the top
    title_label = ctk.CTkLabel(self, text="GLOBAL Edit", font=self.font)
    title_label.pack(side="top", pady=(8, 4))

    # Save button at the bottom of the screen
    btn_save = ctk.CTkButton(self, text="MENU", command=self.menu_screen, width=180)
    btn_save.pack(side="bottom", pady=8)

    large_font = ("Helvetica", 24)
    # Middle container frame
    row_frame = ctk.CTkFrame(self, fg_color="transparent")
    row_frame.pack(pady=20, padx=20, fill="x")
    
    # Configure the grid columns inside the frame
    row_frame.grid_columnconfigure(0, weight=0) 
    row_frame.grid_columnconfigure(1, weight=1) 
    row_frame.grid_columnconfigure(2, weight=0)
    row_frame.grid_columnconfigure(3, weight=1)
    
    # === Volume in row 0 ===
    label = ctk.CTkLabel(row_frame, text="Volume:", font=large_font)
    label.grid(row=0, column=0, pady=20, padx=(50,10), sticky="w") 
    
    self.volume_entry = ctk.CTkEntry(row_frame, width=50, font=large_font)
    self.volume_entry.grid(row=0, column=1, sticky="w") # 1. Grid it first!
    self._set_volume_number(50)                           # 2. Then set its value safely.
    
    down_button = ctk.CTkButton(row_frame, text="▼", font=large_font, width=45, 
            height=45, command=self.decrease_volume)
    down_button.grid(row=0, column=2, padx=(10, 5), sticky="w")
    up_button = ctk.CTkButton(row_frame, text="▲", font=large_font, width=45, 
            height=45, command=self.increase_volume)
    up_button.grid(row=0, column=3, sticky="w")
    
    # === Midi Channel in row 1 ===
    label2 = ctk.CTkLabel(row_frame, text="Midi Channel:", font=large_font)
    label2.grid(row=1, column=0, padx=(50,10), sticky="w") 
    
    self.channel_entry = ctk.CTkEntry(row_frame, width=100, font=large_font)
    self.channel_entry.grid(row=1, column=1, sticky="w") # Grid it first!
    self._set_channel_number("OMNI")
    
    down_button2 = ctk.CTkButton(row_frame, text="▼", font=large_font, width=45, 
            height=45, command=self.decrease_channel)
    down_button2.grid(row=1, column=2, padx=(10, 5), sticky="w")
    up_button2 = ctk.CTkButton(row_frame, text="▲", font=large_font, width=45, 
            height=45, command=self.increase_channel)
    up_button2.grid(row=1, column=3, sticky="w")
    # Transpose in row 2
    label3 = ctk.CTkLabel(row_frame, text="Transpose:", font=large_font)
    label3.grid(row=2, column=0, pady=20, padx=(50,10), sticky="w") 
    self.transpose_entry = ctk.CTkEntry(row_frame, width=100, font=large_font)
    self._set_transpose_number("0")
    self.transpose_entry.grid(row=2, column=1, sticky="w") 
    down_button3 = ctk.CTkButton(row_frame, text="▼", font=large_font, width=45, 
            height=45, command=self.decrease_transpose)
    down_button3.grid(row=2, column=2, padx=(10, 5), sticky="w")
    up_button3 = ctk.CTkButton(row_frame, text="▲", font=large_font, width=45, 
            height=45, command=self.increase_transpose)
    up_button3.grid(row=2, column=3, sticky="w")

    self.update_idletasks()

  def _set_volume_number(self, number: int):
    self.volume_entry.delete(0, "end")
    self.volume_entry.insert(0, str(number))

  def increase_volume(self):
    current = int(self.volume_entry.get())
    if current < 100:
      self._set_volume_number(current + 1)

  def decrease_volume(self):
    current = int(self.volume_entry.get())
    if current > 0:
      self._set_volume_number(current - 1)

  def _set_channel_number(self, val: str):
    self.channel_entry.delete(0, "end")
    self.channel_entry.insert(0, val)

  def increase_channel(self):
    current = self.channel_entry.get()
    if current == "OMNI":
      self._set_channel_number("1")
    else: # from 1 to 16
      n = int(current)
      if n < 16:
        n += 1
        self._set_channel_number(str(n))

  def decrease_channel(self):
    current = self.channel_entry.get()
    if current == "OMNI":
      return
    else: # from 1 to 16
      n = int(current)
      if n == 1: 
        self._set_channel_number("OMNI")
      else:
        n -= 1
        self._set_channel_number(str(n))

  def _set_transpose_number(self, val: str):
    self.transpose_entry.delete(0, "end")
    self.transpose_entry.insert(0, val)

  def increase_transpose(self):
    current = self.transpose_entry.get()
    # either 0 or -1, -2, ... or +1, +2...
    if current == "0":
      self._set_transpose_number("+1")
    elif current == '-1':
       self._set_transpose_number("0")
    else:
      n = int(current)
      n += 1
      if n < 37:
        s = str(n)
        if n > 0:
          s = '+' + s
        self._set_transpose_number(s)

  def decrease_transpose(self):
    current = self.transpose_entry.get()
    # either 0 or -1, -2, ... or +1, +2...
    if current == "0":
      self._set_transpose_number("-1")
    elif current == '+1':
       self._set_transpose_number("0")
    else:
      n = int(current)
      n -= 1
      if n > -37:
        s = str(n)
        if n > 0:
          s = '+' + s
        self._set_transpose_number(s)

if __name__ == "__main__":
  app = App()
  try:
    app.mainloop()
  finally:
    # This block ALWAYS runs, even during crashes or manual process termination
    print("Cleaning up GUI context safely...")
    app.quit()
    app.destroy()


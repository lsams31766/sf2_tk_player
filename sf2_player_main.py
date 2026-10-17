import platform
import customtkinter as ctk
from sf2_player_fs import init_fluidsynth, fs_get_program_list, set_preset, \
  list_instruments_in_bank
from sf2_player_effects import start_effects_containers, set_effect_configuration
import sys
from sf2_single_edit import SingleEdit
from sf2_global_edit import GlobalEdit
from sf2_effects_edit import EffectsEnable
from sf2_combi_edit import CombiEdit
from sf2_song_player import SongPlayer
from touch_input import TouchState

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
    self.touch = TouchState(self)   # one shared touch reader for the app

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
      init_fluidsynth(effect_callback=start_effects_containers)
      #init_fluidsynth()
      self.program_list = fs_get_program_list()

    else:
      print("Running on Mac (or non-Pi): Setting fixed window size")
      self.geometry("450x550")
      self.resizable(False, False)

    self.single_edit_screen = SingleEdit(self)
    self.global_edit_screen = GlobalEdit(self)
    self.effects_enable_screen = EffectsEnable(self)
    self.combi_edit_screen = CombiEdit(self)
    self.song_player = SongPlayer(self)

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
        grid_frame, text="SINGLE Mode", command=self.single_edit_screen.draw, width=160
    )
    btn_single.grid(row=0, column=0, padx=40, pady=10)

    btn_combi = ctk.CTkButton(
        grid_frame, text="COMBI Mode", command=self.combi_edit_screen.draw, width=160
    )
    btn_combi.grid(row=0, column=1, padx=40, pady=10)

    # Row 2: GLOBAL Settings & EFFECTS
    btn_global = ctk.CTkButton(
        grid_frame,
        text="GLOBAL Settings",
        command=self.global_edit_screen.draw,
        width=160,
    )
    btn_global.grid(row=1, column=0, padx=40, pady=10)

    btn_effects = ctk.CTkButton(
        grid_frame, text="EFFECTS", command=self.effects_enable_screen.draw, width=160
    )
    btn_effects.grid(row=1, column=1, padx=40, pady=10)

    # Row 3: MIDI SONG PLAYER, USER PATCHES
    btn_midi_player = ctk.CTkButton(
        grid_frame, text="MIDI SONG PLAYER", command=self.song_player.draw, width=160
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

  def action_combi_mode(self):
    print("COMBI Mode selected!")
    # Add your logic for feature two here

if __name__ == "__main__":
  app = App()
  try:
    app.mainloop()
  finally:
    # This block ALWAYS runs, even during crashes or manual process termination
    print("Cleaning up GUI context safely...")
    app.quit()
    app.destroy()


# sf2_global_edit.py
import customtkinter as ctk
from my_spinner import MySpinner
from sf2_player_fs import set_gain, set_midi_chan, set_midi_transpose, load_sf2_file

saved_sf2_filename = 'default-GM.sf2'

class GlobalEdit:
  def __init__(self, ctx_instance):
    self.ctx = ctx_instance

    # Persistent state variables
    self.vol_value = "50"
    self.chan_value = "OMNI"
    self.transpose_value = "0"
    self.sf2_value = saved_sf2_filename

    # References to active spinners
    self.vol_spinner = None
    self.chan_spinner = None
    self.transpose_spinner = None

  def draw(self):
    print("GLOBAL EDIT selected!")
    self.ctx.clear_window()

    # Title at the top
    title_label = ctk.CTkLabel(self.ctx, text="GLOBAL Edit", font=self.ctx.font)
    title_label.pack(side="top", pady=(8, 4))

    # Save button at the bottom
    btn_save = ctk.CTkButton(
        self.ctx, text="MENU", command=self.go_to_menu, width=180
    )
    btn_save.pack(side="bottom", pady=8)

    large_font = ("Helvetica", 16)

    sp_padx=5
    sp_minsize=120
    sp_ew=160
    # Global Volume spinner
    vol_list = [str(n) for n in range(0, 101, 10)]
    self.vol_spinner = MySpinner(
        self.ctx, vol_list, self.vol_value, large_font, "Volume:",
        command=self.on_volume_changed, padx=sp_padx, minsize=sp_minsize, entry_width=sp_ew
    )
    self.vol_spinner.draw()

    # MIDI Channel spinner
    chan_list = ["OMNI"]
    for n in range(1, 17):
      chan_list.append(str(n))
    self.chan_spinner = MySpinner(
        self.ctx, chan_list, self.chan_value, large_font, "MIDI Channel:",
        command=self.on_chan_changed, padx=sp_padx, minsize=sp_minsize, entry_width=sp_ew
    )
    self.chan_spinner.draw()

    # Transpose spinner
    transpose_list = [str(n) for n in range(-36, 1)]
    for n in range(1, 37):
      transpose_list.append("+" + str(n))
    self.transpose_spinner = MySpinner(
        self.ctx, transpose_list, self.transpose_value, large_font, "Transpose:",
        command=self.on_transpose_changed, padx=sp_padx, minsize=sp_minsize, entry_width=sp_ew
    )
    self.transpose_spinner.draw()

    #sf2 file spinner
    sf2_list = ['default-GM.sf2',  'FluidR3_GM.sf2',  'TimGM6mb.sf2']
    self.sf2_spinner = MySpinner(
        self.ctx, sf2_list, self.sf2_value, large_font, "sf2 File:",
        command=self.on_sf2_changed, padx=sp_padx, minsize=sp_minsize, entry_width=sp_ew
    )
    self.sf2_spinner.draw()

    self.ctx.update_idletasks()

  def save_current_values(self):
    """Safely grabs text from entry boxes before they are destroyed."""
    try:
      if self.vol_spinner:
        self.vol_value = self.vol_spinner.entry.get()
      if self.chan_spinner:
        self.chan_value = self.chan_spinner.entry.get()
      if self.transpose_spinner:
        self.transpose_value = self.transpose_spinner.entry.get()
      if self.sf2_spinner:
        self.sf2_value = self.sf2_spinner.entry.get()
    except Exception:
      pass  # Failsafe if widgets are already gone

  def go_to_menu(self):
    # Save values, then trigger the menu screen transition
    self.save_current_values()
    self.ctx.menu_screen()

  def on_volume_changed(self, new_val):
      self.vol_value = new_val
      f = float(self.vol_value) / 100.0 # scale 0-100 to 0-1
      set_gain(f)

  def on_chan_changed(self, new_val):
      self.chan_value = new_val
      set_midi_chan(new_val)

  def on_transpose_changed(self, new_val):
      self.transpose_value = new_val
      set_midi_transpose(new_val)

  def on_sf2_changed(self, new_val):
    self.sf2_value = new_val
    load_sf2_file(new_val)

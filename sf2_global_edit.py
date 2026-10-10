# sf2_global_edit.py
import customtkinter as ctk
from my_spinner import MySpinner
from sf2_player_fs import set_gain, set_midi_chan, set_midi_transpose


class GlobalEdit:
  def __init__(self, ctx_instance):
    self.ctx = ctx_instance

    # Persistent state variables
    self.vol_value = "50"
    self.chan_value = "OMNI"
    self.transpose_value = "0"

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

    # Global Volume spinner
    vol_list = [str(n) for n in range(0, 101, 10)]
    self.vol_spinner = MySpinner(
        self.ctx, vol_list, self.vol_value, large_font, "Volume:",
        command=self.on_volume_changed, padx=20, minsize=170
    )
    self.vol_spinner.draw()

    # MIDI Channel spinner
    chan_list = ["OMNI"]
    for n in range(1, 17):
      chan_list.append(str(n))
    self.chan_spinner = MySpinner(
        self.ctx, chan_list, self.chan_value, large_font, "MIDI Channel:",
        command=self.on_chan_changed, padx=20, minsize=170
    )
    self.chan_spinner.draw()

    # Transpose spinner
    transpose_list = [str(n) for n in range(-36, 1)]
    for n in range(1, 37):
      transpose_list.append("+" + str(n))
    self.transpose_spinner = MySpinner(
        self.ctx, transpose_list, self.transpose_value, large_font, "Transpose:",
        command=self.on_transpose_changed, padx=20, minsize=170
    )
    self.transpose_spinner.draw()

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

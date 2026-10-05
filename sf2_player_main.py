import platform
import customtkinter as ctk

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
    self.program_list = ["Piano 1", "Piano 2", "Honkey Tonk", "Organ"]

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
    title_label.pack(pady=30)

    # Action buttons that route to other functions
    btn_single = ctk.CTkButton(self, text="SINGLE Mode", command=self.action_single_mode, 
        width=200)
    btn_single.pack(pady=10)

    btn_combi = ctk.CTkButton(self, text="COMBI Mode", command=self.action_combi_mode, 
        width=200)
    btn_combi.pack(pady=10)

    btn_exit = ctk.CTkButton(self, text="Exit App", command=self.destroy,
        width=200, height=40)
    btn_exit.pack(pady=20) 

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
    title_label.pack(side="top", pady=20)

    # 4. Save button at the bottom of the screen
    btn_save = ctk.CTkButton(self, text="Save & Return", command=self.save_program_selection,
        width=200)
    btn_save.pack(side="bottom", pady=20)

    # 3. Middle frame containing the label and dropdown, centered vertically
    center_frame = ctk.CTkFrame(self, fg_color="transparent")
    center_frame.pack(expand=True, padx=5, pady=10)

    label_select = ctk.CTkLabel(center_frame, text="Select a Program:", font=self.font_small)
    label_select.pack(side="left", padx=(0, 15))

    # Create a StringVar initialized to the currently saved program
    initial_program = self.program_list[self.current_program_index]
    self.selected_program_var = ctk.StringVar(value=initial_program)

    # Create the combobox
    self.program_combo = ctk.CTkComboBox(center_frame, values=self.program_list,
        variable=self.selected_program_var, font=self.font_small, state="readonly")
    self.program_combo.pack(side="left") 

    # Force the text to render immediately upon loading
    self.program_combo.set(initial_program)
    self.update_idletasks()

  def save_program_selection(self):
    # Get the value from our StringVar (or combobox)
    selected_item = self.selected_program_var.get()

    if selected_item in self.program_list:
      self.current_program_index = self.program_list.index(selected_item)
      print(
          f"Saved Program Index: {self.current_program_index} ({selected_item})"
      )

    # Return to single mode
    self.action_single_mode()

  def save_program_selection(self):
    selected_item = self.program_combo.get()

    if selected_item in self.program_list:
      # Save the index to our tracking variable
      self.current_program_index = self.program_list.index(selected_item)
      print(
          f"Saved Program Index: {self.current_program_index} ({selected_item})"
      )

    # Return to single mode
    self.action_single_mode()

  def action_combi_mode(self):
    print("COMBI Mode selected!")
    # Add your logic for feature two here


if __name__ == "__main__":
  app = App()
  app.mainloop()


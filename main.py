import customtkinter as ctk

ctk.set_appearance_mode("dark") # or light
ctk.set_default_color_theme("blue")  # or green or blue-green

root = ctk.CTk()
root.geometry = ("500x350")

#Enable Fullscreen Mode
root.attributes("-fullscreen", True)

def login():
    print("login") 

frame = ctk.CTkFrame(master=root)
frame.pack(pady=20, padx=60, fill="both", expand=True)

helvetica_font = ctk.CTkFont(family="Helvetica", size=24, weight="bold")
label = ctk.CTkLabel(master=frame, text="Login System",  font=helvetica_font)
label.pack(pady=12, padx=10)

entry1 = ctk.CTkEntry(master=frame, placeholder_text="Username")
entry1.pack(pady=12, padx=10)

entry2 = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
entry2.pack(pady=12, padx=10)

button = ctk.CTkButton(master=frame, text="Login", command=login)
button.pack(pady=12, padx=10)

checkbox = ctk.CTkCheckBox(master=frame, text="Remeber Me")
checkbox.pack(pady=12, padx=10)

root.mainloop() 

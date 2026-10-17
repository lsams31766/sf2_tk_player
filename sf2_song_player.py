# sf2_song_player.py

import customtkinter as ctk
from my_spinner import MySpinner
from sf2_player_fs import play_midi_file, stop_midi_file
from pathlib import Path

sMidiFileDir = "/home/larry/"
file_names = []

class SongPlayer:
    def __init__(self, ctx_instance):
        self.ctx = ctx_instance
        self.font = getattr(ctx_instance, "font", ctk.CTkFont(family="Helvetica", size=24, weight="bold"))
        self.font_small = getattr(ctx_instance, "font_small", ctk.CTkFont(family="Helvetica", size=18, weight="bold"))
        self.current_program_index = 0
        self.make_songs_list()
        self.cur_song = file_names[0]

    def draw(self):
        print("Song Player selected!")
        self.ctx.clear_window()
        large_font = ("Helvetica", 16)

        title_label = ctk.CTkLabel(self.ctx, text="SONG Player", font=large_font)
        title_label.pack(side="top", pady=20)
        
        btn_home = ctk.CTkButton(
            self.ctx, text="MENU", command=self.ctx.menu_screen, width=200
        )
        btn_home.pack(side="bottom", pady=20)
        
        # Song Spinner
        self.song_spinner = MySpinner(
            self.ctx, file_names, self.cur_song, large_font, "Song:",
            command=self.on_song_changed, padx=20, minsize=100, entry_width=220
        )
        self.song_spinner.draw()
        # Play Button
        btn_play = ctk.CTkButton(
            self.ctx, text="Play", command=self.play, width=200
        )
        btn_play.pack(pady=10)
        
        # Stop Button
        btn_stop = ctk.CTkButton(
            self.ctx, text="Stop", command=self.stop, width=200
        )
        btn_stop.pack(pady=10)


    def on_song_changed(self, value):
        self.cur_song = value

    def make_songs_list(self):
        global file_names
        directory_path = Path(sMidiFileDir)
        file_names = [file.name for file in directory_path.glob("*.mid")]

    def play(self):
        play_midi_file(self.cur_song)

    def stop(self):
        stop_midi_file()


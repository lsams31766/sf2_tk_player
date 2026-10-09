#sf2_player_fs.py
# fluidsynth code
import sys
import time
import os
import threading
import subprocess
import fluidsynth
import mido
from pathlib import Path 
from sf2_player_settings import save_settings, load_settings
from sf2_player_controls import load_default_reverb_settings, load_default_chorus_settings


fs = None
# Global handles for playback control
midi_player_thread = None
midi_stop_event = threading.Event()

# Keep track of state globally
current_bank = 0
current_program = 0
current_instrument_name = ''
current_sf_id = 0 
current_gain = 0.5
current_program_list = []

# --- MIDI FILTER & TRANSPOSE CONFIGURATION ---
TARGET_MIDI_CHANNEL = 0  
input_filter_channel = None  # None = OMNI (accept all channels)
midi_transpose = 0

midi_thread_running = False

sf2_directory = '/usr/share/sounds/sf2/'
nbr_sf2_files = 1 
current_sf2_name = 'unknown'

active_layer_channels = [0]
split_point = -1

def find_midi_keyboard_port():
    """Dynamically find the keyboard port name to avoid strict string mismatches."""
    ports = mido.get_input_names()
    print(f"Available MIDI input ports: {ports}")
    for port in ports:
        if 'Carbon61' in port:
            return port
    if ports:
        return ports[0]
    return None

def midi_listener_thread():
    """Background thread that captures USB MIDI, applies filters/transposition, and plays notes on all active layer channels."""
    global midi_thread_running
    
    time.sleep(1.0)
    port_name = find_midi_keyboard_port()
    if not port_name:
        print("MIDI Listener Error: No MIDI input ports found! Is the keyboard plugged in?")
        return

    try:
        print(f"Opening MIDI input port: {port_name}")
        with mido.open_input(port_name) as inport:
            midi_thread_running = True
            for msg in inport:
                if not midi_thread_running:
                    break

                #print(f'note_on channel {msg.channel} note {msg.note}')
                if input_filter_channel is not None:
                   if hasattr(msg, 'channel') and msg.channel != input_filter_channel:
                       continue 

                if msg.type == 'note_on':
                    #print(f'note_on channel {msg.channel} note {msg.note}')
                    new_note = max(0, min(127, msg.note + midi_transpose))
                    #handle split mode
                    # if len(active_layer_channels) == 2:
                    #     s = f'note_on sp {split_point}, alc0: {active_layer_channels[0]}'
                    #     s += f' alc1: {active_layer_channels[1]}'
                    #     s += f' msg.channel {msg.channel}, new_note {new_note}'
                    #     print(s)
                    if split_point > 0 and len(active_layer_channels) == 2:
                        if msg.channel == active_layer_channels[0] and \
                            new_note < split_point:
                                if msg.velocity > 0:
                                    fs.noteon(active_layer_channels[0], new_note, msg.velocity)
                                else:
                                    fs.noteoff(active_layer_channels[0], new_note)
                        elif msg.channel == active_layer_channels[0] and \
                            new_note >= split_point:
                                if msg.velocity > 0:
                                    fs.noteon(active_layer_channels[1], new_note, msg.velocity)
                                else:
                                    fs.noteoff(active_layer_channels[1], new_note)
                    else:
                        for dest_channel in active_layer_channels:
                            if msg.velocity > 0:
                                fs.noteon(dest_channel, new_note, msg.velocity)
                            else:
                                fs.noteoff(dest_channel, new_note)
                        
                elif msg.type == 'note_off':
                    new_note = max(0, min(127, msg.note + midi_transpose))
                    for dest_channel in active_layer_channels:
                        fs.noteoff(dest_channel, new_note)
                    
                elif msg.type == 'control_change':
                    for dest_channel in active_layer_channels:
                        fs.cc(dest_channel, msg.control, msg.value)
                    
                elif msg.type == 'pitchwheel':
                    for dest_channel in active_layer_channels:
                        fs.pitch_bend(dest_channel, msg.pitch)
                        
    except Exception as e:
        print(f"MIDI Listener Error: {e}")
        midi_thread_running = False

def _ensure_pipewire_jack_wrapper():
    if os.environ.get("SF2_PLAYER_PW_JACK_WRAPPED") == "1":
        return
    ld_path = os.environ.get("LD_LIBRARY_PATH", "")
    if "pipewire" in ld_path and "jack" in ld_path:
        return

    print("Relaunching under pw-jack so fluidsynth can reach pipewire's JACK layer...")
    env = os.environ.copy()
    env["SF2_PLAYER_PW_JACK_WRAPPED"] = "1"
    try:
        os.execvpe("pw-jack", ["pw-jack", sys.executable] + sys.argv, env)
    except FileNotFoundError:
        print("Warning: 'pw-jack' not found on PATH.")

def init_fluidsynth(effect_callback=None):
    """
    Initializes FluidSynth and starts MIDI listening.
    effect_callback: Optional function (like start_reverb_effect or start_chorus_effect) 
                     to wire audio routing after startup.
    """
    global fs, current_sf_id, current_bank, current_program, current_instrument_name, \
        current_sf2_name, current_gain, input_filter_channel, midi_transpose, split_point

    _ensure_pipewire_jack_wrapper()

    settings = load_settings()
    fs = fluidsynth.Synth()
    fs.setting('audio.jack.autoconnect', 1)  # Change 0 to 1
    fs.setting('audio.period-size', 128)
    fs.setting('audio.periods', 2)
    #fs.setting('synth.sample-rate', 44100.0)
    fs.setting('synth.sample-rate', 48000.0) # Change 44100.0 to 48000.0
    fs.setting('midi.driver', 'alsa_seq')

    fs.start(driver="jack")

    sf_path = "/usr/share/sounds/sf2/"
    current_sf2_name = settings.get('soundfont_filename', 'default-GM.sf2')
    sf_id = fs.sfload(os.path.join(sf_path, current_sf2_name))
    
    temp_filter = settings.get('midi_channel', 'OMNI')
    if temp_filter == "OMNI":
        input_filter_channel = None
    else:
        input_filter_channel = int(temp_filter) - 1
    midi_transpose = settings.get('transpose', 0)

    if sf_id == -1:
        print(f"Error: Could not load SoundFont at {sf_path}")
        exit(1)

    current_sf_id = sf_id
    current_bank = 0
    current_program = 0
    fs.program_select(0, current_sf_id, current_bank, current_program)
    try:
        name_query = fs.sfpreset_name(current_sf_id, current_bank, current_program)
        if name_query:
            current_instrument_name = name_query
    except Exception:
        pass
    print(f"SoundFont initialized with {current_instrument_name}")
    print("gettings instruments list")
    list_instruments_in_bank() # load current_program_list

    #layering and splitting
    split_settings = settings.get("split_settings", None)
    if split_settings != None:
        layer_split_mode = split_settings.get("layer_split_mode",None)
        if layer_split_mode != None:
            if layer_split_mode == 1: # layer
                split_point = -1
            if layer_split_mode == 0: # split point
                split_point = split_settings['split_point']
            split_keyboard(split_point)
        layer_sounds(midi_chan1=1, 
                     bank1=0, 
                     prog1=split_settings['layer_1_prog_number'], 
                     midi_chan2=2, 
                     bank2=0, 
                     prog2=split_settings['layer_2_prog_number']
                     )


    current_gain = settings.get('master_volume', 0.5)
    fs.setting('synth.gain', current_gain)

    # Start MIDI listener thread
    t = threading.Thread(target=midi_listener_thread, daemon=True)
    t.start()

    # Execute passed audio effect callback if provided
    #if effect_callback:
    #    effect_callback()

    try:
        print("Setting PipeWire default sink volume to 1.8...")
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "1.8"], check=True)
    except Exception as e:
        print(f"Warning: Could not set system volume via wpctl: {e}")

    print("\n--- Setup Complete! Play your Carbon61 ---")
    print("Press Ctrl+C to stop the script.")

def list_instruments_in_bank(target_bank=0):
    """
    Queries the loaded SoundFont and prints/returns all programs 
    and instrument names matching the target_bank.
    """
    global current_program_list
    print(f"\n--- Instruments in Bank {target_bank} (SoundFont ID: {current_sf_id}) ---")
    
    current_program_list = [] # clear out old list
    try:
        # Modern pyfluidsynth returns a list of tuples or lists: (bank, program, name)
        preset_list = fs.get_preset_info(current_sf_id)
        
        for bank, program, name in preset_list:
            if bank == target_bank:
                print(f"Program {program:03d}: {name}")
                current_program_list.append({"program": program, "name": name})
                
    except AttributeError:
        # Fallback method: If your pyfluidsynth version doesn't have get_preset_info,
        # we manually scan all 128 possible MIDI program slots.
        for program in range(128):
            name = fs.sfpreset_name(current_sf_id, target_bank, program)
            if name:  # If a preset exists at this slot, it returns the string name
                print(f"Program {program:03d}: {name}")
                current_program_list.append({"program": program, "name": name})
                
    if not current_program_list:
        print(f"No instruments found in bank {target_bank}.")

def fs_get_program_list():
    l = [p["name"] for p in current_program_list]
    return l

def previous_preset():
    global current_program, current_bank, current_sf_id, fs, current_instrument_name
    if current_program > 0:
        current_program -= 1
    else:
        print("Reached minimum program (0).")
        return

    if fs and current_sf_id > 0:
        fs.program_select(0, current_sf_id, current_bank, current_program)
        print(f"previous preset -> Switched to Bank: {current_bank}, Program: {current_program}")
        try:
            name_query = fs.sfpreset_name(current_sf_id, current_bank, current_program)
            if name_query:
                current_instrument_name = name_query
        except Exception:
            pass

def next_preset():
    global current_program, current_bank, current_sf_id, fs, current_instrument_name
    if current_program < 127:
        current_program += 1
    else:
        print("Reached maximum program (127).")
        return

    if fs and current_sf_id > 0:
        fs.program_select(0, current_sf_id, current_bank, current_program)
        print(f"next pressed -> Switched to Bank: {current_bank}, Program: {current_program}")
        try:
            name_query = fs.sfpreset_name(current_sf_id, current_bank, current_program)
            if name_query:
                current_instrument_name = name_query
        except Exception:
            pass

def set_preset(new_progr_nbr):
    global current_program, current_bank, current_sf_id, fs, current_instrument_name
    current_program = new_progr_nbr

    if fs and current_sf_id > 0:
        fs.program_select(0, current_sf_id, current_bank, current_program)
        print(f"next pressed -> Switched to Bank: {current_bank}, Program: {current_program}")
        try:
            name_query = fs.sfpreset_name(current_sf_id, current_bank, current_program)
            if name_query:
                current_instrument_name = name_query
        except Exception:
            pass


def get_current_preset_details():
    return current_bank, current_program, current_instrument_name

def get_gain():
    return current_gain 

def set_gain(fValue):
    fs.setting('synth.gain', fValue)

def lower_gain():
    global current_gain
    if current_gain < 0.01:
        return 
    current_gain -= 0.1
    if current_gain < 0:
        current_gain = 0.0
    set_gain(current_gain)

def raise_gain():
    global current_gain
    if current_gain >= 1.0:
        return 
    current_gain += 0.1
    if current_gain > 1.0:
        current_gain = 1.0
    set_gain(current_gain)

def get_midi_chan_display():
    if input_filter_channel is None:
        return 'OMNI'
    return str(input_filter_channel + 1)

def set_midi_chan(new_chan):
    global input_filter_channel
    if str(new_chan) == "OMNI":
        input_filter_channel = -1
    else:
        input_filter_channel = int(new_chan) - 1

def lower_midi_chan():
    global input_filter_channel
    if input_filter_channel is None:
        input_filter_channel = 15 
    elif input_filter_channel > 0:
        input_filter_channel -= 1
    else:
        input_filter_channel = None 
    print(f"MIDI Filter Channel set to: {get_midi_chan_display()}")

def raise_midi_chan():
    global input_filter_channel
    if input_filter_channel is None:
        input_filter_channel = 0 
    elif input_filter_channel < 15:
        input_filter_channel += 1
    else:
        input_filter_channel = None 
    print(f"MIDI Filter Channel set to: {get_midi_chan_display()}")

def get_transpose():
    return midi_transpose

def set_midi_transpose(val):
    global midi_transpose
    n = int(val)
    midi_transpose = n

def raise_midi_transpose():
    global midi_transpose
    if midi_transpose < 12:
        midi_transpose += 1
    print(f"Transpose set to: {midi_transpose:+d} semitones")

def lower_midi_transpose():
    global midi_transpose
    if midi_transpose > -12:
        midi_transpose -= 1
    print(f"Transpose set to: {midi_transpose:+d} semitones")

def get_sf2_filenames():
    global nbr_sf2_files
    directory_path = Path(sf2_directory)
    file_names = [file.name for file in directory_path.glob("*.sf2")]
    nbr_sf2_files = len(file_names)
    return file_names

def get_nbr_sf2_files():
    return nbr_sf2_files

def lookup_prog_name():
    global current_instrument_name
    try:
        name_query = fs.sfpreset_name(current_sf_id, current_bank, current_program)
        if name_query:
            current_instrument_name = name_query
    except Exception:
        pass

def get_sf_file_index():
    files = get_sf2_filenames()
    for index, f in enumerate(files):
        if f == current_sf2_name:
            return index 
    return 0
        
def load_sf2_file(selected_sf2_index):
    global current_sf_id, current_bank, current_program, current_instrument_name, current_sf2_name
    filename = get_sf2_filenames()[selected_sf2_index]
    current_sf2_name = filename
    old_sf_id = current_sf_id
    full_path = os.path.join(sf2_directory, filename) 
    current_sf_id = fs.sfload(full_path)
    fs.program_select(0, current_sf_id, 0, 0)
    fs.sfunload(old_sf_id)
    current_bank = 0 
    current_program = 0
    lookup_prog_name()

def get_current_prog_details():
    return current_bank, current_program, current_instrument_name

def save_settings_to_file(current_reverb_settings, current_chorus_settings, reverb_enabled, chorus_enabled, split_settings):
    if current_reverb_settings == []:
        temp_reverb_settings = load_default_reverb_settings()
    else:
        temp_reverb_settings = current_reverb_settings
    if current_chorus_settings == []:
        temp_chorus_settings = load_default_chorus_settings()
    else:
        temp_chorus_settings = current_chorus_settings
    current_settings = {
        "master_volume": round(current_gain, 2),
        "midi_channel": get_midi_chan_display(),
        "transpose": midi_transpose,
        "soundfont_filename": current_sf2_name,
        "reverb_enabled":reverb_enabled,
        "chorus_enabled":chorus_enabled,
        "reverb":temp_reverb_settings,
        "chorus":temp_chorus_settings,
        "split_settings":split_settings
    }
    save_settings(current_settings)

#-----------LAYERING---------------------------#
def layer_sounds(midi_chan1, bank1, prog1, midi_chan2, bank2, prog2):
    """
    Configures two MIDI channels with specific SoundFont banks and programs,
    and sets them up to be triggered simultaneously by incoming MIDI data.
    Note: midi_chan1 and midi_chan2 are 1-based (e.g., 1 and 2).
    """
    global active_layer_channels, fs, current_sf_id
    if fs is None or current_sf_id == 0:
        print("FluidSynth not initialized or SoundFont not loaded.")
        return

    # Convert 1-based MIDI channels to 0-based FluidSynth channels
    ch1 = midi_chan1 - 1
    ch2 = midi_chan2 - 1

    # Assign presets to both channels
    fs.program_select(ch1, current_sf_id, bank1, prog1)
    fs.program_select(ch2, current_sf_id, bank2, prog2)

    # Set them as the active broadcast channels for the listener thread
    active_layer_channels = [ch1, ch2]
    
    print(f"Layering active: MIDI Ch {midi_chan1} (Bank {bank1}, Prog {prog1}) + "
          f"MIDI Ch {midi_chan2} (Bank {bank2}, Prog {prog2})")    

def lookup_prog_name_from_prog_number(prog_nbr):
    try:
        name_query = fs.sfpreset_name(current_sf_id, current_bank, prog_nbr)
        if name_query:
            return name_query
    except Exception:
        return 'Unknown'

def fs_turn_off_layering():
    global active_layer_channels, split_point
    active_layer_channels = [0]
    split_point = -1 

def split_keyboard(new_split_point):
    global split_point
    split_point = new_split_point

def turn_off_split_keyboard():
    global split_point
    split_point = -1

#for midi song playback
def play_midi_file(filename="SONG1.mid"):
    """Starts playing a MIDI file in a background thread so the UI stays responsive."""
    global midi_player_thread, midi_stop_event
    
    # If already playing, stop the current playback first
    if midi_player_thread and midi_player_thread.is_alive():
        stop_midi_file()

    midi_stop_event.clear()
    
    def _player_worker():
        try:
            mid = mido.MidiFile(filename)            
            for message in mid.play():
                if midi_stop_event.is_set():
                    break
                
                # Send events to pyfluidsynth
                if message.type == 'note_on':
                    fs.noteon(message.channel, message.note, message.velocity)
                elif message.type == 'note_off':
                    fs.noteoff(message.channel, message.note)
                elif message.type == 'program_change':
                    fs.program_change(message.channel, message.program)
                elif message.type == 'control_change':
                    fs.cc(message.channel, message.control, message.value)
        except Exception as e:
            print(f"Error playing MIDI file: {e}")

    midi_player_thread = threading.Thread(target=_player_worker, daemon=True)
    midi_player_thread.start()
    print(f"Started playback: {filename}")

def stop_midi_file():
    """Signals the background MIDI player thread to stop."""
    global midi_stop_event, midi_player_thread
    if midi_player_thread and midi_player_thread.is_alive():
        midi_stop_event.set()
        midi_player_thread.join(timeout=0.5)
        print("MIDI playback stopped.")

    try:
        for channel in range(16):
            fs.cc(channel, 120, 0)  # CC 120: All Sound Off (cuts sound instantly)
            fs.cc(channel, 123, 0)  # CC 123: All Notes Off (respects release tails)
    except Exception as e:
        print(f"Error silencing notes: {e}")
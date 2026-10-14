"""Touchscreen touch-down/up detection for resistive panels (e.g. ADS7846).

X reports this kind of device as a plain pointer with no button events, so
we read touch state straight from the kernel with evdev and deliver it on
the Tk thread.
"""
import queue
import threading 

from evdev import InputDevice, list_devices, ecodes


def find_device(name_part="ADS7846"):
    for path in list_devices():
        dev = InputDevice(path)
        if name_part in dev.name:
            return dev
    raise RuntimeError(f"No input device matching {name_part!r}")


class TouchState:
    """Calls registered listeners with True (touch down) / False (touch up)."""

    def __init__(self, root, device_name="ADS7846", pressure_threshold=0, poll_ms=10):
        self._root = root
        self._threshold = pressure_threshold
        self._poll_ms = poll_ms
        self._q = queue.Queue()
        self._listeners = []
        self._dev = find_device(device_name)
        threading.Thread(target=self._reader, daemon=True).start()
        self._poll()

    def add_listener(self, fn):
        self._listeners.append(fn)

    def _reader(self):
        touching = False
        for ev in self._dev.read_loop():
            if ev.type == ecodes.EV_KEY and ev.code == ecodes.BTN_TOUCH:
                new = bool(ev.value)
            elif ev.type == ecodes.EV_ABS and ev.code == ecodes.ABS_PRESSURE:
                new = ev.value > self._threshold
            else:
                continue
            if new != touching:
                touching = new
                self._q.put(new)

    def _poll(self):
        try:
            while True:
                state = self._q.get_nowait()
                for fn in self._listeners:
                    fn(state)
        except queue.Empty:
            pass
        self._root.after(self._poll_ms, self._poll)

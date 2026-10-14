"""CTkButton that fires once on press, then auto-repeats while held."""
import customtkinter as ctk 


class RepeatButton(ctk.CTkButton):
    def __init__(self, master, touch=None, command=None,
                 delay=1000, interval=100, touch_settle_ms=50, **kwargs):
        super().__init__(master, command=None, **kwargs)
        self._cmd = command
        self._delay = delay
        self._interval = interval
        self._settle = touch_settle_ms
        self._after_id = None

        if touch is not None:                      # touchscreen path
            touch.add_listener(self._on_touch)

        top = self.winfo_toplevel()                # real mouse path
        top.bind("<ButtonPress-1>", lambda e: self._start_if_inside(), add="+")
        top.bind("<ButtonRelease-1>", lambda e: self._stop(), add="+")

    def _pointer_inside(self):
        x, y = self.winfo_pointerxy()
        bx, by = self.winfo_rootx(), self.winfo_rooty()
        return bx <= x < bx + self.winfo_width() and by <= y < by + self.winfo_height()

    def _on_touch(self, down):
        if down:
            # give X a moment to move the pointer to the touch point
            self.after(self._settle, self._start_if_inside)
        else:
            self._stop()

    def _start_if_inside(self):
        if self._after_id is None and self._pointer_inside():
            self._fire()
            self._after_id = self.after(self._delay, self._repeat)

    def _repeat(self):
        self._fire()
        self._after_id = self.after(self._interval, self._repeat)

    def _stop(self):
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    def _fire(self):
        if self._cmd:
            self._cmd()

    def destroy(self):
        self._stop()
        super().destroy()

import customtkinter as ctk


class RepeatButton(ctk.CTkButton):
    def __init__(self, master, touch=None, command=None,
                 delay=500, interval=100, touch_settle_ms=150,
                 reset_delay_ms=30, **kwargs):
        super().__init__(master, command=None, **kwargs)
        self._cmd = command
        self._delay = delay         # Hold time before continuous firing begins (500 ms)
        self._interval = interval   # Interval between repeats while held
        self._settle = touch_settle_ms
        self._reset_delay = reset_delay_ms  # Small wait so our reset runs after CTk's own handling
        self._after_id = None       # hold-delay / repeat timer
        self._settle_id = None      # pending touch "settle" timer
        self._reset_id = None       # pending visual reset timer
        self._pressed = False       # True only while a press is actually in progress
        self._press_inside = False  # True once the press is confirmed to be on this button
        self._hold_fired = False    # True once the long-press (continuous) firing has begun

        if touch is not None:                      # touchscreen path
            touch.add_listener(self._on_touch)

        top = self.winfo_toplevel()                # real mouse path
        top.bind("<ButtonPress-1>", lambda e: self._on_press(), add="+")
        top.bind("<ButtonRelease-1>", lambda e: self._stop(), add="+")

        # Also catch the release on the button itself
        self.bind("<ButtonRelease-1>", lambda e: self._schedule_reset(), add="+")

    # ------------------------------------------------------------------
    # Visual state handling
    # ------------------------------------------------------------------
    def _schedule_reset(self):
        """Schedule a redraw to the un-pressed look after a short tick."""
        if not self.winfo_exists():
            return
        if self._reset_id is not None:
            try:
                self.after_cancel(self._reset_id)
            except Exception:
                pass
        self._reset_id = self.after(self._reset_delay, self._reset_look)

    def _reset_look(self):
        """Force the button back to its un-pressed appearance."""
        self._reset_id = None
        if not self.winfo_exists():
            return
        try:
            # Preferred: CustomTkinter's own leave handler restores the
            # normal colors and clears the hover/click state.
            self._on_leave()
        except Exception:
            # Fallback for versions where the private handler differs
            try:
                self._hover_state = False
                self._draw()
            except Exception:
                pass
        try:
            self.update_idletasks()
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Pointer / touch handling
    # ------------------------------------------------------------------
    def _pointer_inside(self):
        if not self.winfo_exists():
            return False
        x, y = self.winfo_pointerxy()
        bx, by = self.winfo_rootx(), self.winfo_rooty()
        return bx <= x < bx + self.winfo_width() and by <= y < by + self.winfo_height()

    def _begin_press(self):
        self._pressed = True
        self._press_inside = False
        self._hold_fired = False

    def _on_press(self):
        """A press began (mouse path)."""
        if not self.winfo_exists():
            return
        if not self._pressed:               # a touch may already have started this press
            self._begin_press()
        self._start_if_inside()

    def _on_touch(self, down):
        if not self.winfo_exists():
            return
        if down:
            if not self._pressed:
                self._begin_press()
            # give X a moment to move the pointer to the touch point
            if self._settle_id is not None:
                self.after_cancel(self._settle_id)
            self._settle_id = self.after(self._settle, self._after_settle)
        else:
            self._stop()

    def _after_settle(self):
        self._settle_id = None
        # If the finger was already lifted during the settle wait, do nothing.
        if not self._pressed:
            return
        self._start_if_inside()

    def _start_if_inside(self):
        if not self.winfo_exists() or not self._pressed:
            return
        if self._pointer_inside():
            self._press_inside = True
            if self._after_id is None and not self._hold_fired:
                # Wait for the hold threshold before continuous firing begins
                self._after_id = self.after(self._delay, self._first_fire_and_repeat)

    def _first_fire_and_repeat(self):
        if not self.winfo_exists():
            return
        self._after_id = None
        if not self._pressed:       # released before the hold threshold
            return
        self._hold_fired = True     # this is now a long press; release must not fire again
        self._fire()
        # Switch to the faster repeat interval for subsequent triggers while held
        self._after_id = self.after(self._interval, self._repeat)

    def _repeat(self):
        if not self.winfo_exists():
            return
        self._after_id = None
        if not self._pressed:       # safety net: never repeat without a held press
            return
        self._fire()
        self._after_id = self.after(self._interval, self._repeat)

    def _stop(self, reset=True):
        was_pressed = self._pressed
        settle_pending = self._settle_id is not None
        self._pressed = False
        if not self.winfo_exists():
            return
        if self._settle_id is not None:     # cancel a touch start that hasn't happened yet
            self.after_cancel(self._settle_id)
            self._settle_id = None
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

        # Brief click: fire exactly once on release (long presses already fired).
        if reset and was_pressed and not self._hold_fired:
            # If a touch was released before the settle wait ended, we never got to
            # confirm the location, so check where the pointer is right now.
            on_button = self._press_inside or (settle_pending and self._pointer_inside())
            if on_button:
                self._fire()

        self._hold_fired = False
        self._press_inside = False
        if reset:
            self._schedule_reset()

    def _fire(self):
        if not self.winfo_exists():
            return
        if self._cmd:
            self._cmd()

    def destroy(self):
        self._stop(reset=False)
        if self._reset_id is not None:
            try:
                self.after_cancel(self._reset_id)
            except Exception:
                pass
            self._reset_id = None
        super().destroy()
        
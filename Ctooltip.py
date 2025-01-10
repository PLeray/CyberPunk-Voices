import tkinter as tk

class Tooltip:
    """Classe pour ajouter des infobulles aux widgets Tkinter."""
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tip_window = None
        self.id_after = None
        self.widget.bind("<Enter>", self.schedule_show)
        self.widget.bind("<Leave>", self.hide_tip)

    def schedule_show(self, event=None):
        """Planifier l'affichage de l'infobulle après un délai."""
        self.id_after = self.widget.after(self.delay, self.show_tip)

    def show_tip(self):
        """Afficher l'infobulle."""
        if self.tip_window or not self.text:
            return
        x, y, _cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=5, ipady=5)

    def hide_tip(self, event=None):
        """Masquer l'infobulle et annuler l'affichage prévu."""
        if self.id_after:
            self.widget.after_cancel(self.id_after)
            self.id_after = None
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

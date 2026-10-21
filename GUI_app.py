import colorsys
import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from hillClimbing import hill_climbing, random_restart
from starter import generate_armada

CELL = 20
MAX_DELAY_MS = 1000

FIELDS = [
    ("n_vehicles", "Kendaraan", "30"),
    ("n_ships", "Kapal", "2"),
    ("sideways", "Maks sideways", "0"),
    ("neighbors", "Neighbor/iterasi", "50"),
    ("restarts", "Restart (0 = tanpa)", "0"),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Armada Optimizer")
        self.armada = None
        self.running = False
        self.q = queue.Queue()
        self.vars = {}
        self.canvases, self.infos, self.colors = {}, {}, {}
        self.delay_ms = 0       # dibaca thread algoritma, jadi bukan tk.Variable
        self.prev_fee = 0

        form = ttk.Frame(self, padding=8)
        form.pack(fill="x")
        for i, (key, label, default) in enumerate(FIELDS):
            ttk.Label(form, text=label).grid(row=0, column=2 * i)
            self.vars[key] = tk.StringVar(value=default)
            ttk.Entry(form, width=6, textvariable=self.vars[key]).grid(row=0, column=2 * i + 1, padx=(2, 10))

        buttons = ttk.Frame(self, padding=(8, 0))
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Generate", command=self.generate).pack(side="left")
        self.run_btn = ttk.Button(buttons, text="Jalankan Hill Climbing", command=self.run, state="disabled")
        self.run_btn.pack(side="left", padx=8)

        ttk.Label(buttons, text="Jeda/iterasi").pack(side="left", padx=(12, 4))
        ttk.Scale(buttons, from_=0, to=MAX_DELAY_MS, length=160, command=self._on_delay).pack(side="left")
        self.delay_label = ttk.Label(buttons, text="0 ms", width=8)
        self.delay_label.pack(side="left")

        self.status = tk.StringVar(value="Klik Generate dulu.")
        ttk.Label(buttons, textvariable=self.status).pack(side="left", padx=8)

        self.boards = ttk.Frame(self, padding=8)
        self.boards.pack(fill="both", expand=True)
        self.outside = tk.StringVar()
        ttk.Label(self, textvariable=self.outside, padding=(8, 0), wraplength=700).pack(anchor="w")
        self.log = tk.Text(self, height=8, state="disabled")
        self.log.pack(fill="x", padx=8, pady=8)

    # ---- util
    def _int(self, key):
        return int(self.vars[key].get())

    def _on_delay(self, value):
        self.delay_ms = int(float(value))
        self.delay_label.config(text=f"{self.delay_ms} ms")

    def write(self, text):
        self.log.config(state="normal")
        self.log.insert("end", text + "\n")
        self.log.see("end")
        self.log.config(state="disabled")

    # ---- aksi
    def generate(self):
        if self.running:
            return
        try:
            self.armada = generate_armada(n_vehicles=self._int("n_vehicles"), n_ships=self._int("n_ships"))
        except ValueError:
            messagebox.showerror("Input tidak valid", "Jumlah kendaraan dan kapal harus bilangan bulat.")
            return
        self.build(self.armada)
        self.render(self.armada)
        self.run_btn.config(state="normal")
        self.status.set(f"Fee awal: {self.armada.calculate_armada_shipping_fee()}")
        self.write(f"Generate: {self._int('n_vehicles')} kendaraan, {self._int('n_ships')} kapal")

    def run(self):
        if self.armada is None or self.running:
            return
        try:
            sideways, neighbors, restarts = self._int("sideways"), self._int("neighbors"), self._int("restarts")
        except ValueError:
            messagebox.showerror("Input tidak valid", "Parameter harus bilangan bulat.")
            return
        self.running = True
        self.run_btn.config(state="disabled")
        threading.Thread(target=self._worker, args=(sideways, neighbors, restarts), daemon=True).start()
        self.after(30, self._poll)

    def _worker(self, sideways, neighbors, restarts):
        def progress(it, fee, armada):
            self.q.put(("progress", it, fee, armada))
            if self.delay_ms:
                time.sleep(self.delay_ms / 1000)

        try:
            if restarts > 0:
                result = random_restart(self.armada, sideways, neighbors, restarts, progress)
            else:
                result = hill_climbing(self.armada, sideways, neighbors, progress)
            self.q.put(("done", result))
        except Exception as e:
            self.q.put(("error", repr(e)))

    def _poll(self):
        last = None
        while True:
            try:
                kind, *data = self.q.get_nowait()
            except queue.Empty:
                break
            if kind == "progress":
                it, fee, armada = data
                self._log_iteration(it, fee)
                last = (it, fee, armada)
            elif kind == "done":
                armada, fee, history = data[0]
                self.render(armada)
                self.status.set(f"Selesai | fee {history[0]} -> {fee}")
                self.write(f"Selesai: fee {history[0]} -> {fee} ({len(history) - 1} iterasi)")
                self._finish()
                return
            elif kind == "error":
                messagebox.showerror("Error", data[0])
                self._finish()
                return
        if last:  # delay kecil bikin banyak iterasi menumpuk; gambar yang terbaru saja
            it, fee, armada = last
            self.status.set(f"Iterasi {it} | fee {fee}")
            self.render(armada)
        self.after(30, self._poll)

    def _log_iteration(self, it, fee):
        if it == 0:
            self.write(f"--- mulai dari fee {fee}")
        else:
            self.write(f"Iterasi {it}: fee {fee} ({fee - self.prev_fee:+d})")
        self.prev_fee = fee

    def _finish(self):
        self.running = False
        self.run_btn.config(state="normal")

    # ---- gambar
    def build(self, armada):
        """Buat label + canvas tiap kapal sekali; render() cuma menggambar ulang isinya."""
        for child in self.boards.winfo_children():
            child.destroy()
        self.canvases, self.infos = {}, {}
        self.colors = {v.id: self._color(i) for i, v in enumerate(armada.list_all_vehicles)}
        for ship in sorted(armada.ship_list, key=lambda s: s.id):
            info = tk.StringVar()
            ttk.Label(self.boards, textvariable=info).pack(anchor="w")
            canvas = tk.Canvas(self.boards, width=ship.l * CELL + 1, height=ship.w * CELL + 1,
                               bg="#f4f6f8", highlightthickness=0)
            canvas.pack(anchor="w", pady=(0, 8))
            self.canvases[ship.id], self.infos[ship.id] = canvas, info

    def render(self, armada):
        for ship in armada.ship_list:
            canvas = self.canvases[ship.id]
            canvas.delete("all")
            for r in range(ship.w + 1):
                canvas.create_line(0, r * CELL, ship.l * CELL, r * CELL, fill="#c9d0d6")
            for c in range(ship.l + 1):
                canvas.create_line(c * CELL, 0, c * CELL, ship.w * CELL, fill="#c9d0d6")
            for v in ship.list_vehicles_in_ship:
                rows, cols = (v.w, v.l) if v.orientation == "vertical" else (v.l, v.w)
                x0, y0 = v.coor[1] * CELL, v.coor[0] * CELL
                canvas.create_rectangle(x0, y0, x0 + cols * CELL, y0 + rows * CELL,
                                        fill=self.colors[v.id], outline="#445")
                canvas.create_text(x0 + cols * CELL / 2, y0 + rows * CELL / 2, text=v.id, font=("Segoe UI", 7))
            self.infos[ship.id].set(f"Kapal {ship.id} ({ship.w}x{ship.l}) | {len(ship.list_vehicles_in_ship)} kendaraan | "
                                    f"berat {ship.calculate_ship_weight()}/{ship.max_capacity} | "
                                    f"fee {ship.calculate_shipping_fee()}")

        inside = {v for s in armada.ship_list for v in s.list_vehicles_in_ship}
        outside = [v.id for v in armada.list_all_vehicles if v not in inside]
        self.outside.set(f"Di luar kapal ({len(outside)}): " + (", ".join(outside) or "-"))

    @staticmethod
    def _color(i):
        r, g, b = colorsys.hsv_to_rgb((i * 0.618033988) % 1, 0.45, 0.97)
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


if __name__ == "__main__":
    App().mainloop()

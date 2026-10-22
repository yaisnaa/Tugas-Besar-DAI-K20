import colorsys
import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import copy


from hillClimbing import hill_climbing, random_restart
from simulated_annealing import simulated_annealing
from starter import generate_armada, global_optima
from genetic import run_genetic_algorithm, run_benchmark_experiments



CELL = 20
MAX_DELAY_MS = 1000

HC_FIELDS = [
    ("n_vehicles", "Kendaraan", "30"),
    ("n_ships", "Kapal", "2"),
    ("sideways", "Maks sideways", "0"),
    ("neighbors", "Neighbor/iterasi", "50"),
    ("restarts", "Restart (0 = tanpa)", "0"),
]
SA_FIELDS = [
    ("temp", "Suhu awal (T)", "100"),
    ("cooling", "Cooling rate", "0.99"),
]
GA_FIELDS = [
    ("pop_size", "Populasi GA", "40"),
    ("generations", "Generasi GA", "30"),
]


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Armada Optimizer")
        self.geometry("960x760")
        self.minsize(860, 560)
        self.armada = None
        self.running = False
        self.q = queue.Queue()
        self.vars = {}
        self.algo = tk.StringVar(value="hill")
        self.stochastic = tk.BooleanVar(value=False)
        self.canvases, self.infos, self.colors = {}, {}, {}
        self.delay_ms = 0       # dibaca thread algoritma, jadi bukan tk.Variable
        self.prev_fee = 0
        self.global_opt = None   # (fee, armada) hasil "hitung global optima"
        self.t0 = 0.0
        self.slept = 0.0
        self.reference_armada = None   # armada hasil Generate, tidak pernah diubah
        self.reference_fee = 0
        self.fee_sebelum_ga = 0
        self.initial_armadas = []      # populasi GA gen 0, terurut peringkat
        self.final_armadas = []        # populasi GA akhir, terurut peringkat
        self.last_ga_history = None



        form = ttk.Frame(self, padding=8)
        form.pack(fill="x")
        for i, (key, label, default) in enumerate(HC_FIELDS):
            ttk.Label(form, text=label).grid(row=0, column=2 * i)
            self.vars[key] = tk.StringVar(value=default)
            ttk.Entry(form, width=6, textvariable=self.vars[key]).grid(row=0, column=2 * i + 1, padx=(2, 10))
        ttk.Checkbutton(form, text="Stochastic", variable=self.stochastic).grid(row=0, column=2 * len(HC_FIELDS))

        algo_row = ttk.Frame(self, padding=(8, 0, 8, 6))
        algo_row.pack(fill="x")
        ttk.Label(algo_row, text="Algoritma").pack(side="left")
        for value, text in (("hill", "Hill Climbing"), ("sa", "Simulated Annealing")):
            ttk.Radiobutton(algo_row, text=text, value=value, variable=self.algo).pack(side="left", padx=(8, 0))
        for key, label, default in SA_FIELDS:
            ttk.Label(algo_row, text=label).pack(side="left", padx=(16, 2))
            self.vars[key] = tk.StringVar(value=default)
            ttk.Entry(algo_row, width=6, textvariable=self.vars[key]).pack(side="left")
        ga_row = ttk.Frame(self, padding=(8, 0, 8, 6))
        ga_row.pack(fill="x")
        ttk.Label(ga_row, text="Genetic Algorithm").pack(side="left")
        for key, label, default in GA_FIELDS:
            ttk.Label(ga_row, text=label).pack(side="left", padx=(16, 2))
            self.vars[key] = tk.StringVar(value=default)
            ttk.Entry(ga_row, width=6, textvariable=self.vars[key]).pack(side="left")


        buttons = ttk.Frame(self, padding=(8, 0))
        buttons.pack(fill="x")
        self.generate_btn = ttk.Button(buttons, text="Generate", command=self.generate)
        self.generate_btn.pack(side="left")

        #self.run_btn = ttk.Button(buttons, text="Jalankan Hill Climbing", command=self.run, state="disabled")
        self.run_btn = ttk.Button(buttons, text="Jalankan", command=self.run, state="disabled")
        self.run_btn.pack(side="left", padx=8)
        self.run_ga_btn = ttk.Button(buttons, text="Jalankan GA", command=self.run_ga, state="disabled")
        self.run_ga_btn.pack(side="left", padx=4)
        self.plot_btn = ttk.Button(buttons, text="Grafik Konvergensi GA", command=self.show_plot, state="disabled")
        self.plot_btn.pack(side="left", padx=4)
        self.batch_exp_btn = ttk.Button(buttons, text="18 Eksperimen GA", command=self.run_batch_exp)
        self.batch_exp_btn.pack(side="left", padx=4)

        ttk.Label(buttons, text="Jeda/iterasi").pack(side="left", padx=(12, 4))
        ttk.Scale(buttons, from_=0, to=MAX_DELAY_MS, length=160, command=self._on_delay).pack(side="left")
        self.delay_label = ttk.Label(buttons, text="0 ms", width=8)
        self.delay_label.pack(side="left")

        self.status = tk.StringVar(value="Klik Generate dulu.")
        ttk.Label(buttons, textvariable=self.status).pack(side="left", padx=8)

        #button global maximum
        opt_row = ttk.Frame(self, padding=(8, 2))
        opt_row.pack(fill="x")
        ttk.Label(opt_row, text="Sampel acak").pack(side="left")
        self.vars["samples"] = tk.StringVar(value="5000")
        ttk.Entry(opt_row, width=8, textvariable=self.vars["samples"]).pack(side="left", padx=(4, 8))
        self.opt_btn = ttk.Button(opt_row, text="Hitung global optima", command=self.hitung_optima, state="disabled")
        self.opt_btn.pack(side="left")
        self.opt_var = tk.StringVar(value="Global optima: -")
        ttk.Label(opt_row, textvariable=self.opt_var, font=("Segoe UI", 10, "bold")).pack(side="left", padx=12)


        # panel inspeksi populasi GA (muncul setelah GA selesai)
        self.inspect_frame = ttk.LabelFrame(self, text="Inspeksi Populasi GA", padding=(8, 4))
        ttk.Label(self.inspect_frame, text="Tahap:").pack(side="left", padx=2)
        self.stage_var = tk.StringVar(value="final")
        for value, text in (("reference", "Armada Awal"), ("initial", "State Awal (Gen 0)"), ("final", "State Akhir")):
            ttk.Radiobutton(self.inspect_frame, text=text, variable=self.stage_var, value=value,
                            command=self._refresh_armada_dropdown).pack(side="left", padx=4)
        ttk.Label(self.inspect_frame, text="|  Armada:").pack(side="left", padx=(10, 4))
        self.armada_selector = ttk.Combobox(self.inspect_frame, width=52, state="readonly")
        self.armada_selector.pack(side="left", padx=4)
        self.armada_selector.bind("<<ComboboxSelected>>", self._on_armada_selected)

        # papan kapal yang bisa di-scroll
        self.boards = ttk.Frame(self, padding=8)
        self.boards.pack(fill="both", expand=True)
        self.boards_canvas = tk.Canvas(self.boards, bg=self.cget("bg"), highlightthickness=0, borderwidth=0)
        boards_scroll = ttk.Scrollbar(self.boards, orient="vertical", command=self.boards_canvas.yview)
        self.boards_canvas.configure(yscrollcommand=boards_scroll.set)
        boards_scroll.pack(side="right", fill="y")
        self.boards_canvas.pack(side="left", fill="both", expand=True)
        self.inner_boards = ttk.Frame(self.boards_canvas)
        self.boards_window = self.boards_canvas.create_window((0, 0), window=self.inner_boards, anchor="nw")
        self.inner_boards.bind("<Configure>",
                               lambda e: self.boards_canvas.configure(scrollregion=self.boards_canvas.bbox("all")))
        self.boards_canvas.bind("<Configure>",
                                lambda e: self.boards_canvas.itemconfig(
                                    self.boards_window, width=max(e.width, self.inner_boards.winfo_reqwidth())))
        self.bind_all("<MouseWheel>", self._on_mousewheel)

        self.outside = tk.StringVar()
        ttk.Label(self, textvariable=self.outside, padding=(8, 0), wraplength=700).pack(anchor="w")
        self.log = tk.Text(self, height=8, state="disabled")
        self.log.pack(fill="x", padx=8, pady=8)

    # ---- util
    def _int(self, key):
        return int(self.vars[key].get())
    def _float(self, key):
        return float(self.vars[key].get().replace(",", "."))


    def _on_delay(self, value):
        self.delay_ms = int(float(value))
        self.delay_label.config(text=f"{self.delay_ms} ms")
    def _on_mousewheel(self, event):
        if str(event.widget).startswith(str(self.boards)):
            self.boards_canvas.yview_scroll(-2 if event.delta > 0 else 2, "units")


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
        self.reference_armada = copy.deepcopy(self.armada)
        self.reference_fee = self.armada.calculate_armada_shipping_fee()
        self.initial_armadas, self.final_armadas = [], []
        self.inspect_frame.pack_forget()
        self.build(self.armada)
        self.render(self.armada)
        self.global_opt = None
        self.opt_var.set("Global optima: -")
        self._set_busy(False)
        self.status.set(f"Armada siap | fee awal: {self.reference_fee}")
        self.write(f"Generate: {self._int('n_vehicles')} kendaraan, {self._int('n_ships')} kapal (fee awal {self.reference_fee})")

    
    def hitung_optima(self):
        """Global optima = fee terbaik dari ribuan state acak murni (tanpa move / switch / rotate)."""
        if self.armada is None or self.running:
            return
        try:
            n = self._int("samples")
            if n < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input tidak valid", "Jumlah sampel harus bilangan bulat >= 1.")
            return
        self.running = True
        for b in (self.run_btn, self.opt_btn):        # kalau sudah ada: tambahkan self.reset_btn, self.best_btn
            b.config(state="disabled")
            self.running = True
            self._set_busy(True)

        self.t0 = time.perf_counter()
        self.opt_var.set(f"Global optima: menghitung 0/{n} ...")
        threading.Thread(target=self._opt_worker, args=(n,), daemon=True).start()
        self.after(30, self._poll)

    def _opt_worker(self, n):
        try:
            fee, armada = global_optima(self.armada, n, lambda i, best: self.q.put(("opt_progress", i, n, best)))
            self.q.put(("opt_done", fee, armada, n))
        except Exception as e:
            self.q.put(("error", repr(e)))
###########################
    def run(self):
        if self.armada is None or self.running:
            return
        algo = self.algo.get()
        try:
            if algo == "sa":
                T, cooling = self._float("temp"), self._float("cooling")
                if T <= 0.1 or not 0 < cooling < 1:
                    raise ValueError
                params = (T, cooling)
            else:
                params = (self._int("sideways"), self._int("neighbors"), self._int("restarts"), self.stochastic.get())
        except ValueError:
            messagebox.showerror("Input tidak valid",
                                 "Hill Climbing: parameter harus bilangan bulat.\n"
                                 "Simulated Annealing: T > 0.1 dan 0 < cooling rate < 1.")
            return
        self.inspect_frame.pack_forget()
        self.running = True
        self._set_busy(True)

        self.t0 = time.perf_counter()
        self.slept = 0.0

        threading.Thread(target=self._worker, args=(algo, params), daemon=True).start()
        self.after(30, self._poll)

    def _worker(self, algo, params):
        def progress(it, fee, armada, extra=""):
            self.q.put(("progress", it, fee, armada, extra))
            if self.delay_ms:
                time.sleep(self.delay_ms / 1000)
                self.slept += self.delay_ms / 1000

        try:
            if algo == "sa":
                T, cooling = params
                result = simulated_annealing(self.armada, T, cooling).execute(progress)
            else:
                sideways, neighbors, restarts, stochastic = params
                if restarts > 0:
                    result = random_restart(self.armada, sideways, neighbors, restarts, progress, stochastic)
                else:
                    result = hill_climbing(self.armada, sideways, neighbors, progress, stochastic)
            self.q.put(("done", result))
        except Exception as e:
            self.q.put(("error", repr(e)))
    def run_ga(self):
        if self.armada is None or self.running:
            return
        try:
            pop_size, generations = self._int("pop_size"), self._int("generations")
            if pop_size < 2 or generations < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input tidak valid", "Populasi GA >= 2 dan generasi GA >= 1 (bilangan bulat).")
            return
        self.inspect_frame.pack_forget()
        self.running = True
        self._set_busy(True)
        self.t0 = time.perf_counter()
        self.slept = 0.0
        self.fee_sebelum_ga = self.armada.calculate_armada_shipping_fee()
        self.initial_armadas, self.final_armadas = [], []
        self.write(f"--- Mulai Genetic Algorithm: populasi {pop_size}, generasi {generations} (fee awal {self.fee_sebelum_ga}) ---")
        threading.Thread(target=self._worker_ga, args=(copy.deepcopy(self.armada), pop_size, generations), daemon=True).start()
        self.after(30, self._poll)

    def _worker_ga(self, armada_input, pop_size, generations):
        def progress_ga(gen, max_fee, avg_fee, best_armada):
            self.q.put(("progress_ga", gen, max_fee, avg_fee, best_armada))
            if self.delay_ms:
                time.sleep(self.delay_ms / 1000)
                self.slept += self.delay_ms / 1000

        try:
            res = run_genetic_algorithm(armada_input, pop_size=pop_size, generations=generations, on_iteration=progress_ga)
            self.q.put(("done_ga", res))
        except Exception as e:
            self.q.put(("error", repr(e)))

    def show_plot(self):
        h = self.last_ga_history
        if h is None:
            messagebox.showinfo("Grafik Konvergensi", "Belum ada riwayat GA yang dijalankan.")
            return
        win = tk.Toplevel(self)
        win.title("Kurva Konvergensi GA")
        fig = Figure(figsize=(8, 5))
        ax = fig.add_subplot(111)
        ax.plot(h["history_max"], label="Fitness Maksimum (Best)", linewidth=2)
        ax.plot(h["history_avg"], label="Rata-rata Populasi (Avg)", linestyle="--", linewidth=1.8)
        ax.set_title(f"Kurva Konvergensi GA (Pop: {h['pop_size']}, Gen: {h['generations']}, Best Fee: {h['best_fitness']:.0f})")
        ax.set_xlabel("Generasi")
        ax.set_ylabel("Shipping Fee (Fitness)")
        ax.legend()
        ax.grid(True, linestyle=":", alpha=0.6)
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def run_batch_exp(self):
        if self.running:
            return
        self.inspect_frame.pack_forget()
        self.running = True
        self._set_busy(True)
        self.t0 = time.perf_counter()
        self.status.set("Menjalankan 18 eksperimen GA di background...")
        self.write("--- Mulai 18 skenario eksperimen GA (Exp 1 dan Exp 2) ---")
        threading.Thread(target=self._worker_batch_exp, daemon=True).start()
        self.after(30, self._poll)

    def _worker_batch_exp(self):
        try:
            run_benchmark_experiments(on_progress=lambda msg: self.q.put(("exp_log", msg)), output_dir="output")
            self.q.put(("exp_done",))
        except Exception as e:
            self.q.put(("error", repr(e)))

    # ---- inspeksi populasi GA
    def _refresh_armada_dropdown(self):
        stage = self.stage_var.get()
        if stage == "reference":
            options = [f"Armada Awal - Fee {self.reference_fee}"] if self.reference_armada is not None else []
        else:
            armadas = self.initial_armadas if stage == "initial" else self.final_armadas
            others = self.final_armadas if stage == "initial" else self.initial_armadas
            options = []
            for i, a in enumerate(armadas):
                label = f"Peringkat {i + 1}{' (Terbaik)' if i == 0 else ''} - Fee {a.calculate_armada_shipping_fee()}"
                if i < len(others):
                    label += f" (vs {'Final' if stage == 'initial' else 'Gen 0'}: {others[i].calculate_armada_shipping_fee()})"
                options.append(label)
        prev = self.armada_selector.current()
        self.armada_selector["values"] = options
        if options:
            self.armada_selector.current(prev if 0 <= prev < len(options) else 0)
            self._on_armada_selected()

    def _on_armada_selected(self, event=None):
        stage = self.stage_var.get()
        idx = self.armada_selector.current()
        if idx < 0:
            return
        if stage == "reference":
            armada, nama = self.reference_armada, "Armada Awal"
        else:
            armadas = self.initial_armadas if stage == "initial" else self.final_armadas
            if idx >= len(armadas):
                return
            armada = armadas[idx]
            nama = f"Peringkat {idx + 1} ({'State Awal Gen 0' if stage == 'initial' else 'State Akhir'})"
        if armada is None:
            return
        self.render(armada)   # hanya ditampilkan; self.armada (state awal untuk semua run) tidak diubah
        self.status.set(f"Menampilkan: {nama} | Fee: {armada.calculate_armada_shipping_fee()} | Fee awal: {self.reference_fee}")


    def _poll(self):
        last = None
        last_ga = None
        while True:
            try:
                kind, *data = self.q.get_nowait()
            except queue.Empty:
                break
            if kind == "progress":
                it, fee, armada, extra = data
                self._log_iteration(it, fee, extra)
                last = (it, fee, armada, extra)
            elif kind == "error":
                messagebox.showerror("Error", data[0])
                self._finish()
                return
            elif kind == "done":
                armada, fee, history = data[0]
                elapsed = time.perf_counter() - self.t0 - self.slept
                self.render(armada)
                self.status.set(f"Selesai | fee {history[0]} -> {fee} | {elapsed:.2f} s")
                self.write(f"Selesai: fee {history[0]} -> {fee} ({len(history) - 1} iterasi), "
                           f"waktu {elapsed:.2f} s (di luar jeda)")
                self._finish()
                return
            elif kind == "opt_progress":
                i, n, best = data
                self.opt_var.set(f"Global optima: menghitung {i}/{n} | terbaik {best}")
            elif kind == "opt_done":
                fee, armada, n = data
                elapsed = time.perf_counter() - self.t0
                self.global_opt = (fee, armada)
                self.opt_var.set(f"Global optima: {fee}")
                self.render(armada)
                self.status.set(f"Global optima: {fee} | {n} sampel | {elapsed:.2f} s")
                self.write(f"Global optima (terbaik dari {n} state acak): {fee}, waktu {elapsed:.2f} s")
                self._finish()
                return
            elif kind == "progress_ga":
                gen, max_fee, avg_fee, armada = data
                self.write(f"Generasi {gen}: best {max_fee:.0f} | avg {avg_fee:.1f}")
                last_ga = (gen, max_fee, avg_fee, armada)
            elif kind == "done_ga":
                res = data[0]
                elapsed = time.perf_counter() - self.t0 - self.slept
                self.initial_armadas = res["initial_armadas"]
                self.final_armadas = res["final_armadas"]
                self.last_ga_history = {k: res[k] for k in ("history_max", "history_avg", "generations", "pop_size", "best_fitness")}
                self.inspect_frame.pack(fill="x", padx=8, pady=(4, 0), before=self.boards)
                self.stage_var.set("final")
                self._refresh_armada_dropdown()
                gain = res["best_fitness"] - self.fee_sebelum_ga
                self.status.set(f"GA selesai | fee {self.fee_sebelum_ga} -> {res['best_fitness']:.0f} ({gain:+.0f}) | {elapsed:.2f} s")
                self.write(f"Selesai GA: fee {self.fee_sebelum_ga} -> {res['best_fitness']:.0f} ({gain:+.0f}), "
                           f"{res['generations']} generasi, waktu {elapsed:.2f} s (di luar jeda)")
                self._finish()
                return
            elif kind == "exp_log":
                self.write(data[0])
                if "Run ke-" in data[0]:
                    self.status.set(data[0].strip())
            elif kind == "exp_done":
                dur = time.perf_counter() - self.t0
                self.status.set(f"18 eksperimen GA selesai ({dur:.1f} s) -> folder output/")
                self.write(f"--- 18 eksperimen GA selesai dalam {dur:.2f} s. CSV, TXT, dan PNG tersimpan di output/ ---")
                self._finish()
                messagebox.showinfo("Eksperimen selesai", f"18 eksperimen GA selesai dalam {dur:.2f} detik.\nHasil di folder output/.")
                return

        if last:  # delay kecil bikin banyak iterasi menumpuk; gambar yang terbaru saja
            it, fee, armada, extra = last
            self.status.set(f"Iterasi {it} | fee {fee} {extra} | {time.perf_counter() - self.t0 - self.slept:.1f} s")
            self.render(armada)
        if last_ga:  # gambar generasi terbaru saja
            gen, max_fee, avg_fee, armada = last_ga
            self.status.set(f"Generasi {gen} | best {max_fee:.0f} | avg {avg_fee:.1f} | {time.perf_counter() - self.t0 - self.slept:.1f} s")
            self.render(armada)

        self.after(30, self._poll)



    def _log_iteration(self, it, fee, extra=""):
        if it == 0:
            self.write(f"--- mulai dari fee {fee} {extra}".rstrip())
        else:
            self.write(f"Iterasi {it}: fee {fee} ({fee - self.prev_fee:+d}) {extra}".rstrip())
        self.prev_fee = fee


    def _set_busy(self, busy):
        """Satu tempat untuk mengatur semua tombol. Tombol algoritma baru aktif kalau armada sudah ada."""
        has_armada = self.armada is not None
        state = lambda ok: "normal" if ok and not busy else "disabled"
        self.generate_btn.config(state=state(True))
        self.batch_exp_btn.config(state=state(True))
        for b in (self.run_btn, self.run_ga_btn, self.opt_btn):
            b.config(state=state(has_armada))
        self.plot_btn.config(state=state(self.last_ga_history is not None))

    def _finish(self):
        self.running = False
        self._set_busy(False)


    # ---- gambar
    def build(self, armada):
        """Buat label + canvas tiap kapal sekali; render() cuma menggambar ulang isinya."""
        for child in self.inner_boards.winfo_children():
            child.destroy()
        self.canvases, self.infos = {}, {}
        self.colors = {v.id: self._color(i) for i, v in enumerate(armada.list_all_vehicles)}
        for ship in sorted(armada.ship_list, key=lambda s: s.id):
            info = tk.StringVar()
            ttk.Label(self.inner_boards, textvariable=info).pack(anchor="w")
            canvas = tk.Canvas(self.inner_boards, width=ship.l * CELL + 1, height=ship.w * CELL + 1,
                               bg="#f4f6f8", highlightthickness=0)
            canvas.pack(anchor="w", pady=(0, 8))
            self.canvases[ship.id], self.infos[ship.id] = canvas, info
        self.boards_canvas.yview_moveto(0.0)

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

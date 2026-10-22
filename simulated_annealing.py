from starter import Vehicle, Ship, Armada, armada
import math
import random
import copy
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class simulated_annealing:
    all_duration = []
    all_stuck_local_frequency = []
    all_shipping_fee_gain = []

    def __init__(self, armada: Armada, T: float, cooling_rate: float):
        self.armada_awal = copy.deepcopy(armada)
        self.armada = copy.deepcopy(armada)
        self.best_armada = copy.deepcopy(armada)
        self.T = T
        self.initial_T = T
        self.cooling_rate = cooling_rate
        self.best_shipping_fee = self.armada.calculate_armada_shipping_fee()

        self.duration = 0.0
        self.stuck_local_frequency = 0
        self.shipping_fee_iteration = []
        self.history_acceptance_rate = []
        self.history_acceptance_step = []
        self.history_shipping_fee = [self.armada.calculate_armada_shipping_fee()]
        self.total_iterations = 0

    def move_success(self, neighbor: Armada, current_iter: int) -> bool:
        if neighbor is None:
            return False

        delta = neighbor.calculate_armada_shipping_fee() - self.armada.calculate_armada_shipping_fee()
        if delta >= 0:
            self.armada = neighbor
            self.T = self.T * self.cooling_rate
            return True
        else:
            prob = math.exp(delta / self.T)
            self.history_acceptance_rate.append(prob)
            self.history_acceptance_step.append(current_iter)
            if random.random() < prob:
                self.armada = neighbor
                self.T = self.T * self.cooling_rate
                return True
            else:
                self.stuck_local_frequency += 1
                self.T = self.T * self.cooling_rate
                return False

    def find_random_neighbour(self) -> Armada:
        move_found = False
        neighbour = copy.deepcopy(self.armada)
        max_iteration = 500
        iteration = 0
        while iteration <= max_iteration:
            iteration += 1
            random_num = random.randint(1, 3)
            match random_num:
                case 1:
                    if neighbour.switch_vehicle_success():
                        move_found = True
                case 2:
                    chosen_ship = random.choice(list(neighbour.ship_list))
                    if len(chosen_ship.list_vehicles_in_ship) > 0:
                        chosen_vehicle = random.choice(list(chosen_ship.list_vehicles_in_ship))
                        if chosen_ship.move_vehicle_success(chosen_vehicle):
                            move_found = True
                case 3:
                    chosen_ship = random.choice(list(neighbour.ship_list))
                    if len(chosen_ship.list_vehicles_in_ship) > 0:
                        chosen_vehicle = random.choice(list(chosen_ship.list_vehicles_in_ship))
                        if chosen_ship.change_orientation_success(chosen_vehicle):
                            move_found = True

            if move_found:
                return neighbour
        return None

    def execute(self, on_iteration=None):
        start_time = time.time()
        iteration = 0
        max_iteration = 100
        initial_shipping_fee = self.armada.calculate_armada_shipping_fee()

        step = 0
        if on_iteration:
            on_iteration(0, initial_shipping_fee, self.armada, f"T={self.T:.2f}")

        while iteration <= max_iteration and self.T > 0.1:
            iteration += 1
            self.total_iterations += 1
            neighbour = self.find_random_neighbour()

            if self.move_success(neighbour, self.total_iterations):
                iteration = 0
                step += 1
                fee = self.armada.calculate_armada_shipping_fee()
                self.shipping_fee_iteration.append(fee)
                self.history_shipping_fee.append(fee)
                if fee > self.best_shipping_fee:
                    self.best_armada, self.best_shipping_fee = copy.deepcopy(self.armada), fee

                if on_iteration:
                    on_iteration(step, fee, self.armada, f"T={self.T:.2f}")
            else:
                self.history_shipping_fee.append(self.armada.calculate_armada_shipping_fee())

        gain = self.best_shipping_fee - initial_shipping_fee
        simulated_annealing.all_shipping_fee_gain.append(gain)
        simulated_annealing.all_stuck_local_frequency.append(self.stuck_local_frequency)
        self.duration = time.time() - start_time
        simulated_annealing.all_duration.append(self.duration)
        return self.best_armada, self.best_shipping_fee, self.history_shipping_fee

    def plot_objective_function(self, run_id: int, output_dir: str = "output"):
        os.makedirs(output_dir, exist_ok=True)
        plt.figure(figsize=(10, 5))

        iterations = range(len(self.history_shipping_fee))
        plt.plot(iterations, self.history_shipping_fee, label="Current State Fee", color="#1f77b4", linewidth=1.5)
        plt.axhline(y=self.best_shipping_fee, color="#d62728", linestyle="--",
                    label=f"Best Fee ({self.best_shipping_fee})")

        plt.title(f"Simulated Annealing - Objective Function vs Iterations (Run {run_id})\n"
                  f"Initial Fee: {self.history_shipping_fee[0]} | Final/Best Fee: {self.best_shipping_fee} | Duration: {self.duration:.3f}s")
        plt.xlabel("Iterasi")
        plt.ylabel("Objective Function (Total Shipping Fee)")
        plt.legend(loc="lower right")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.tight_layout()

        filepath = os.path.join(output_dir, f"SA_run{run_id}_objective_function.png")
        plt.savefig(filepath, dpi=300)
        plt.close()

    def plot_acceptance_probability(self, run_id: int, output_dir: str = "output"):
        os.makedirs(output_dir, exist_ok=True)
        plt.figure(figsize=(10, 5))

        if len(self.history_acceptance_rate) > 0:
            plt.plot(self.history_acceptance_step, self.history_acceptance_rate,
                     color="#ff7f0e", alpha=0.5, linewidth=1, label=r"$e^{\Delta E / T}$ Trajectory")
            plt.scatter(self.history_acceptance_step, self.history_acceptance_rate,
                        color="#d62728", s=18, zorder=3, label=r"Titik Evaluasi ($\Delta E < 0$)")
        else:
            plt.text(0.5, 0.5, "Tidak ada langkah dengan Delta E < 0",
                     horizontalalignment="center", verticalalignment="center", transform=plt.gca().transAxes)

        plt.title(f"Simulated Annealing - Acceptance Probability ($e^{{\\Delta E / T}}$) vs Iterations (Run {run_id})\n"
                  f"Frekuensi Stuck di Local Optima: {self.stuck_local_frequency}")
        plt.xlabel("Iterasi")
        plt.ylabel(r"Acceptance Probability ($e^{\Delta E / T}$)")
        plt.ylim(-0.05, 1.05)
        plt.legend(loc="upper right")
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.tight_layout()

        filepath = os.path.join(output_dir, f"SA_run{run_id}_boltzmann_probability.png")
        plt.savefig(filepath, dpi=300)
        plt.close()

    @staticmethod
    def plot_armada_state(armada_obj: Armada, title: str, filename: str, output_dir: str = "output"):
        os.makedirs(output_dir, exist_ok=True)
        ships = sorted(list(armada_obj.ship_list), key=lambda s: s.id)
        n_ships = len(ships)

        fig, axes = plt.subplots(1, n_ships, figsize=(7 * n_ships, 6))
        if n_ships == 1:
            axes = [axes]

        cmap = plt.colormaps.get_cmap("tab20")
        all_vehicles = sorted(armada_obj.list_all_vehicles, key=lambda v: int(v.id[1:]) if v.id[1:].isdigit() else v.id)
        color_map = {v.id: cmap(i % 20) for i, v in enumerate(all_vehicles)}

        placed_ids = set()

        for ax, ship in zip(axes, ships):
            ax.set_xlim(0, ship.l)
            ax.set_ylim(0, ship.w)
            ax.set_xticks(range(0, ship.l + 1))
            ax.set_yticks(range(0, ship.w + 1))
            ax.grid(True, which="both", color="gray", linestyle="-", linewidth=0.5)
            ax.set_aspect("equal")
            ax.invert_yaxis()

            for v in ship.list_vehicles_in_ship:
                placed_ids.add(v.id)
                x_row, y_col = v.coor
                true_w = v.w if v.orientation == "vertical" else v.l
                true_l = v.l if v.orientation == "vertical" else v.w

                rect = patches.Rectangle(
                    (y_col, x_row), true_l, true_w,
                    linewidth=1.5, edgecolor="black", facecolor=color_map[v.id], alpha=0.85
                )
                ax.add_patch(rect)
                ax.text(
                    y_col + true_l / 2, x_row + true_w / 2,
                    f"{v.id}\n(${v.shipping_fee}, {v.weight}t)",
                    ha="center", va="center", fontsize=7.5, fontweight="bold", color="black"
                )

            ship_fee = ship.calculate_shipping_fee()
            ship_weight = ship.calculate_ship_weight()
            ax.set_title(
                f"Kapal {ship.id} (Dimensi: {ship.w}x{ship.l})\n"
                f"Muatan: {ship_weight}/{ship.max_capacity} | Tarif: {ship_fee} | Jml Kendaraan: {len(ship.list_vehicles_in_ship)}",
                fontsize=10, fontweight="bold"
            )
            ax.set_xlabel("Length (Y)")
            ax.set_ylabel("Width (X)")

        unplaced = [f"{v.id}(${v.shipping_fee})" for v in all_vehicles if v.id not in placed_ids]
        unplaced_text = ", ".join(unplaced) if unplaced else "Tidak ada (Semua terangkut)"

        max_char_per_line = 110
        wrapped_unplaced = "\n".join([unplaced_text[i:i+max_char_per_line] for i in range(0, len(unplaced_text), max_char_per_line)])

        total_fee = armada_obj.calculate_armada_shipping_fee()
        fig.suptitle(f"{title}\nTotal Armada Shipping Fee (Value): {total_fee}", fontsize=13, fontweight="bold", y=0.98)
        fig.text(0.5, 0.02, f"Kendaraan di Luar Kapal ({len(unplaced)}): {wrapped_unplaced}",
                 ha="center", va="bottom", fontsize=8.5,
                 bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#ced4da"))

        plt.tight_layout(rect=[0, 0.10, 1, 0.90])
        filepath = os.path.join(output_dir, filename)
        plt.savefig(filepath, dpi=300)
        plt.close()

    def save_all_plots(self, run_id: int, output_dir: str = "output"):
        self.plot_objective_function(run_id, output_dir)
        self.plot_acceptance_probability(run_id, output_dir)
        self.plot_armada_state(
            self.armada_awal,
            title=f"Simulated Annealing - Initial State (Run {run_id})",
            filename=f"SA_run{run_id}_initial_state.png",
            output_dir=output_dir
        )
        self.plot_armada_state(
            self.best_armada,
            title=f"Simulated Annealing - Final State (Run {run_id})",
            filename=f"SA_run{run_id}_final_state.png",
            output_dir=output_dir
        )


def plot_summary_all_runs(sa_instances: list[simulated_annealing], output_dir: str = "output"):
    os.makedirs(output_dir, exist_ok=True)

    plt.figure(figsize=(10, 5))
    colors = ["#1f77b4", "#2ca02c", "#d62728"]
    for idx, sa in enumerate(sa_instances, start=1):
        plt.plot(sa.history_shipping_fee, label=f"Run {idx} (Best: {sa.best_shipping_fee}, Time: {sa.duration:.2f}s)",
                 color=colors[(idx - 1) % len(colors)], linewidth=1.5)

    plt.title("Simulated Annealing - Perbandingan Objective Function (3 Runs)")
    plt.xlabel("Iterasi")
    plt.ylabel("Objective Function (Total Shipping Fee)")
    plt.legend()
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "SA_summary_objective_comparison.png"), dpi=300)
    plt.close()

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    runs = [f"Run {i+1}" for i in range(len(sa_instances))]
    x = np.arange(len(runs))
    width = 0.35

    initial_fees = [sa.history_shipping_fee[0] for sa in sa_instances]
    best_fees = [sa.best_shipping_fee for sa in sa_instances]
    stuck_freqs = [sa.stuck_local_frequency for sa in sa_instances]
    durations = [sa.duration for sa in sa_instances]

    axes[0].bar(x - width/2, initial_fees, width, label="Initial Fee", color="#aec7e8")
    axes[0].bar(x + width/2, best_fees, width, label="Final/Best Fee", color="#1f77b4")
    axes[0].set_title("Initial vs Final Shipping Fee")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(runs)
    axes[0].set_ylabel("Shipping Fee")
    axes[0].legend()
    axes[0].grid(axis="y", linestyle=":", alpha=0.6)

    axes[1].bar(runs, stuck_freqs, color="#ffbb78", edgecolor="#ff7f0e")
    axes[1].set_title("Frekuensi Stuck di Local Optima")
    axes[1].set_ylabel("Jumlah Stuck")
    axes[1].grid(axis="y", linestyle=":", alpha=0.6)
    for i, v in enumerate(stuck_freqs):
        axes[1].text(i, v + max(stuck_freqs)*0.02, str(v), ha="center", fontweight="bold")

    axes[2].bar(runs, durations, color="#98df8a", edgecolor="#2ca02c")
    axes[2].set_title("Durasi Proses Pencarian (Detik)")
    axes[2].set_ylabel("Waktu (s)")
    axes[2].grid(axis="y", linestyle=":", alpha=0.6)
    for i, v in enumerate(durations):
        axes[2].text(i, v + max(durations)*0.02, f"{v:.3f}s", ha="center", fontweight="bold")

    plt.suptitle("Ringkasan Eksperimen Simulated Annealing (3x Run)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "SA_summary_metrics.png"), dpi=300)
    plt.close()


if __name__ == "__main__":
    OUTPUT_FOLDER = "output"
    T_INITIAL = 1000.0
    COOLING_RATE = 0.95
    NUM_RUNS = 3

    sa_runs = []
    print("=== MENJALANKAN EKSPERIMEN SIMULATED ANNEALING (3 KALI RUN) ===")

    for run in range(1, NUM_RUNS + 1):
        sa = simulated_annealing(armada=armada, T=T_INITIAL, cooling_rate=COOLING_RATE)
        best_armada, best_fee, history_fee = sa.execute()
        sa.save_all_plots(run_id=run, output_dir=OUTPUT_FOLDER)
        sa_runs.append(sa)

        print(f"\n[Run {run}]")
        print(f"  - Initial Shipping Fee : {history_fee[0]}")
        print(f"  - Final/Best Fee       : {best_fee}")
        print(f"  - Total Iterasi        : {sa.total_iterations}")
        print(f"  - Frekuensi Stuck      : {sa.stuck_local_frequency} kali")
        print(f"  - Durasi Pencarian     : {sa.duration:.4f} detik")

    plot_summary_all_runs(sa_runs, output_dir=OUTPUT_FOLDER)
    print(f"\nSeluruh grafik telah berhasil disimpan ke dalam folder '{OUTPUT_FOLDER}/'!")
from starter import *
import random as rd
import copy
import random as rd
import copy
import os
import time
import colorsys
import textwrap
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle

# hillclimb, armada dilakukan inisialisasi awal ->  switching, move vehicle -> hitung neighbor, 
# -> steepest pindah ke neighbor kalo ada yang lebih baik
# -> sideways pindah ke neighbor kalo sama atau lebih baik
# -> random restart -> bisa di restart


# randomize ukuran vehicle dengan ukuran yang sudah ada(misal 2x2, 3x4, 4x2, 5x2, dll) atau bisa di assign sendiri
# ukuran ship juga akan di randomize dengan ukuran yang sudah ada (50x50, 50x25, dll) atau bisa di assign sendiri
def get_neighbor(armada:Armada):
    neighbor = copy.deepcopy(armada)

    while True:
        gerakan = rd.choice(["switch", "move", "rotate"])
        if gerakan == "switch":
                if neighbor.switch_vehicle_success():
                    return neighbor
        else:
            ship = rd.choice(list(neighbor.ship_list))
            if ship.list_vehicles_in_ship:
                vehicle = rd.choice(list(ship.list_vehicles_in_ship))
                if gerakan == "move": 
                    if ship.move_vehicle_success(vehicle):
                        return neighbor
                else:
                    if ship.change_orientation_success(vehicle):
                        return neighbor
    
def hill_climbing(armada, max_sideways=0, n_neighbors=50, on_iteration = None, stochastic = False):
    fee_sekarang = armada.calculate_armada_shipping_fee()
    sideways = 0
    history = [fee_sekarang]

    if on_iteration:
        on_iteration(0,fee_sekarang, armada)
    while True:
        fee_terbaik = -1
        kandidat = []
        kandidat_better = []

        for _ in range(n_neighbors):
            tetangga = get_neighbor(armada)
            f = tetangga.calculate_armada_shipping_fee()
            if f>fee_sekarang:
                kandidat_better.append((f,tetangga))
            if f > fee_terbaik:
                fee_terbaik = f
                kandidat = [tetangga]
            elif f == fee_terbaik:
                kandidat.append(tetangga)

        if fee_terbaik > fee_sekarang:
            if stochastic:
                fee_sekarang,armada = rd.choice(kandidat_better)
            else:
                armada = rd.choice(kandidat)
                fee_sekarang = fee_terbaik
            sideways = 0
        elif fee_terbaik == fee_sekarang and sideways <  max_sideways:
            armada = rd.choice(kandidat)
            sideways += 1
        else:
            break
        history.append(fee_sekarang)
        if on_iteration:
            on_iteration(len(history) - 1, fee_sekarang, armada)
    return armada, fee_sekarang, history


def new_random_armada(armada):
    ships = set()
    for i in armada.ship_list:
        ships.add(Ship(i.w,i.l,i.max_capacity, i.id))
    vehicles = copy.deepcopy(armada.list_all_vehicles)
    for i in vehicles:
        i.coor = [-1,-1]
    fresh = Armada(ships,vehicles)
    fresh.random_state_armada(vehicles)
    return fresh

def random_restart(armada, max_sideways = 0, n_neighbor = 50, max_restart=100, on_iteration = None, stochastic=False, histories = None):
    best,best_fee,best_history = hill_climbing(armada, max_sideways, n_neighbor, on_iteration, stochastic)
    if histories is not None:
        histories.append(best_history)
    for _ in range(max_restart):
        hasil, fee, history = hill_climbing(new_random_armada(armada), max_sideways, n_neighbor, on_iteration, stochastic)
        if histories is not None:
            histories.append(history)
        if fee > best_fee:
            best_fee = fee
            best = hasil
            best_history = history
    return best, best_fee, best_history


def export_run_image(filename, title, initial_armada, final_armada, history, info, restart_points=None):
    """Simpan 1 gambar: state awal & akhir tiap kapal, plot fee vs iterasi, dan ringkasan run."""
    initial_ships = sorted(initial_armada.ship_list, key=lambda s: s.id)
    final_ships = sorted(final_armada.ship_list, key=lambda s: s.id)
    n = len(initial_ships)

    colors = {}
    for i, v in enumerate(initial_armada.list_all_vehicles):
        colors[v.id] = colorsys.hsv_to_rgb((i * 0.618033988) % 1, 0.45, 0.97)

    fig = Figure(figsize=(7 * n, 14))
    fig.suptitle(title, fontsize=15, fontweight="bold")
    gs = fig.add_gridspec(3, n, height_ratios=[1, 1, 1.2])

    # baris 0 = state awal, baris 1 = state akhir
    for row, (label, ship_list) in enumerate((("State Awal", initial_ships), ("State Akhir", final_ships))):
        for col, ship in enumerate(ship_list):
            ax = fig.add_subplot(gs[row, col])
            ax.set_xlim(0, ship.l)
            ax.set_ylim(ship.w, 0)
            ax.set_aspect("equal")
            ax.set_xticks(range(ship.l + 1))
            ax.set_yticks(range(ship.w + 1))
            ax.tick_params(labelbottom=False, labelleft=False, length=0)
            ax.grid(True, color="#c9d0d6", linewidth=0.6)
            for v in ship.list_vehicles_in_ship:
                rows, cols = (v.w, v.l) if v.orientation == "vertical" else (v.l, v.w)
                ax.add_patch(Rectangle((v.coor[1], v.coor[0]), cols, rows,
                                       facecolor=colors.get(v.id, "#cccccc"), edgecolor="#444455"))
                ax.text(v.coor[1] + cols / 2, v.coor[0] + rows / 2, v.id, ha="center", va="center", fontsize=7)
            ax.set_title(f"{label} - Kapal {ship.id} ({ship.w}x{ship.l})\n"
                         f"{len(ship.list_vehicles_in_ship)} kendaraan | berat {ship.calculate_ship_weight()}/"
                         f"{ship.max_capacity} | fee {ship.calculate_shipping_fee()}", fontsize=9)

    bottom = gs[2, :].subgridspec(1, 2, width_ratios=[2, 1])

    # plot objective function terhadap iterasi
    ax_plot = fig.add_subplot(bottom[0, 0])
    ax_plot.plot(range(len(history)), history, linewidth=1.8, marker="o" if len(history) <= 60 else None, markersize=3)
    for x in restart_points or []:
        ax_plot.axvline(x, color="red", linestyle=":", linewidth=1)
    ax_plot.set_title("Objective Function (Shipping Fee) vs Iterasi")
    ax_plot.set_xlabel("Iterasi" + (" (garis merah = restart)" if restart_points else ""))
    ax_plot.set_ylabel("Shipping Fee")
    ax_plot.grid(True, linestyle=":", alpha=0.6)

    # ringkasan
    ax_info = fig.add_subplot(bottom[0, 1])
    ax_info.axis("off")
    inside = {v for s in final_armada.ship_list for v in s.list_vehicles_in_ship}
    outside = [v.id for v in final_armada.list_all_vehicles if v not in inside]
    lines = [f"{k}: {v}" for k, v in info.items()]
    lines.append("")
    lines.append(textwrap.fill(f"Di luar kapal akhir ({len(outside)}): " + (", ".join(outside) or "-"), width=48))
    ax_info.text(0, 1, "\n".join(lines), va="top", ha="left", fontsize=10, family="monospace")

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    folder = os.path.dirname(filename)
    if folder:
        os.makedirs(folder, exist_ok=True)
    fig.savefig(filename, dpi=110)


if __name__ == "__main__":
    OUTPUT_DIR = os.path.join("output", "hill_climbing")
    N_NEIGHBORS = 50
    MAX_SIDEWAYS = 10
    MAX_RESTART = 5
    N_RUN = 3

    varian = [
        ("steepest", "Steepest Ascent Hill-Climbing", 0, False),
        ("sideways", "Hill-Climbing with Sideways Move", MAX_SIDEWAYS, False),
        ("stochastic", "Stochastic Hill-Climbing", 0, True),
    ]

    for key, nama, max_sideways, stochastic in varian:
        for run in range(1, N_RUN + 1):
            awal = copy.deepcopy(armada)
            t0 = time.perf_counter()
            hasil, fee, history = hill_climbing(copy.deepcopy(awal), max_sideways, N_NEIGHBORS, None, stochastic)
            durasi = time.perf_counter() - t0

            info = {
                "Fee awal": history[0],
                "Fee akhir": fee,
                "Durasi": f"{durasi:.4f} s",
                "Neighbor/iterasi": N_NEIGHBORS,
                "Iterasi hingga berhenti": len(history) - 1,
            }
            if key == "sideways":
                info["Maks sideways move"] = max_sideways
                info["Sideways move dilakukan"] = sum(1 for a, b in zip(history, history[1:]) if a == b)

            export_run_image(os.path.join(OUTPUT_DIR, f"{key}_run{run}.png"),
                             f"{nama} - Run {run}", awal, hasil, history, info)
            print(f"{nama} run {run}: {history[0]} -> {fee} | {len(history) - 1} iterasi | {durasi:.4f} s")

    for run in range(1, N_RUN + 1):
        awal = copy.deepcopy(armada)
        histories = []
        t0 = time.perf_counter()
        hasil, fee, _ = random_restart(copy.deepcopy(awal), 0, N_NEIGHBORS, MAX_RESTART, None, False, histories)
        durasi = time.perf_counter() - t0

        # gabungkan riwayat semua restart jadi satu plot, garis merah = titik restart
        gabungan, titik_restart = [], []
        for h in histories:
            if gabungan:
                titik_restart.append(len(gabungan))
            gabungan.extend(h)

        iter_per_restart = [len(h) - 1 for h in histories]
        info = {
            "Fee awal": histories[0][0],
            "Fee akhir (terbaik)": fee,
            "Durasi": f"{durasi:.4f} s",
            "Neighbor/iterasi": N_NEIGHBORS,
            "Maks restart": MAX_RESTART,
            "Banyak restart": len(histories) - 1,
            "Iterasi run awal": iter_per_restart[0],
            "Iterasi per restart": ", ".join(map(str, iter_per_restart[1:])) or "-",
            "Total iterasi": sum(iter_per_restart),
        }
        export_run_image(os.path.join(OUTPUT_DIR, f"random_restart_run{run}.png"),
                         f"Random Restart Hill-Climbing - Run {run}", awal, hasil, gabungan, info, titik_restart)
        print(f"Random Restart run {run}: {histories[0][0]} -> {fee} | {len(histories) - 1} restart | "
              f"iterasi/restart {iter_per_restart} | {durasi:.4f} s")

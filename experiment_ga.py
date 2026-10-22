import os
import matplotlib.pyplot as plt
from starter import list_vehicles
from genetic import run_genetic_algorithm

def format_grid_to_string(grid):
    lines = []
    for row in grid:
        lines.append(" ".join(row))
    return "\n".join(lines)


def get_vehicle_lists_string(individual):
    loaded = []
    unplaced = []
    for v in individual.vehicles:
        gene = individual.genes.get(v.id)
        if gene and gene["is_loaded"]:
            loaded.append(f"{v.id}(fee:{v.shipping_fee}, w:{v.weight})")
        else:
            unplaced.append(f"{v.id}(fee:{v.shipping_fee}, w:{v.weight})")
            
    loaded_str = ", ".join(loaded) if len(loaded) > 0 else "-"
    unplaced_str = ", ".join(unplaced) if len(unplaced) > 0 else "-"
    return f"Kendaraan di Kapal ({len(loaded)}):\n  {loaded_str}\nKendaraan di Luar Kapal ({len(unplaced)}):\n  {unplaced_str}"


def main():
    if not os.path.exists("output"):
        os.makedirs("output")

    csv_file = open("output/rekap_eksperimen_ga.csv", "w", encoding="utf-8")
    csv_file.write("Eksperimen,Populasi,Iterasi,Run,Durasi_Detik,Fitness_Awal,Fitness_Akhir\n")

    txt_file = open("output/rekap_eksperimen_ga.txt", "w", encoding="utf-8")
    txt_file.write("Eksperimen\tPopulasi\tIterasi\tRun\tDurasi(detik)\tFitness_Awal\tFitness_Akhir\n")

    state_file = open("output/visualisasi_state_ga.txt", "w", encoding="utf-8")

    # Eksperimen 1: populasi kontrol (50), variasi iterasi (50, 100, 200)
    pop_kontrol = 50
    variasi_iterasi = [50, 100, 200]

    print("Memulai Eksperimen 1: Populasi Kontrol (Populasi = 50)")
    for iterasi in variasi_iterasi:
        for run_idx in range(1, 4):
            print(f"Exp 1 | Populasi: {pop_kontrol} | Iterasi: {iterasi} | Run ke-{run_idx}...")
            
            hasil = run_genetic_algorithm(
                list_vehicles,
                ship_w=10,
                ship_l=20,
                max_capacity=200,
                pop_size=pop_kontrol,
                generations=iterasi
            )
            
            durasi_formatted = f"{hasil['duration']:.4f}"
            fit_awal = f"{hasil['initial_state'].fitness:.1f}"
            fit_akhir = f"{hasil['best_fitness']:.1f}"
            
            csv_file.write(f"Exp1,{pop_kontrol},{iterasi},{run_idx},{durasi_formatted},{fit_awal},{fit_akhir}\n")
            txt_file.write(f"Exp1\t{pop_kontrol}\t{iterasi}\t{run_idx}\t{durasi_formatted}\t{fit_awal}\t{fit_akhir}\n")
            
            state_file.write(f"Eksperimen 1: Pop={pop_kontrol}, Iter={iterasi}, Run={run_idx}\n")
            state_file.write(f"State Awal (Fitness: {fit_awal}):\n")
            state_file.write(get_vehicle_lists_string(hasil['initial_state']) + "\n")
            state_file.write(format_grid_to_string(hasil['initial_state'].get_grid()) + "\n\n")
            
            state_file.write(f"State Akhir (Fitness: {fit_akhir}, Durasi: {durasi_formatted} detik):\n")
            state_file.write(get_vehicle_lists_string(hasil['final_state']) + "\n")
            state_file.write(format_grid_to_string(hasil['final_state'].get_grid()) + "\n")
            state_file.write("--------------------------------------------------\n\n")
            
            plt.figure(figsize=(7, 4))
            plt.plot(hasil["history_max"], label="Fitness Maksimum")
            plt.plot(hasil["history_avg"], label="Rata-rata Populasi", linestyle="--")
            plt.title(f"Eksperimen 1: Pop={pop_kontrol}, Iter={iterasi} (Run {run_idx})")
            plt.xlabel("Iterasi")
            plt.ylabel("Shipping Fee")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            plt.savefig(f"output/exp1_iter{iterasi}_run{run_idx}.png")
            plt.close()

    # Eksperimen 2: iterasi kontrol (100), variasi populasi (20, 50, 100)
    iter_kontrol = 100
    variasi_populasi = [20, 50, 100]

    print("\nMemulai Eksperimen 2: Iterasi Kontrol (Iterasi = 100)")
    for pop in variasi_populasi:
        for run_idx in range(1, 4):
            print(f"Exp 2 | Populasi: {pop} | Iterasi: {iter_kontrol} | Run ke-{run_idx}...")
            
            hasil = run_genetic_algorithm(
                list_vehicles,
                ship_w=10,
                ship_l=20,
                max_capacity=200,
                pop_size=pop,
                generations=iter_kontrol
            )
            
            durasi_formatted = f"{hasil['duration']:.4f}"
            fit_awal = f"{hasil['initial_state'].fitness:.1f}"
            fit_akhir = f"{hasil['best_fitness']:.1f}"
            
            csv_file.write(f"Exp2,{pop},{iter_kontrol},{run_idx},{durasi_formatted},{fit_awal},{fit_akhir}\n")
            txt_file.write(f"Exp2\t{pop}\t{iter_kontrol}\t{run_idx}\t{durasi_formatted}\t{fit_awal}\t{fit_akhir}\n")
            
            state_file.write(f"Eksperimen 2: Pop={pop}, Iter={iter_kontrol}, Run={run_idx}\n")
            state_file.write(f"State Awal (Fitness: {fit_awal}):\n")
            state_file.write(get_vehicle_lists_string(hasil['initial_state']) + "\n")
            state_file.write(format_grid_to_string(hasil['initial_state'].get_grid()) + "\n\n")
            
            state_file.write(f"State Akhir (Fitness: {fit_akhir}, Durasi: {durasi_formatted} detik):\n")
            state_file.write(get_vehicle_lists_string(hasil['final_state']) + "\n")
            state_file.write(format_grid_to_string(hasil['final_state'].get_grid()) + "\n")
            state_file.write("--------------------------------------------------\n\n")
            
            plt.figure(figsize=(7, 4))
            plt.plot(hasil["history_max"], label="Fitness Maksimum")
            plt.plot(hasil["history_avg"], label="Rata-rata Populasi", linestyle="--")
            plt.title(f"Eksperimen 2: Pop={pop}, Iter={iter_kontrol} (Run {run_idx})")
            plt.xlabel("Iterasi")
            plt.ylabel("Shipping Fee")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            
            plt.savefig(f"output/exp2_pop{pop}_run{run_idx}.png")
            plt.close()

    csv_file.close()
    txt_file.close()
    state_file.close()
    print("\nSeluruh 18 eksperimen selesai dijalankan.")


if __name__ == "__main__":
    main()

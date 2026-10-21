import random
from starter import Vehicle, list_vehicles

class Individual:
    def __init__(self, vehicles, ship_w, ship_l, max_capacity):
        self.vehicles = vehicles
        self.ship_w = ship_w
        self.ship_l = ship_l
        self.max_capacity = max_capacity
        
        # pemetaan gen: id kendaraan -> status penempatan
        self.genes = {}
        self.fitness = 0.0
        self.total_weight = 0

    def randomize(self):
        # acak urutan mobil agar tiap individu punya urutan penempatan berbeda
        shuffled_vehicles = list(self.vehicles)
        random.shuffle(shuffled_vehicles)
        
        # grid sementara untuk memantau sel yang sudah terisi
        grid = []
        for _ in range(self.ship_w):
            baris = [0] * self.ship_l
            grid.append(baris)
            
        current_weight = 0
        
        for v in shuffled_vehicles:
            orientation = random.choice(["horizontal", "vertical"])
            
            if orientation == "vertical":
                w = v.w
                l = v.l
            else:
                w = v.l
                l = v.w
            
            placed = False
            
            # cek apakah berat dan ukuran fisik masih muat di geladak
            if current_weight + v.weight <= self.max_capacity:
                if w <= self.ship_w and l <= self.ship_l:
                    max_x = self.ship_w - w
                    max_y = self.ship_l - l
                    
                    # coba maksimal 15 kali mencari koordinat kosong
                    for _ in range(15):
                        rx = random.randint(0, max_x)
                        ry = random.randint(0, max_y)
                        
                        overlap = False
                        for r in range(w):
                            for c in range(l):
                                if grid[rx + r][ry + c] != 0:
                                    overlap = True
                                    break
                            if overlap:
                                break
                        
                        # jika tidak menimpa mobil lain, letakkan mobil
                        if not overlap:
                            for r in range(w):
                                for c in range(l):
                                    grid[rx + r][ry + c] = v.id
                            
                            self.genes[v.id] = {
                                "is_loaded": True,
                                "x": rx,
                                "y": ry,
                                "orientation": orientation
                            }
                            current_weight = current_weight + v.weight
                            placed = True
                            break
            
            # jika tidak muat atau gagal cari ruang kosong, tandai di luar kapal
            if not placed:
                self.genes[v.id] = {
                    "is_loaded": False,
                    "x": -1,
                    "y": -1,
                    "orientation": orientation
                }
                
        self.evaluate()

    def evaluate(self):
        # bersihkan grid untuk validasi ulang dan hitung fitness
        grid = []
        for _ in range(self.ship_w):
            baris = [0] * self.ship_l
            grid.append(baris)
            
        total_fee = 0.0
        current_weight = 0

        for v in self.vehicles:
            gene = self.genes.get(v.id)
            if gene is None:
                continue
            if not gene["is_loaded"]:
                continue

            orientation = gene["orientation"]
            if orientation == "vertical":
                w = v.w
                l = v.l
            else:
                w = v.l
                l = v.w
                
            x = gene["x"]
            y = gene["y"]

            # batalkan penempatan jika koordinat keluar dari batas kapal
            if x < 0 or y < 0:
                gene["is_loaded"] = False
                continue
            if (x + w) > self.ship_w or (y + l) > self.ship_l:
                gene["is_loaded"] = False
                continue

            # batalkan penempatan jika beban melebihi kapasitas maksimum
            if current_weight + v.weight > self.max_capacity:
                gene["is_loaded"] = False
                continue

            # periksa apakah menimpa kendaraan lain yang sudah valid
            overlap = False
            for r in range(w):
                for c in range(l):
                    if grid[x + r][y + c] != 0:
                        overlap = True
                        break
                if overlap:
                    break

            if overlap:
                gene["is_loaded"] = False
            else:
                for r in range(w):
                    for c in range(l):
                        grid[x + r][y + c] = v.id
                current_weight = current_weight + v.weight
                total_fee = total_fee + v.shipping_fee

        self.total_weight = current_weight
        self.fitness = total_fee
        return self.fitness

    def clone(self):
        # salin objek dan nilai gen secara mandiri agar tidak saling merusak state
        new_ind = Individual(self.vehicles, self.ship_w, self.ship_l, self.max_capacity)
        for vid, state in self.genes.items():
            new_ind.genes[vid] = {
                "is_loaded": state["is_loaded"],
                "x": state["x"],
                "y": state["y"],
                "orientation": state["orientation"]
            }
        new_ind.fitness = self.fitness
        new_ind.total_weight = self.total_weight
        return new_ind

    def display(self):
        grid = []
        for _ in range(self.ship_w):
            baris = ["0"] * self.ship_l
            grid.append(baris)
            
        for v in self.vehicles:
            gene = self.genes.get(v.id)
            if gene is not None:
                if gene["is_loaded"]:
                    if gene["orientation"] == "vertical":
                        w = v.w
                        l = v.l
                    else:
                        w = v.l
                        l = v.w
                    for r in range(w):
                        for c in range(l):
                            grid[gene["x"] + r][gene["y"] + c] = v.id
                        
        print(f"Total Fitness: {self.fitness}")
        print(f"Total Weight : {self.total_weight}/{self.max_capacity}")
        for row in grid:
            print(" ".join(row))


# ==========================================
# BATCH 2: OPERATOR GENETIK
# ==========================================

def tournament_selection(population, k=3):
    # ambil k kandidat acak dari populasi
    candidates = random.sample(population, k)
    
    # cari kandidat dengan fitness tertinggi di antara k peserta
    best_candidate = candidates[0]
    for ind in candidates:
        if ind.fitness > best_candidate.fitness:
            best_candidate = ind
            
    return best_candidate


def crossover(parent1, parent2, crossover_rate=0.8):
    # jika tidak lolos probabilitas kawin, anak mengkloning parent1
    if random.random() > crossover_rate:
        return parent1.clone()

    child = Individual(parent1.vehicles, parent1.ship_w, parent1.ship_l, parent1.max_capacity)
    
    # kombinasikan gen: peluang 50% dari parent1, 50% dari parent2
    for v in parent1.vehicles:
        if random.random() < 0.5:
            source_gene = parent1.genes[v.id]
        else:
            source_gene = parent2.genes[v.id]

        child.genes[v.id] = {
            "is_loaded": source_gene["is_loaded"],
            "x": source_gene["x"],
            "y": source_gene["y"],
            "orientation": source_gene["orientation"]
        }

    # reparasi otomatis jika ada mobil yang bertabrakan dari gabungan kedua orang tua
    child.evaluate()
    return child


def mutate(individual, mutation_rate=0.2):
    # jika tidak lolos probabilitas mutasi, lewati
    if random.random() > mutation_rate:
        return

    # kumpulkan daftar mobil yang saat ini di dalam dan di luar kapal
    loaded_ids = []
    unloaded_ids = []
    for vid, state in individual.genes.items():
        if state["is_loaded"]:
            loaded_ids.append(vid)
        else:
            unloaded_ids.append(vid)

    # pilih salah satu dari 3 aksi mutasi yang sesuai spesifikasi
    mutation_type = random.randint(1, 3)

    if mutation_type == 1 and len(loaded_ids) > 0:
        # aksi 1: geser koordinat mobil di dalam kapal ke posisi acak baru
        target_id = random.choice(loaded_ids)
        individual.genes[target_id]["x"] = random.randint(0, individual.ship_w - 1)
        individual.genes[target_id]["y"] = random.randint(0, individual.ship_l - 1)

    elif mutation_type == 2 and len(loaded_ids) > 0:
        # aksi 2: putar orientasi mobil
        target_id = random.choice(loaded_ids)
        current_orient = individual.genes[target_id]["orientation"]
        if current_orient == "vertical":
            individual.genes[target_id]["orientation"] = "horizontal"
        else:
            individual.genes[target_id]["orientation"] = "vertical"

    elif mutation_type == 3 and len(unloaded_ids) > 0:
        # aksi 3: coba masukkan mobil dari luar kapal ke posisi acak
        target_id = random.choice(unloaded_ids)
        individual.genes[target_id]["is_loaded"] = True
        individual.genes[target_id]["x"] = random.randint(0, individual.ship_w - 1)
        individual.genes[target_id]["y"] = random.randint(0, individual.ship_l - 1)

    # validasi dan reparasi ulang setelah mengalami mutasi
    individual.evaluate()


def get_elites(population, elite_count=2):
    # urutkan populasi dari fitness tertinggi ke terendah secara manual
    sorted_pop = list(population)
    sorted_pop.sort(key=lambda ind: ind.fitness, reverse=True)
    
    elites = []
    for i in range(elite_count):
        elites.append(sorted_pop[i].clone())
        
    return elites


if __name__ == "__main__":
    print("=== PENGUJIAN BATCH 2: OPERATOR GENETIK ===")
    
    # 1. Uji Buat Populasi Mini
    pop = []
    for _ in range(5):
        ind = Individual(list_vehicles, ship_w=10, ship_l=20, max_capacity=200)
        ind.randomize()
        pop.append(ind)
    print(f"Berhasil membuat populasi mini: {len(pop)} individu")
    for i, ind in enumerate(pop):
        print(f"Individu {i+1} Fitness: {ind.fitness}")

    # 2. Uji Tournament Selection
    parent1 = tournament_selection(pop, k=3)
    parent2 = tournament_selection(pop, k=3)
    print(f"\nParent 1 terpilih: Fitness {parent1.fitness}")
    print(f"Parent 2 terpilih: Fitness {parent2.fitness}")

    # 3. Uji Crossover
    child = crossover(parent1, parent2, crossover_rate=1.0)
    print(f"\nAnak hasil persilangan: Fitness {child.fitness}, Berat {child.total_weight}/{child.max_capacity}")
    assert child.total_weight <= child.max_capacity, "Error: Berat anak melebihi kapasitas!"

    # 4. Uji Mutasi
    print("\nSebelum mutasi, Fitness:", child.fitness)
    mutate(child, mutation_rate=1.0) # paksa mutasi 100%
    print("Setelah mutasi, Fitness:", child.fitness)
    assert child.total_weight <= child.max_capacity, "Error: Berat setelah mutasi melebihi kapasitas!"

    # 5. Uji Elitisme
    elites = get_elites(pop, elite_count=2)
    print(f"\n2 Elite terbaik: Fitness {elites[0].fitness} dan {elites[1].fitness}")
    assert elites[0].fitness >= elites[1].fitness, "Error: Urutan elit tidak sesuai!"
    
    print("\nSemua pengujian Batch 2 berhasil dan valid!")

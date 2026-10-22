import random
import time
import copy
import os
import matplotlib.pyplot as plt
from starter import Vehicle, Ship, Armada

list_vehicles = [
    Vehicle(id="a", w=3, l=2, orientation="horizontal", shipping_fee=5, weight=10, eta=10),
    Vehicle(id="b", w=3, l=2, orientation="vertical", shipping_fee=20, weight=10, eta=10),
    Vehicle(id="c", w=3, l=2, orientation="horizontal", shipping_fee=20, weight=10, eta=10),
    Vehicle(id="d", w=2, l=4, orientation="vertical", shipping_fee=35, weight=15, eta=12),
    Vehicle(id="e", w=2, l=3, orientation="horizontal", shipping_fee=25, weight=12, eta=14),
    Vehicle(id="f", w=4, l=2, orientation="horizontal", shipping_fee=40, weight=18, eta=8),
    Vehicle(id="g", w=2, l=2, orientation="vertical", shipping_fee=15, weight=8, eta=15),
    Vehicle(id="h", w=5, l=2, orientation="horizontal", shipping_fee=50, weight=25, eta=9),
    Vehicle(id="i", w=3, l=3, orientation="vertical", shipping_fee=30, weight=14, eta=11),
    Vehicle(id="j", w=2, l=5, orientation="vertical", shipping_fee=45, weight=20, eta=13),
    Vehicle(id="k", w=3, l=2, orientation="horizontal", shipping_fee=5, weight=11, eta=10),
    Vehicle(id="l", w=2, l=3, orientation="vertical", shipping_fee=28, weight=13, eta=12),
    Vehicle(id="m", w=4, l=2, orientation="horizontal", shipping_fee=2, weight=17, eta=8),
    Vehicle(id="n", w=2, l=4, orientation="vertical", shipping_fee=32, weight=16, eta=9),
    Vehicle(id="o", w=2, l=2, orientation="horizontal", shipping_fee=3, weight=9, eta=14),
    Vehicle(id="p", w=3, l=3, orientation="vertical", shipping_fee=33, weight=15, eta=11),
    Vehicle(id="q", w=5, l=2, orientation="horizontal", shipping_fee=48, weight=24, eta=7),
    Vehicle(id="r", w=2, l=5, orientation="vertical", shipping_fee=42, weight=21, eta=13),
    Vehicle(id="s", w=4, l=3, orientation="horizontal", shipping_fee=6, weight=26, eta=10),
    Vehicle(id="t", w=3, l=4, orientation="vertical", shipping_fee=55, weight=26, eta=15),
    Vehicle(id="u", w=2, l=2, orientation="horizontal", shipping_fee=15, weight=8, eta=12),
    Vehicle(id="v", w=3, l=2, orientation="vertical", shipping_fee=25, weight=12, eta=14),
    Vehicle(id="w", w=4, l=2, orientation="horizontal", shipping_fee=40, weight=18, eta=9),
    Vehicle(id="x", w=2, l=3, orientation="vertical", shipping_fee=30, weight=14, eta=11),
    Vehicle(id="y", w=3, l=3, orientation="horizontal", shipping_fee=35, weight=16, eta=10),
    Vehicle(id="z", w=2, l=4, orientation="vertical", shipping_fee=38, weight=17, eta=12),
    Vehicle(id="A", w=3, l=2, orientation="horizontal", shipping_fee=24, weight=11, eta=11),
    Vehicle(id="B", w=2, l=2, orientation="vertical", shipping_fee=16, weight=8, eta=14),
    Vehicle(id="C", w=4, l=3, orientation="horizontal", shipping_fee=52, weight=25, eta=9),
    Vehicle(id="D", w=3, l=3, orientation="vertical", shipping_fee=34, weight=15, eta=13),
    Vehicle(id="E", w=5, l=2, orientation="horizontal", shipping_fee=46, weight=22, eta=8),
    Vehicle(id="F", w=2, l=5, orientation="vertical", shipping_fee=44, weight=21, eta=12),
    Vehicle(id="G", w=2, l=3, orientation="horizontal", shipping_fee=26, weight=13, eta=15),
    Vehicle(id="H", w=4, l=2, orientation="vertical", shipping_fee=36, weight=18, eta=10),
    Vehicle(id="I", w=3, l=4, orientation="horizontal", shipping_fee=48, weight=23, eta=11),
]

class Individual:
    def __init__(self, vehicles, ships_or_w, ship_l=None, max_capacity=None):
        self.vehicles = list(vehicles)
        
        # bisa terima objek kumpulan kapal atau parameter dimensi kapal tunggal
        if isinstance(ships_or_w, (list, set, tuple)):
            self.ships = list(ships_or_w)
        else:
            ship_w = ships_or_w
            self.ships = [Ship(w=ship_w, l=ship_l, max_capacity=max_capacity, id="S1")]
            
        self.ship_map = {}
        for s in self.ships:
            self.ship_map[s.id] = s
            
        # kompatibilitas jika dipanggil mode single ship
        if len(self.ships) == 1:
            first_ship = self.ships[0]
            self.ship_w = first_ship.w
            self.ship_l = first_ship.l
            self.max_capacity = first_ship.max_capacity
            
        self.genes = {}
        self.fitness = 0.0
        self.total_weight = 0

    def randomize(self):
        # acak urutan mobil agar penataan awal tiap individu beda-beda
        shuffled = list(self.vehicles)
        random.shuffle(shuffled)
        
        ship_grids = {}
        ship_weights = {}
        for s in self.ships:
            grid = []
            for _ in range(s.w):
                baris = [0] * s.l
                grid.append(baris)
            ship_grids[s.id] = grid
            ship_weights[s.id] = 0
            
        for v in shuffled:
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "vertical":
                w = v.w
                l = v.l
            else:
                w = v.l
                l = v.w
                
            # cari kapal acak yang muat berat kendaraan
            candidate_ships = []
            for s in self.ships:
                if ship_weights[s.id] + v.weight <= s.max_capacity:
                    candidate_ships.append(s)
            random.shuffle(candidate_ships)
            
            placed = False
            for target_ship in candidate_ships:
                if w <= target_ship.w and l <= target_ship.l:
                    max_x = target_ship.w - w
                    max_y = target_ship.l - l
                    
                    grid = ship_grids[target_ship.id]
                    # coba cari koordinat acak sampai 15 kali untuk cari ruang kosong
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
                                
                        if not overlap:
                            for r in range(w):
                                for c in range(l):
                                    grid[rx + r][ry + c] = v.id
                                    
                            self.genes[v.id] = {
                                "ship_id": target_ship.id,
                                "is_loaded": True,
                                "x": rx,
                                "y": ry,
                                "orientation": orientation
                            }
                            ship_weights[target_ship.id] = ship_weights[target_ship.id] + v.weight
                            placed = True
                            break
                            
                if placed:
                    break
                    
            if not placed:
                # penting: simpan target kapal dan koordinat awal acak agar kromosomnya tidak hilang permanen
                random_ship = random.choice(self.ships)
                if orientation == "vertical":
                    cw = v.w
                    cl = v.l
                else:
                    cw = v.l
                    cl = v.w
                if cw <= random_ship.w and cl <= random_ship.l:
                    rx = random.randint(0, random_ship.w - cw)
                    ry = random.randint(0, random_ship.l - cl)
                else:
                    rx = 0
                    ry = 0
                self.genes[v.id] = {
                    "ship_id": random_ship.id,
                    "is_loaded": False,
                    "x": rx,
                    "y": ry,
                    "orientation": orientation
                }
                
        self.evaluate()

    def evaluate(self):
        ship_grids = {}
        ship_weights = {}
        for s in self.ships:
            grid = []
            for _ in range(s.w):
                baris = [0] * s.l
                grid.append(baris)
            ship_grids[s.id] = grid
            ship_weights[s.id] = 0
            
        total_fee = 0.0
        
        # ambil semua kendaraan yang punya target kapal valid di kromosomnya
        # jangan cuma ambil yang is_loaded=True, biar gen mobil ga mati permanen!
        candidate_vehicles = []
        for v in self.vehicles:
            gene = self.genes.get(v.id)
            if gene is not None:
                if gene["ship_id"] is not None and gene["ship_id"] in self.ship_map:
                    candidate_vehicles.append(v)
                    
        # prioritaskan mobil fee mahal masuk duluan jika ada perebutan sel
        candidate_vehicles.sort(key=lambda item: item.shipping_fee, reverse=True)
        
        for v in candidate_vehicles:
            gene = self.genes[v.id]
            target_ship = self.ship_map[gene["ship_id"]]
                
            orientation = gene["orientation"]
            if orientation == "vertical":
                w = v.w
                l = v.l
            else:
                w = v.l
                l = v.w
                
            x = gene["x"]
            y = gene["y"]
            
            if x < 0 or y < 0:
                gene["is_loaded"] = False
                continue
            if (x + w) > target_ship.w or (y + l) > target_ship.l:
                gene["is_loaded"] = False
                continue
                
            if ship_weights[target_ship.id] + v.weight > target_ship.max_capacity:
                gene["is_loaded"] = False
                continue
                
            grid = ship_grids[target_ship.id]
            overlap = False
            for r in range(w):
                for c in range(l):
                    if grid[x + r][y + c] != 0:
                        overlap = True
                        break
                if overlap:
                    break
                    
            if overlap:
                # kalau tabrakan, cukup tandai is_loaded False. Jangan hapus ship_id atau x, y-nya!
                gene["is_loaded"] = False
            else:
                for r in range(w):
                    for c in range(l):
                        grid[x + r][y + c] = v.id
                ship_weights[target_ship.id] = ship_weights[target_ship.id] + v.weight
                total_fee = total_fee + v.shipping_fee
                gene["is_loaded"] = True
                
        total_w = 0
        for w_val in ship_weights.values():
            total_w = total_w + w_val
        self.total_weight = total_w
        self.fitness = total_fee
        return self.fitness

    def clone(self):
        new_ind = Individual(self.vehicles, self.ships)
        for vid, state in self.genes.items():
            new_ind.genes[vid] = {
                "ship_id": state["ship_id"],
                "is_loaded": state["is_loaded"],
                "x": state["x"],
                "y": state["y"],
                "orientation": state["orientation"]
            }
        new_ind.fitness = self.fitness
        new_ind.total_weight = self.total_weight
        return new_ind

    def get_grid(self, ship_id=None):
        # ambil grid kapal pertama atau berdasarkan id kapal yang dipilih
        if ship_id is not None and ship_id in self.ship_map:
            target_ship = self.ship_map[ship_id]
        else:
            target_ship = self.ships[0]
            
        grid = []
        for _ in range(target_ship.w):
            baris = ["0"] * target_ship.l
            grid.append(baris)
            
        for v in self.vehicles:
            gene = self.genes.get(v.id)
            if gene is not None:
                if gene["is_loaded"] and gene["ship_id"] == target_ship.id:
                    if gene["orientation"] == "vertical":
                        w = v.w
                        l = v.l
                    else:
                        w = v.l
                        l = v.w
                    for r in range(w):
                        for c in range(l):
                            grid[gene["x"] + r][gene["y"] + c] = v.id
        return grid

    def get_armada_grids(self):
        grids = {}
        for s in self.ships:
            grids[s.id] = self.get_grid(s.id)
        return grids

    def to_armada(self):
        new_ships = set()
        ship_map_copy = {}
        for s in self.ships:
            fresh_ship = Ship(w=s.w, l=s.l, max_capacity=s.max_capacity, id=s.id)
            new_ships.add(fresh_ship)
            ship_map_copy[s.id] = fresh_ship
            
        vehicles_copy = copy.deepcopy(self.vehicles)
        armada_obj = Armada(new_ships, vehicles_copy)
        
        for v in vehicles_copy:
            gene = self.genes.get(v.id)
            if gene is not None and gene["is_loaded"] and gene["ship_id"] in ship_map_copy:
                target_ship = ship_map_copy[gene["ship_id"]]
                v.orientation = gene["orientation"]
                success = target_ship.inputing_vehicle_success(v, gene["x"], gene["y"])
                if not success:
                    v.coor = [-1, -1]
            else:
                v.coor = [-1, -1]
                
        return armada_obj

    def display(self):
        print(f"Total Fitness: {self.fitness}")
        print(f"Total Berat  : {self.total_weight}")
        for s in self.ships:
            grid = self.get_grid(s.id)
            print(f"--- Kapal {s.id} ({s.w}x{s.l}, Kapasitas: {s.max_capacity}) ---")
            for row in grid:
                print(" ".join(row))


def tournament_selection(population, k=3):
    k_actual = min(k, len(population))
    candidates = random.sample(population, k_actual)
    
    best_candidate = candidates[0]
    for ind in candidates:
        if ind.fitness > best_candidate.fitness:
            best_candidate = ind
            
    return best_candidate


def crossover(parent1, parent2, crossover_rate=0.8):
    if random.random() > crossover_rate:
        return parent1.clone()

    child = Individual(parent1.vehicles, parent1.ships)
    
    # bias crossover: prioritaskan gen dari parent yang mobilnya beneran berhasil masuk geladak
    for v in parent1.vehicles:
        g1 = parent1.genes[v.id]
        g2 = parent2.genes[v.id]

        if g1["is_loaded"] and not g2["is_loaded"]:
            if random.random() < 0.7:
                source_gene = g1
            else:
                source_gene = g2
        elif g2["is_loaded"] and not g1["is_loaded"]:
            if random.random() < 0.7:
                source_gene = g2
            else:
                source_gene = g1
        else:
            if random.random() < 0.5:
                source_gene = g1
            else:
                source_gene = g2

        child.genes[v.id] = {
            "ship_id": source_gene["ship_id"],
            "is_loaded": source_gene["is_loaded"],
            "x": source_gene["x"],
            "y": source_gene["y"],
            "orientation": source_gene["orientation"]
        }

    return child


def fill_empty_slots(individual):
    # operator agresif buat nyari ruang-ruang kosong di geladak kapal dan menyisipkan mobil unplaced
    ship_grids = {}
    ship_weights = {}
    for s in individual.ships:
        grid = []
        for _ in range(s.w):
            baris = [0] * s.l
            grid.append(baris)
        ship_grids[s.id] = grid
        ship_weights[s.id] = 0

    v_map = {}
    for v in individual.vehicles:
        v_map[v.id] = v

    # petakan mobil yang saat ini sudah valid masuk geladak
    for vid, gene in individual.genes.items():
        if gene["is_loaded"] and gene["ship_id"] in individual.ship_map:
            v = v_map[vid]
            s = individual.ship_map[gene["ship_id"]]
            orient = gene["orientation"]
            if orient == "vertical":
                w = v.w
                l = v.l
            else:
                w = v.l
                l = v.w
            for r in range(w):
                for c in range(l):
                    ship_grids[s.id][gene["x"] + r][gene["y"] + c] = vid
            ship_weights[s.id] = ship_weights[s.id] + v.weight

    # kumpulkan mobil-mobil yang masih di luar kapal (unplaced)
    unplaced = []
    for v in individual.vehicles:
        gene = individual.genes.get(v.id)
        if gene is None or not gene["is_loaded"]:
            unplaced.append(v)

    # urutkan dari shipping fee terbesar agar penambahan fee maksimal
    unplaced.sort(key=lambda item: item.shipping_fee, reverse=True)

    for v in unplaced:
        # cari kapal-kapal yang masih punya sisa kapasitas berat
        candidate_ships = []
        for s in individual.ships:
            if ship_weights[s.id] + v.weight <= s.max_capacity:
                candidate_ships.append(s)

        if len(candidate_ships) == 0:
            continue

        # acak urutan kapal kandidat agar variasinya terjaga
        random.shuffle(candidate_ships)
        placed = False

        for target_ship in candidate_ships:
            grid = ship_grids[target_ship.id]
            orientations = ["vertical", "horizontal"]
            random.shuffle(orientations)

            for orient in orientations:
                if orient == "vertical":
                    w = v.w
                    l = v.l
                else:
                    w = v.l
                    l = v.w

                if w > target_ship.w or l > target_ship.l:
                    continue

                max_x = target_ship.w - w
                max_y = target_ship.l - l

                # coba cari slot: kadang acak dulu, kalau ga dapet baru first-fit terstruktur
                found_pos = None
                if random.random() < 0.35:
                    for _ in range(12):
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
                        if not overlap:
                            found_pos = (rx, ry)
                            break

                # scan terstruktur dari pojok untuk memadatkan geladak kapal
                if found_pos is None:
                    for rx in range(max_x + 1):
                        for ry in range(max_y + 1):
                            overlap = False
                            for r in range(w):
                                for c in range(l):
                                    if grid[rx + r][ry + c] != 0:
                                        overlap = True
                                        break
                                if overlap:
                                    break
                            if not overlap:
                                found_pos = (rx, ry)
                                break
                        if found_pos is not None:
                            break

                if found_pos is not None:
                    fx, fy = found_pos
                    for r in range(w):
                        for c in range(l):
                            grid[fx + r][fy + c] = v.id
                    ship_weights[target_ship.id] = ship_weights[target_ship.id] + v.weight

                    individual.genes[v.id] = {
                        "ship_id": target_ship.id,
                        "is_loaded": True,
                        "x": fx,
                        "y": fy,
                        "orientation": orient
                    }
                    placed = True
                    break

            if placed:
                break

    # evaluasi ulang fitness dan berat setelah penyisipan mobil
    individual.evaluate()


def mutate(individual, mutation_rate=0.3, is_stagnant=False):
    # evaluasi awal agar status is_loaded terverifikasi
    individual.evaluate()

    v_map = {}
    for v in individual.vehicles:
        v_map[v.id] = v

    loaded_ids = []
    unloaded_ids = []
    for vid, state in individual.genes.items():
        if state["is_loaded"] and state["ship_id"] is not None:
            loaded_ids.append(vid)
        else:
            unloaded_ids.append(vid)

    # mutasi adaptif: kalau stagnan, tingkatkan mutation rate dan jumlah mutasi
    effective_rate = mutation_rate
    if is_stagnant:
        effective_rate = min(0.7, mutation_rate * 1.6)

    if random.random() < effective_rate:
        # mutasi multi-gene: ubah 1 sampai 3 gen sekaligus
        if is_stagnant:
            num_mutations = random.randint(2, 4)
        else:
            num_mutations = random.randint(1, 3)

        for _ in range(num_mutations):
            m_type = random.randint(1, 4)

            if m_type == 1 and len(loaded_ids) > 0:
                # variasikan koordinat / jiggle koordinat mobil yang sudah ada di geladak
                target_id = random.choice(loaded_ids)
                v = v_map[target_id]
                gene = individual.genes[target_id]
                if gene["ship_id"] is None or gene["ship_id"] not in individual.ship_map:
                    continue
                target_ship = individual.ship_map[gene["ship_id"]]

                orient = gene["orientation"]
                if orient == "vertical":
                    w = v.w
                    l = v.l
                else:
                    w = v.l
                    l = v.w

                max_x = target_ship.w - w
                max_y = target_ship.l - l
                if max_x >= 0 and max_y >= 0:
                    if random.random() < 0.65:
                        # jiggle halus (-2 s.d. +2) biar merapat ke sudut atau mobil lain
                        dx = random.choice([-2, -1, 1, 2])
                        dy = random.choice([-2, -1, 1, 2])
                        gene["x"] = max(0, min(max_x, gene["x"] + dx))
                        gene["y"] = max(0, min(max_y, gene["y"] + dy))
                    else:
                        # lompat koordinat acak untuk eksplorasi luas
                        gene["x"] = random.randint(0, max_x)
                        gene["y"] = random.randint(0, max_y)

            elif m_type == 2 and len(loaded_ids) > 0:
                # putar orientasi mobil horizontal <-> vertical
                target_id = random.choice(loaded_ids)
                v = v_map[target_id]
                gene = individual.genes[target_id]
                if gene["ship_id"] is None or gene["ship_id"] not in individual.ship_map:
                    continue
                target_ship = individual.ship_map[gene["ship_id"]]

                if gene["orientation"] == "vertical":
                    new_orient = "horizontal"
                    nw = v.l
                    nl = v.w
                else:
                    new_orient = "vertical"
                    nw = v.w
                    nl = v.l

                max_x = target_ship.w - nw
                max_y = target_ship.l - nl
                if max_x >= 0 and max_y >= 0:
                    gene["orientation"] = new_orient
                    if gene["x"] > max_x:
                        gene["x"] = max_x
                    if gene["y"] > max_y:
                        gene["y"] = max_y

            elif m_type == 3 and len(loaded_ids) > 0 and len(unloaded_ids) > 0:
                # tukar mobil loaded dengan mobil unplaced yang punya fee lebih gede
                unloaded_cand = random.choice(unloaded_ids)
                v_un = v_map[unloaded_cand]

                cheaper_loaded = []
                for lid in loaded_ids:
                    if v_map[lid].shipping_fee < v_un.shipping_fee:
                        cheaper_loaded.append(lid)

                if len(cheaper_loaded) > 0:
                    target_loaded = random.choice(cheaper_loaded)
                    g_loaded = individual.genes[target_loaded]
                    g_un = individual.genes[unloaded_cand]

                    # berikan koordinat mobil lama ke mobil yang fee-nya lebih tinggi
                    g_un["ship_id"] = g_loaded["ship_id"]
                    g_un["x"] = g_loaded["x"]
                    g_un["y"] = g_loaded["y"]
                    g_un["orientation"] = g_loaded["orientation"]
                    g_loaded["is_loaded"] = False
                    g_loaded["ship_id"] = None
                    g_loaded["x"] = -1
                    g_loaded["y"] = -1

                    # update list tracking agar loop berikutnya tidak ambil gen yang baru dimatikan
                    if target_loaded in loaded_ids:
                        loaded_ids.remove(target_loaded)
                    unloaded_ids.append(target_loaded)
                    if unloaded_cand in unloaded_ids:
                        unloaded_ids.remove(unloaded_cand)
                    loaded_ids.append(unloaded_cand)

            elif m_type == 4 and len(individual.ships) > 1 and len(loaded_ids) > 0:
                # pindah kapal untuk armada multi-kapal
                target_id = random.choice(loaded_ids)
                v = v_map[target_id]
                gene = individual.genes[target_id]
                if gene["ship_id"] is None or gene["ship_id"] not in individual.ship_map:
                    continue

                other_ships = []
                for s in individual.ships:
                    if s.id != gene["ship_id"]:
                        other_ships.append(s)

                if len(other_ships) > 0:
                    dest = random.choice(other_ships)
                    orient = gene["orientation"]
                    if orient == "vertical":
                        w = v.w
                        l = v.l
                    else:
                        w = v.l
                        l = v.w

                    max_x = dest.w - w
                    max_y = dest.l - l
                    if max_x >= 0 and max_y >= 0:
                        gene["ship_id"] = dest.id
                        gene["x"] = random.randint(0, max_x)
                        gene["y"] = random.randint(0, max_y)

    # evaluasi ulang dulu setelah permutasi gen
    individual.evaluate()

    # lakukan penyisipan agresif untuk mengisi sisa ruang di geladak
    fill_empty_slots(individual)


def get_elites(population, elite_count=2):
    count = min(elite_count, len(population))
    sorted_pop = list(population)
    sorted_pop.sort(key=lambda ind: ind.fitness, reverse=True)
    
    # simpan individu terbaik agar solusinya tidak hilang pas evolusi
    elites = []
    for i in range(count):
        elites.append(sorted_pop[i].clone())
        
    return elites


def individual_from_armada(armada):
    # ekstrak state armada yang ada di GUI menjadi individu GA (seeding)
    ships = list(armada.ship_list)
    vehicles = armada.list_all_vehicles
    ind = Individual(vehicles, ships)
    
    for v in vehicles:
        found_ship = None
        for s in ships:
            if v in s.list_vehicles_in_ship:
                found_ship = s
                break
                
        if found_ship is not None and v.coor != [-1, -1]:
            ind.genes[v.id] = {
                "ship_id": found_ship.id,
                "is_loaded": True,
                "x": v.coor[0],
                "y": v.coor[1],
                "orientation": v.orientation
            }
        else:
            # kalau belum muat di kapal awal, tandai koordinat -1 dan ship_id None agar tidak bentrok di geladak
            ind.genes[v.id] = {
                "ship_id": None,
                "is_loaded": False,
                "x": -1,
                "y": -1,
                "orientation": v.orientation
            }
            
    ind.evaluate()
    return ind


def run_genetic_algorithm(armada_or_vehicles, ship_w=None, ship_l=None, max_capacity=None, pop_size=50, generations=100, crossover_rate=0.8, mutation_rate=0.3, elite_count=2, on_iteration=None):
    start_time = time.time()
    
    # normalisasi input: bisa menerima objek Armada langsung atau parameter kapal satuan
    if isinstance(armada_or_vehicles, Armada):
        ships = list(armada_or_vehicles.ship_list)
        vehicles = armada_or_vehicles.list_all_vehicles
        # jika parameter dikirim posisi run_genetic_algorithm(armada, pop_size, generations)
        if isinstance(ship_w, int):
            pop_size = ship_w
        if isinstance(ship_l, int):
            generations = ship_l
    else:
        vehicles = armada_or_vehicles
        ships = [Ship(w=ship_w, l=ship_l, max_capacity=max_capacity, id="S1")]
        
    population = []
    
    # jika input berupa objek armada aktif, sertakan sebagai seed awal agar fee GA bersambung
    reference_individual = None
    if isinstance(armada_or_vehicles, Armada):
        seed_ind = individual_from_armada(armada_or_vehicles)
        reference_individual = seed_ind.clone()
        population.append(seed_ind)
        
    while len(population) < pop_size:
        ind = Individual(vehicles, ships)
        ind.randomize()
        population.append(ind)
        
    population.sort(key=lambda ind: ind.fitness, reverse=True)
    initial_state = population[0].clone()
    
    # simpan seluruh armada pada generasi awal terurut dari peringkat terbaik
    initial_armadas = []
    for ind in population:
        initial_armadas.append(ind.to_armada())
    
    history_max = []
    history_avg = []
    
    last_best_fitness = population[0].fitness
    stagnant_generations = 0
    
    for gen_idx in range(generations):
        # rekap fitness max dan rata-rata generasi ini untuk data grafik
        current_max = population[0].fitness
        total_fitness = 0.0
        for ind in population:
            total_fitness = total_fitness + ind.fitness
            if ind.fitness > current_max:
                current_max = ind.fitness
        
        current_avg = total_fitness / len(population)
        history_max.append(current_max)
        history_avg.append(current_avg)
        
        # deteksi stagnasi untuk memicu mutasi adaptif
        if current_max > last_best_fitness:
            last_best_fitness = current_max
            stagnant_generations = 0
        else:
            stagnant_generations = stagnant_generations + 1
            
        if stagnant_generations >= 3:
            is_stagnant = True
        else:
            is_stagnant = False
        
        if on_iteration is not None:
            current_best_armada = population[0].to_armada()
            on_iteration(gen_idx + 1, current_max, current_avg, current_best_armada)
        
        elite_count_actual = max(1, elite_count)
        new_population = get_elites(population, elite_count_actual)
        
        while len(new_population) < pop_size:
            parent1 = tournament_selection(population, k=3)
            parent2 = tournament_selection(population, k=3)
            
            child = crossover(parent1, parent2, crossover_rate)
            mutate(child, mutation_rate, is_stagnant=is_stagnant)
            new_population.append(child)
            
        population = new_population
        population.sort(key=lambda ind: ind.fitness, reverse=True)
    final_avg = sum(ind.fitness for ind in population) / len(population)
    history_max.append(population[0].fitness)
    history_avg.append(final_avg)
    if on_iteration is not None:
        on_iteration(generations + 1, population[0].fitness, final_avg, population[0].to_armada())

    duration = time.time() - start_time
    final_state = population[0].clone()
    
    # simpan seluruh armada pada generasi akhir terurut dari peringkat terbaik
    final_armadas = []
    for ind in population:
        final_armadas.append(ind.to_armada())
    
    return {
        "initial_state": initial_state,
        "final_state": final_state,
        "best_fitness": final_state.fitness,
        "duration": duration,
        "history_max": history_max,
        "history_avg": history_avg,
        "pop_size": pop_size,
        "generations": generations,
        "armada": final_state.to_armada(),
        "initial_armadas": initial_armadas,
        "final_armadas": final_armadas,
        "reference_state": reference_individual
    }


def genetic_algorithm(armada, pop_size=50, generations=100, on_iteration=None):
    # wrapper yang cocok dengan interface GUI_app (mengembalikan tuple armada, fee, history)
    res = run_genetic_algorithm(armada, pop_size=pop_size, generations=generations, on_iteration=on_iteration)
    final_armada = res["armada"]
    final_fee = res["best_fitness"]
    history = res["history_max"]
    return final_armada, final_fee, history


def format_grid_to_string(grid):
    lines = []
    for row in grid:
        lines.append(" ".join(row))
    return "\n".join(lines)


def get_vehicle_lists_string(individual):
    lines = []
    for s in individual.ships:
        in_ship = []
        for v in individual.vehicles:
            gene = individual.genes.get(v.id)
            if gene is not None and gene["is_loaded"] and gene["ship_id"] == s.id:
                in_ship.append(f"{v.id}(fee:{v.shipping_fee}, w:{v.weight})")
        if len(in_ship) > 0:
            ship_str = ", ".join(in_ship)
        else:
            ship_str = "-"
        lines.append(f"Kendaraan di Kapal {s.id} ({len(in_ship)}):\n  {ship_str}")
        
    unplaced = []
    for v in individual.vehicles:
        gene = individual.genes.get(v.id)
        if gene is None or not gene["is_loaded"] or gene["ship_id"] is None:
            unplaced.append(f"{v.id}(fee:{v.shipping_fee}, w:{v.weight})")
            
    if len(unplaced) > 0:
        unplaced_str = ", ".join(unplaced)
    else:
        unplaced_str = "-"
    lines.append(f"Kendaraan di Luar Kapal ({len(unplaced)}):\n  {unplaced_str}")
    return "\n".join(lines)


def run_benchmark_experiments(on_progress=None, output_dir="output"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    csv_path = os.path.join(output_dir, "rekap_eksperimen_ga.csv")
    txt_path = os.path.join(output_dir, "rekap_eksperimen_ga.txt")
    state_path = os.path.join(output_dir, "visualisasi_state_ga.txt")

    csv_file = open(csv_path, "w", encoding="utf-8")
    csv_file.write("Eksperimen,Populasi,Iterasi,Run,Durasi_Detik,Fitness_Awal,Fitness_Akhir\n")

    txt_file = open(txt_path, "w", encoding="utf-8")
    txt_file.write("Eksperimen\tPopulasi\tIterasi\tRun\tDurasi(detik)\tFitness_Awal\tFitness_Akhir\n")

    state_file = open(state_path, "w", encoding="utf-8")

    def emit(msg):
        print(msg)
        if on_progress is not None:
            on_progress(msg)

    # Eksperimen 1: populasi kontrol (50), variasi iterasi (50, 100, 200)
    pop_kontrol = 50
    variasi_iterasi = [50, 100, 200]

    emit("Memulai Eksperimen 1: Populasi Kontrol (Populasi = 50)")
    for iterasi in variasi_iterasi:
        for run_idx in range(1, 4):
            emit(f"Exp 1 | Populasi: {pop_kontrol} | Iterasi: {iterasi} | Run ke-{run_idx}...")
            
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
            
            fig = plt.figure(figsize=(7, 4))
            ax = fig.add_subplot(111)
            ax.plot(hasil["history_max"], label="Fitness Maksimum")
            ax.plot(hasil["history_avg"], label="Rata-rata Populasi", linestyle="--")
            ax.set_title(f"Eksperimen 1: Pop={pop_kontrol}, Iter={iterasi} (Run {run_idx})")
            ax.set_xlabel("Iterasi")
            ax.set_ylabel("Shipping Fee")
            ax.legend()
            ax.grid(True)
            fig.tight_layout()
            
            plot_path = os.path.join(output_dir, f"exp1_iter{iterasi}_run{run_idx}.png")
            fig.savefig(plot_path)
            plt.close(fig)

    # Eksperimen 2: iterasi kontrol (100), variasi populasi (20, 50, 100)
    iter_kontrol = 100
    variasi_populasi = [20, 50, 100]

    emit("\nMemulai Eksperimen 2: Iterasi Kontrol (Iterasi = 100)")
    for pop in variasi_populasi:
        for run_idx in range(1, 4):
            emit(f"Exp 2 | Populasi: {pop} | Iterasi: {iter_kontrol} | Run ke-{run_idx}...")
            
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
            
            fig = plt.figure(figsize=(7, 4))
            ax = fig.add_subplot(111)
            ax.plot(hasil["history_max"], label="Fitness Maksimum")
            ax.plot(hasil["history_avg"], label="Rata-rata Populasi", linestyle="--")
            ax.set_title(f"Eksperimen 2: Pop={pop}, Iter={iter_kontrol} (Run {run_idx})")
            ax.set_xlabel("Iterasi")
            ax.set_ylabel("Shipping Fee")
            ax.legend()
            ax.grid(True)
            fig.tight_layout()
            
            plot_path = os.path.join(output_dir, f"exp2_pop{pop}_run{run_idx}.png")
            fig.savefig(plot_path)
            plt.close(fig)

    csv_file.close()
    txt_file.close()
    state_file.close()
    emit("\nSeluruh 18 eksperimen selesai dijalankan. Hasil tersimpan di folder output/.")


if __name__ == "__main__":
    run_benchmark_experiments()

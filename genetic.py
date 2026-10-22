import random
import time
from starter import Vehicle, list_vehicles

class Individual:
    def __init__(self, vehicles, ship_w, ship_l, max_capacity):
        self.vehicles = vehicles
        self.ship_w = ship_w
        self.ship_l = ship_l
        self.max_capacity = max_capacity
        
        self.genes = {}
        self.fitness = 0.0
        self.total_weight = 0

    def randomize(self):
        # acak urutan mobil agar penataan tiap individu beda-beda
        shuffled = list(self.vehicles)
        random.shuffle(shuffled)
        
        grid = []
        for _ in range(self.ship_w):
            baris = [0] * self.ship_l
            grid.append(baris)
            
        current_weight = 0
        
        for v in shuffled:
            orientation = random.choice(["horizontal", "vertical"])
            if orientation == "vertical":
                w = v.w
                l = v.l
            else:
                w = v.l
                l = v.w
            
            placed = False
            if current_weight + v.weight <= self.max_capacity:
                if w <= self.ship_w and l <= self.ship_l:
                    max_x = self.ship_w - w
                    max_y = self.ship_l - l
                    
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
                                "is_loaded": True,
                                "x": rx,
                                "y": ry,
                                "orientation": orientation
                            }
                            current_weight = current_weight + v.weight
                            placed = True
                            break
            
            if not placed:
                self.genes[v.id] = {
                    "is_loaded": False,
                    "x": -1,
                    "y": -1,
                    "orientation": orientation
                }
                
        self.total_weight = current_weight
        total_fee = 0.0
        for vid, g in self.genes.items():
            if g["is_loaded"]:
                for v in self.vehicles:
                    if v.id == vid:
                        total_fee = total_fee + v.shipping_fee
                        break
        self.fitness = total_fee

    def evaluate(self):
        grid = []
        for _ in range(self.ship_w):
            baris = [0] * self.ship_l
            grid.append(baris)
            
        total_fee = 0.0
        current_weight = 0

        # prioritaskan mobil fee mahal masuk duluan jika ada tabrakan sel
        candidate_vehicles = []
        for v in self.vehicles:
            gene = self.genes.get(v.id)
            if gene is not None:
                if gene["is_loaded"]:
                    candidate_vehicles.append(v)
                    
        candidate_vehicles.sort(key=lambda item: item.shipping_fee, reverse=True)

        for v in candidate_vehicles:
            gene = self.genes[v.id]
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
            if (x + w) > self.ship_w or (y + l) > self.ship_l:
                gene["is_loaded"] = False
                continue

            if current_weight + v.weight > self.max_capacity:
                gene["is_loaded"] = False
                continue

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

    def get_grid(self):
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
        return grid

    def display(self):
        grid = self.get_grid()
        print(f"Total Fitness: {self.fitness}")
        print(f"Total Weight : {self.total_weight}/{self.max_capacity}")
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

    child = Individual(parent1.vehicles, parent1.ship_w, parent1.ship_l, parent1.max_capacity)
    
    # peluang 50:50 ambil gen dari parent1 atau parent2
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

    return child


def mutate(individual, mutation_rate=0.2):
    if random.random() > mutation_rate:
        return

    loaded_ids = []
    unloaded_ids = []
    for vid, state in individual.genes.items():
        if state["is_loaded"]:
            loaded_ids.append(vid)
        else:
            unloaded_ids.append(vid)

    v_map = {}
    for v in individual.vehicles:
        v_map[v.id] = v

    mutation_type = random.randint(1, 4)

    if mutation_type == 1 and len(loaded_ids) > 0:
        # geser koordinat mobil di kapal
        target_id = random.choice(loaded_ids)
        v = v_map[target_id]
        orientation = individual.genes[target_id]["orientation"]
        if orientation == "vertical":
            w = v.w
            l = v.l
        else:
            w = v.l
            l = v.w
            
        max_x = individual.ship_w - w
        max_y = individual.ship_l - l
        if max_x >= 0 and max_y >= 0:
            individual.genes[target_id]["x"] = random.randint(0, max_x)
            individual.genes[target_id]["y"] = random.randint(0, max_y)

    elif mutation_type == 2 and len(loaded_ids) > 0:
        # putar orientasi mobil horizontal <-> vertical
        target_id = random.choice(loaded_ids)
        v = v_map[target_id]
        current_orient = individual.genes[target_id]["orientation"]
        if current_orient == "vertical":
            new_orient = "horizontal"
            new_w = v.l
            new_l = v.w
        else:
            new_orient = "vertical"
            new_w = v.w
            new_l = v.l
            
        max_x = individual.ship_w - new_w
        max_y = individual.ship_l - new_l
        if max_x >= 0 and max_y >= 0:
            individual.genes[target_id]["orientation"] = new_orient
            cur_x = individual.genes[target_id]["x"]
            cur_y = individual.genes[target_id]["y"]
            if cur_x > max_x:
                individual.genes[target_id]["x"] = max_x
            if cur_y > max_y:
                individual.genes[target_id]["y"] = max_y

    elif mutation_type == 3 and len(unloaded_ids) > 0:
        # coba naikin mobil dari luar kapal
        target_id = random.choice(unloaded_ids)
        v = v_map[target_id]
        orientation = random.choice(["horizontal", "vertical"])
        if orientation == "vertical":
            w = v.w
            l = v.l
        else:
            w = v.l
            l = v.w
            
        max_x = individual.ship_w - w
        max_y = individual.ship_l - l
        if max_x >= 0 and max_y >= 0:
            individual.genes[target_id]["is_loaded"] = True
            individual.genes[target_id]["orientation"] = orientation
            individual.genes[target_id]["x"] = random.randint(0, max_x)
            individual.genes[target_id]["y"] = random.randint(0, max_y)

    elif mutation_type == 4 and len(loaded_ids) > 0 and len(unloaded_ids) > 0:
        # tukar posisi mobil dalam kapal dengan mobil di luar kapal
        in_id = random.choice(loaded_ids)
        out_id = random.choice(unloaded_ids)
        old_x = individual.genes[in_id]["x"]
        old_y = individual.genes[in_id]["y"]
        orient = individual.genes[in_id]["orientation"]
        
        individual.genes[in_id]["is_loaded"] = False
        individual.genes[in_id]["x"] = -1
        individual.genes[in_id]["y"] = -1
        
        v_out = v_map[out_id]
        if orient == "vertical":
            w = v_out.w
            l = v_out.l
        else:
            w = v_out.l
            l = v_out.w
        if (old_x + w) <= individual.ship_w and (old_y + l) <= individual.ship_l:
            individual.genes[out_id]["is_loaded"] = True
            individual.genes[out_id]["x"] = old_x
            individual.genes[out_id]["y"] = old_y
            individual.genes[out_id]["orientation"] = orient


def get_elites(population, elite_count=2):
    count = min(elite_count, len(population))
    sorted_pop = list(population)
    sorted_pop.sort(key=lambda ind: ind.fitness, reverse=True)
    
    # simpan individu terbaik agar solusinya tidak hilang pas evolusi
    elites = []
    for i in range(count):
        elites.append(sorted_pop[i].clone())
        
    return elites


def run_genetic_algorithm(vehicles, ship_w, ship_l, max_capacity, pop_size=50, generations=100, crossover_rate=0.8, mutation_rate=0.2, elite_count=2):
    start_time = time.time()
    
    population = []
    for _ in range(pop_size):
        ind = Individual(vehicles, ship_w, ship_l, max_capacity)
        ind.randomize()
        population.append(ind)
        
    population.sort(key=lambda ind: ind.fitness, reverse=True)
    initial_state = population[0].clone()
    
    history_max = []
    history_avg = []
    
    for _ in range(generations):
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
        
        new_population = get_elites(population, elite_count)
        
        while len(new_population) < pop_size:
            parent1 = tournament_selection(population, k=3)
            parent2 = tournament_selection(population, k=3)
            
            child = crossover(parent1, parent2, crossover_rate)
            mutate(child, mutation_rate)
            child.evaluate()
            new_population.append(child)
            
        population = new_population
        population.sort(key=lambda ind: ind.fitness, reverse=True)
        
    duration = time.time() - start_time
    final_state = population[0].clone()
    
    return {
        "initial_state": initial_state,
        "final_state": final_state,
        "best_fitness": final_state.fitness,
        "duration": duration,
        "history_max": history_max,
        "history_avg": history_avg,
        "pop_size": pop_size,
        "generations": generations
    }


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


if __name__ == "__main__":
    ind1 = Individual(list_vehicles, ship_w=10, ship_l=20, max_capacity=200)
    ind1.randomize()
    print("=== INDIVIDU 1 ===")
    ind1.display()

    print("\n=== UJI INDEPENDENSI STATE (CLONE) ===")
    ind2 = ind1.clone()
    
    # ubah salah satu koordinat gen di ind1
    target_id = list_vehicles[0].id
    ind1.genes[target_id]["x"] = 999
    
    print(f"Koordinat x mobil '{target_id}' di ind1: {ind1.genes[target_id]['x']}")
    print(f"Koordinat x mobil '{target_id}' di ind2 (harus tetap asli): {ind2.genes[target_id]['x']}")

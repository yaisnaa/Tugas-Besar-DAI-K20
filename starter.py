import random
import string
import numpy as np

class Vehicle:
    id_list = set()
    def __init__(self, id: str, w: int, l: int, orientation: str, shipping_fee: float, weight: int, eta: int, coor=[-1,-1]):
        if id in self.id_list:
            raise ValueError("udah ada id nya, ganti")
        self.id = id
        self.w = w
        self.l = l
        self.orientation = orientation
        self.shipping_fee = shipping_fee
        self.weight = weight
        self.eta = eta
        self.id_list.add(self.id)
        self.coor = coor
    
    def __str__(self) -> str:
        return f"{self.id}"

    def __repr__(self) -> str:
         return f"\033[92m{self.id}\033[0m"
class Ship:
    def __init__(self, w: int, l: int, max_capacity: int):
        self.w = w
        self.l = l
        self.max_capacity = max_capacity
        # Initialize with None properly
        self.ship_matrix = np.full((w, l), 0, dtype=object)
    
    def is_coor_filled(self, x_coor, y_coor) -> bool:
        if x_coor >= self.w or x_coor < 0:
            return True
        if y_coor >= self.l or y_coor < 0:
            return True
        if self.ship_matrix[x_coor, y_coor] != 0:
            return True
        return False
    
    def is_space_filled(self, w, l, start_x_coor, start_y_coor):
       

        for x_coor in range(w):
            for y_coor in range(l):
                if self.is_coor_filled(start_x_coor + x_coor, start_y_coor + y_coor): 
                    return True
        return False
    
    def calculate_shipping_fee(self):
        sum_shipping_fee = 0
        seen_vehicles = set()
        for x_coor in range(self.w):
            for y_coor in range(self.l):
                if self.is_coor_filled(x_coor, y_coor):
                    vehicle = self.ship_matrix[x_coor, y_coor]
                    if vehicle.id not in seen_vehicles:
                        sum_shipping_fee += vehicle.shipping_fee
                        seen_vehicles.add(vehicle.id)
        return sum_shipping_fee
    
    def inputing_ship(self, vehicle: "Vehicle", start_x_coor, start_y_coor) -> str:
       
       
        true_w = vehicle.w if vehicle.orientation == "vertical" else vehicle.l
        true_l = vehicle.l if vehicle.orientation == "vertical" else vehicle.w
        
        if self.is_space_filled(true_w, true_l, start_x_coor, start_y_coor): 
            return "gagal input"
            
        for x_coor in range(true_w):
            for y_coor in range(true_l):
                self.ship_matrix[start_x_coor + x_coor, start_y_coor + y_coor] = vehicle
        
        vehicle.coor = [start_x_coor, start_y_coor]
        return "sukses"
    
    def display(self):
        for row in self.ship_matrix:
            print(" ".join(str(cell) for cell in row))

def randomize_initial_state(ship: "Ship", vehicles: list, max_attempts: int = 100, seed=None):
    """
    State awal hill climbing: tiap vehicle dicoba ditaruh di posisi & orientasi acak.
    Urutan vehicle diacak, tiap vehicle dicoba max_attempts kali sampai muat
    (inputing_ship sudah menolak overlap / keluar batas).
    Return (placed, unplaced).
    """
    rng = random.Random(seed)
    order = list(vehicles)
    rng.shuffle(order)

    placed, unplaced = [], []
    for vehicle in order:
        success = False
        for _ in range(max_attempts):
            vehicle.orientation = rng.choice(["vertical", "horizontal"])
            start_x = rng.randrange(ship.w)
            start_y = rng.randrange(ship.l)
            if ship.inputing_ship(vehicle, start_x, start_y) == "sukses":
                success = True
                break
        if success:
            placed.append(vehicle)
        else:
            vehicle.coor = [-1, -1]
            unplaced.append(vehicle)
    return placed, unplaced

def place_vehicle_anywhere(ship: "Ship", vehicle: "Vehicle") -> bool:
    """Scan seluruh posisi & kedua orientasi, taruh di tempat pertama yang muat."""
    original = vehicle.orientation
    for orientation in ("vertical", "horizontal"):
        vehicle.orientation = orientation
        for x in range(ship.w):
            for y in range(ship.l):
                if ship.inputing_ship(vehicle, x, y) == "sukses":
                    return True
    vehicle.orientation = original
    return False

def fill_ship_until_full(ship: "Ship", vehicles: list):
    """
    Masukkan kendaraan satu per satu sampai kapal penuh, yaitu tidak ada lagi
    kendaraan tersisa yang muat. Vehicle yang tidak muat dilewati (bisa saja
    vehicle berikutnya yang lebih kecil masih muat).
    Return (placed, unplaced).
    """
    placed, unplaced = [], []
    for vehicle in vehicles:
        if place_vehicle_anywhere(ship, vehicle):
            placed.append(vehicle)
        else:
            unplaced.append(vehicle)
    return placed, unplaced

if __name__ == "__main__":
    ship1 = Ship(w=10, l=20, max_capacity=10)

    vehicles = [
        Vehicle(id=string.ascii_letters[i], w=random.randint(1, 3), l=random.randint(2, 4),
                orientation="vertical", shipping_fee=random.randint(10, 50),
                weight=random.randint(5, 20), eta=random.randint(1, 10))
        for i in range(26)
    ]

    # state awal acak untuk hill climbing
    placed, unplaced = randomize_initial_state(ship1, vehicles, seed=42)

    ship1.display()
    print(f"placed: {len(placed)}, unplaced: {len(unplaced)}")
    print(f"total shipping fee: {ship1.calculate_shipping_fee()}")

    # alternatif: isi kapal sampai penuh (deterministik)
    # ship2 = Ship(w=10, l=20, max_capacity=10)
    # placed, unplaced = fill_ship_until_full(ship2, vehicles)

# catatan: koordinat masih array, x = vertikal (baris), y = horizontal (kolom)

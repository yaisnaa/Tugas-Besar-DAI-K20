import numpy as np
import random
import copy
class Vehicle:
    def __init__(self, id: str, w: int, l: int, shipping_fee: float, weight: int, eta: int, coor=None, orientation="vertical"):
        self.id = id
        self.w = w
        self.l = l
        self.orientation = orientation
        self.shipping_fee = shipping_fee
        self.weight = weight
        self.eta = eta
        if coor is None:
            self.coor = [-1, -1]
        else:
            self.coor = [coor[0], coor[1]]

    def __str__(self) -> str:
        return f"{self.id}"

    def __repr__(self) -> str:
        return f"{self.id}"


class Ship:
    def __init__(self, w: int, l: int, max_capacity: int, id: str, list_vehicles_in_ship=None):
        self.w = w
        self.l = l
        self.max_capacity = max_capacity
        self.ship_matrix = np.full((w, l), 0, dtype=object)
        self.id = id
        if list_vehicles_in_ship is None:
            self.list_vehicles_in_ship = set()
        else:
            self.list_vehicles_in_ship = set(list_vehicles_in_ship)
    
    def __str__(self) -> str:
        return f"Ship(id='{self.id}')"

    def __repr__(self) -> str:
        return f"Ship(id='{self.id}')"

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
    
    def calculate_shipping_fee(self) -> float:
        sum_shipping_fee = 0
        for vehicle in self.list_vehicles_in_ship:
            sum_shipping_fee += vehicle.shipping_fee
        return sum_shipping_fee
    
    def calculate_ship_weight(self):
        sum_ship_weight = 0
        for vehicle in self.list_vehicles_in_ship:
            sum_ship_weight += vehicle.weight
        return sum_ship_weight
    
    def is_ship_full(self, vehicle: Vehicle) -> bool:
        return self.calculate_ship_weight() + vehicle.weight > self.max_capacity
    
    def inputing_vehicle_success(self, vehicle: Vehicle, start_x_coor, start_y_coor) -> bool:
        true_w = vehicle.w if vehicle.orientation == "vertical" else vehicle.l
        true_l = vehicle.l if vehicle.orientation == "vertical" else vehicle.w
        
        if self.is_space_filled(true_w, true_l, start_x_coor, start_y_coor) or self.is_ship_full(vehicle): 
            return False
            
        for x_coor in range(true_w):
            for y_coor in range(true_l):
                self.ship_matrix[start_x_coor + x_coor, start_y_coor + y_coor] = vehicle
        
        vehicle.coor = [start_x_coor, start_y_coor]
        self.list_vehicles_in_ship.add(vehicle)
        return True
    
    def random_state_ship(self, vehicles: list[Vehicle]):
        unplaced_vehicles = list(vehicles)
        
        attempts = 0
        max_attempts = 100
        options = ["vertical", "horizontal"]
        
        while len(unplaced_vehicles) != 0 and attempts < max_attempts:
            attempts += 1
            
            selected_vehicle = random.choice(unplaced_vehicles)
            orientation_of_vehicle = random.choice(options)

            selected_vehicle.orientation = orientation_of_vehicle
            
            random_x = random.randrange(0, self.w)
            random_y = random.randrange(0, self.l)
        
            if self.inputing_vehicle_success(selected_vehicle, random_x, random_y):
                unplaced_vehicles.remove(selected_vehicle)
                attempts = 0 
        return unplaced_vehicles

    def remove_vehicle_success(self, vehicle: Vehicle) -> bool:
        if vehicle not in self.list_vehicles_in_ship or vehicle.coor == [-1, -1]:
            return False
        true_w = vehicle.w if vehicle.orientation == "vertical" else vehicle.l
        true_l = vehicle.l if vehicle.orientation == "vertical" else vehicle.w
            
        for x_coor in range(true_w):
            for y_coor in range(true_l):
                self.ship_matrix[vehicle.coor[0] + x_coor, vehicle.coor[1] + y_coor] = 0
        
        vehicle.coor = [-1, -1]
        self.list_vehicles_in_ship.discard(vehicle)
        return True

    def change_orientation_success(self, vehicle: Vehicle) -> bool:
        if vehicle not in self.list_vehicles_in_ship or vehicle.coor == [-1, -1]:
            return False
        
        original_orientation = vehicle.orientation
        x_coor = vehicle.coor[0]
        y_coor = vehicle.coor[1]
        self.remove_vehicle_success(vehicle)
        vehicle.orientation = "vertical" if vehicle.orientation == "horizontal" else "horizontal"

        if self.inputing_vehicle_success(vehicle, x_coor, y_coor):
            return True
        
        vehicle.orientation = original_orientation
        self.inputing_vehicle_success(vehicle, x_coor, y_coor)
        return False
    
    def move_vehicle_success(self, vehicle: Vehicle) -> bool:
        if vehicle not in self.list_vehicles_in_ship or vehicle.coor == [-1, -1]:
            return False

        old_x, old_y = vehicle.coor

        new_coor_x = random.randrange(0, self.w)
        new_coor_y = random.randrange(0, self.l)

        self.remove_vehicle_success(vehicle)

        if self.inputing_vehicle_success(vehicle, new_coor_x, new_coor_y):
            return True
       
        self.inputing_vehicle_success(vehicle, old_x, old_y)
        return False

    def switch_vehicles_success(self, vehicle_a: Vehicle, vehicle_b: Vehicle) -> bool: 
        in_a = vehicle_a in self.list_vehicles_in_ship
        in_b = vehicle_b in self.list_vehicles_in_ship
        
        if not in_a and not in_b:
            return False
        
        coor_a = list(vehicle_a.coor)
        coor_b = list(vehicle_b.coor)
        
        if in_a:
            self.remove_vehicle_success(vehicle_a)
        if in_b:
            self.remove_vehicle_success(vehicle_b)
            
        ok_a = (not in_b) or self.inputing_vehicle_success(vehicle_a, *coor_b)
        ok_b = ok_a and ((not in_a) or self.inputing_vehicle_success(vehicle_b, *coor_a))
        
        if ok_a and ok_b:
            return True
            
        if in_b:
            self.remove_vehicle_success(vehicle_a)
        if in_a:
            self.remove_vehicle_success(vehicle_b)
        if in_a:
            self.inputing_vehicle_success(vehicle_a, *coor_a)
        if in_b:
            self.inputing_vehicle_success(vehicle_b, *coor_b)
        return False

    def display(self):
        for row in self.ship_matrix:
            row_str = ""
            for cell in row:
                if cell == 0:
                    row_str += "0 "
                else:
                    row_str += f"\033[92m{cell.id}\033[0m "
            print(f"[{row_str.strip()}]")


class Armada:
    def __init__(self, ship_list: set, list_all_vehicles):
        self.ship_list = ship_list
        self.list_all_vehicles = list(list_all_vehicles)
    
    def calculate_armada_shipping_fee(self) -> int:
        sum_shipping_fee = 0
        for ship in self.ship_list:
            sum_shipping_fee += ship.calculate_shipping_fee()
        return sum_shipping_fee
    
    def random_state_armada(self, list_vehicles: list[Vehicle]):
        unplaced = list(list_vehicles)
        for ship in self.ship_list:
            unplaced = ship.random_state_ship(unplaced)
        return unplaced

    def switch_vehicle_success(self) -> bool:
        if len(self.ship_list) == 0:
            return False
        vehicle_a, vehicle_b = random.sample(self.list_all_vehicles, 2)
        ship_a = None
        ship_b = None
        for s in self.ship_list:
            if vehicle_a in s.list_vehicles_in_ship:
                ship_a = s
                break
        for s in self.ship_list:
            if vehicle_b in s.list_vehicles_in_ship:
                ship_b = s
                break
        if ship_a is None and ship_b is None:
            return False
        
        coor_a = list(vehicle_a.coor) 
        coor_b = list(vehicle_b.coor)
        
        # lepas dari kapal (kalau memang di kapal)
        if ship_a:
            ship_a.remove_vehicle_success(vehicle_a)
        if ship_b:
            ship_b.remove_vehicle_success(vehicle_b)

        ok_a = (ship_b is None) or ship_b.inputing_vehicle_success(vehicle_a, *coor_b)
        ok_b = ok_a and ((ship_a is None) or ship_a.inputing_vehicle_success(vehicle_b, *coor_a))
        if ok_a and ok_b:
            return True

        # gagal -> rollback
        if ship_b:
            ship_b.remove_vehicle_success(vehicle_a)
        if ship_a:
            ship_a.remove_vehicle_success(vehicle_b)
        if ship_a:
            ship_a.inputing_vehicle_success(vehicle_a, *coor_a)
        if ship_b:
            ship_b.inputing_vehicle_success(vehicle_b, *coor_b)
        return False
    
def generate_armada(n_vehicles=30, n_ships=2,
                    ship_w=(8, 12), ship_l=(15, 25), capacity=(150, 250),
                    vehicle_w=(2, 5), vehicle_l=(2, 5),
                    fee=(5, 60), weight=(8, 26), eta=(7, 15)) -> Armada:
    ships = [Ship(w=random.randint(*ship_w), l=random.randint(*ship_l),
                  max_capacity=random.randint(*capacity), id=f"S{i}")
             for i in range(1, n_ships + 1)]
    vehicles = [Vehicle(id=f"V{i}", w=random.randint(*vehicle_w), l=random.randint(*vehicle_l),
                        shipping_fee=random.randint(*fee), weight=random.randint(*weight),
                        eta=random.randint(*eta),
                        orientation=random.choice(["vertical", "horizontal"]))
                for i in range(1, n_vehicles + 1)]
    armada = Armada(set(ships), vehicles)
    armada.random_state_armada(vehicles)
    return armada

def global_optima(armada, n_samples = 5000, on_progress = None, report_every=100):
    work = copy.deepcopy(armada)
    vehicles = work.list_all_vehicles
    best_fee, best_armada = -1, None
    for i in range(1, n_samples + 1):
        for ship in work.ship_list:
            ship.ship_matrix[:] = 0
            ship.list_vehicles_in_ship.clear()
        for v in vehicles:
            v.coor = [-1, -1]
        work.random_state_armada(vehicles)
        fee = work.calculate_armada_shipping_fee()
        if fee > best_fee:
            best_fee = fee
            best_armada = copy.deepcopy(work)
        if on_progress and (i % report_every == 0 or i == n_samples):
                on_progress(i, best_fee)
    return best_fee, best_armada

if __name__ == "__main__":
    armada = generate_armada()
    for ship in armada.ship_list:
        print(f"=== SHIP {ship.id} ===")
        ship.display()
    print("Total fee:", armada.calculate_armada_shipping_fee())




S1 = Ship(w=8, l=20, max_capacity=214, id="S1")
S2 = Ship(w=12, l=25, max_capacity=163, id="S2")
ships = [S1,S2]

V1 = Vehicle(id="V1", w=3, l=5, shipping_fee=55, weight=26, eta=15, orientation="vertical")
V2 = Vehicle(id="V2", w=5, l=3, shipping_fee=5, weight=10, eta=8, orientation="horizontal")
V3 = Vehicle(id="V3", w=2, l=5, shipping_fee=5, weight=23, eta=12, orientation="vertical")
V4 = Vehicle(id="V4", w=5, l=4, shipping_fee=27, weight=19, eta=13, orientation="horizontal")
V5 = Vehicle(id="V5", w=4, l=2, shipping_fee=40, weight=25, eta=11, orientation="vertical")
V6 = Vehicle(id="V6", w=5, l=3, shipping_fee=46, weight=26, eta=11, orientation="horizontal")
V7 = Vehicle(id="V7", w=4, l=4, shipping_fee=34, weight=21, eta=8, orientation="vertical")
V8 = Vehicle(id="V8", w=5, l=2, shipping_fee=32, weight=24, eta=14, orientation="vertical")
V9 = Vehicle(id="V9", w=4, l=5, shipping_fee=41, weight=23, eta=15, orientation="horizontal")
V10 = Vehicle(id="V10", w=3, l=3, shipping_fee=57, weight=9, eta=15, orientation="vertical")
V11 = Vehicle(id="V11", w=5, l=5, shipping_fee=14, weight=23, eta=10, orientation="vertical")
V12 = Vehicle(id="V12", w=5, l=5, shipping_fee=50, weight=25, eta=11, orientation="horizontal")
V13 = Vehicle(id="V13", w=4, l=5, shipping_fee=56, weight=20, eta=13, orientation="vertical")
V14 = Vehicle(id="V14", w=4, l=4, shipping_fee=5, weight=9, eta=9, orientation="horizontal")
V15 = Vehicle(id="V15", w=5, l=4, shipping_fee=17, weight=16, eta=14, orientation="horizontal")
V16 = Vehicle(id="V16", w=5, l=5, shipping_fee=40, weight=9, eta=11, orientation="vertical")
V17 = Vehicle(id="V17", w=5, l=2, shipping_fee=33, weight=24, eta=11, orientation="vertical")
V18 = Vehicle(id="V18", w=3, l=5, shipping_fee=58, weight=23, eta=8, orientation="horizontal")
V19 = Vehicle(id="V19", w=5, l=4, shipping_fee=11, weight=14, eta=13, orientation="vertical")
V20 = Vehicle(id="V20", w=5, l=2, shipping_fee=10, weight=8, eta=14, orientation="vertical")
V21 = Vehicle(id="V21", w=3, l=3, shipping_fee=12, weight=9, eta=15, orientation="vertical")
V22 = Vehicle(id="V22", w=4, l=3, shipping_fee=5, weight=18, eta=14, orientation="horizontal")
V23 = Vehicle(id="V23", w=3, l=5, shipping_fee=42, weight=12, eta=15, orientation="vertical")
V24 = Vehicle(id="V24", w=2, l=5, shipping_fee=47, weight=13, eta=9, orientation="horizontal")
V25 = Vehicle(id="V25", w=5, l=5, shipping_fee=56, weight=12, eta=15, orientation="horizontal")
V26 = Vehicle(id="V26", w=5, l=2, shipping_fee=11, weight=20, eta=8, orientation="horizontal")
V27 = Vehicle(id="V27", w=4, l=4, shipping_fee=54, weight=8, eta=7, orientation="vertical")
V28 = Vehicle(id="V28", w=4, l=4, shipping_fee=33, weight=18, eta=8, orientation="horizontal")
V29 = Vehicle(id="V29", w=5, l=3, shipping_fee=14, weight=26, eta=15, orientation="horizontal")
V30 = Vehicle(id="V30", w=5, l=4, shipping_fee=34, weight=15, eta=8, orientation="horizontal")
V31 = Vehicle(id="V31", w=2, l=3, shipping_fee=46, weight=13, eta=7, orientation="horizontal")
V32 = Vehicle(id="V32", w=5, l=3, shipping_fee=35, weight=8, eta=9, orientation="vertical")
V33 = Vehicle(id="V33", w=3, l=3, shipping_fee=47, weight=13, eta=13, orientation="horizontal")
V34 = Vehicle(id="V34", w=5, l=5, shipping_fee=60, weight=10, eta=13, orientation="vertical")
V35 = Vehicle(id="V35", w=3, l=4, shipping_fee=16, weight=16, eta=14, orientation="horizontal")
V36 = Vehicle(id="V36", w=5, l=4, shipping_fee=34, weight=13, eta=12, orientation="horizontal")
V37 = Vehicle(id="V37", w=5, l=2, shipping_fee=38, weight=24, eta=11, orientation="horizontal")
V38 = Vehicle(id="V38", w=3, l=3, shipping_fee=5, weight=10, eta=14, orientation="horizontal")
V39 = Vehicle(id="V39", w=5, l=3, shipping_fee=6, weight=19, eta=9, orientation="vertical")
V40 = Vehicle(id="V40", w=3, l=2, shipping_fee=44, weight=16, eta=15, orientation="vertical")
V41 = Vehicle(id="V41", w=4, l=4, shipping_fee=47, weight=25, eta=9, orientation="vertical")
V42 = Vehicle(id="V42", w=4, l=2, shipping_fee=32, weight=13, eta=8, orientation="horizontal")
V43 = Vehicle(id="V43", w=4, l=3, shipping_fee=46, weight=11, eta=15, orientation="vertical")
V44 = Vehicle(id="V44", w=4, l=2, shipping_fee=23, weight=18, eta=9, orientation="horizontal")
V45 = Vehicle(id="V45", w=4, l=2, shipping_fee=5, weight=21, eta=11, orientation="horizontal")
V46 = Vehicle(id="V46", w=2, l=2, shipping_fee=11, weight=15, eta=7, orientation="vertical")
V47 = Vehicle(id="V47", w=2, l=2, shipping_fee=48, weight=25, eta=12, orientation="horizontal")
V48 = Vehicle(id="V48", w=5, l=2, shipping_fee=30, weight=18, eta=10, orientation="horizontal")
V49 = Vehicle(id="V49", w=5, l=2, shipping_fee=48, weight=19, eta=15, orientation="vertical")
V50 = Vehicle(id="V50", w=5, l=4, shipping_fee=57, weight=19, eta=7, orientation="vertical")

list_vehicles = [V1, V2, V3, V4, V5, V6, V7, V8, V9, V10,
            V11, V12, V13, V14, V15, V16, V17, V18, V19, V20,
            V21, V22, V23, V24, V25, V26, V27, V28, V29, V30,
            V31, V32, V33, V34, V35, V36, V37, V38, V39, V40,
            V41, V42, V43, V44, V45, V46, V47, V48, V49, V50]

armada = Armada(ships, list_vehicles)
armada.random_state_armada(list_vehicles)

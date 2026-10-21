import numpy as np
import random

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


if __name__ == "__main__":
    armada = generate_armada()
    for ship in armada.ship_list:
        print(f"=== SHIP {ship.id} ===")
        ship.display()
    print("Total fee:", armada.calculate_armada_shipping_fee())

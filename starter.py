import numpy as np

class Vehicle:
    id_list = set()
    def __init__(self, id: str, w: int, l: int, shipping_fee: float, weight: int, eta: int, coor=[-1,-1], orientation = "vertical"):
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
       
        return f"{self.id}"
    

class Ship:
    def __init__(self, w: int, l: int, max_capacity: int, id: str, list_vehicles_in_ship = set()):
        self.w = w
        self.l = l
        self.max_capacity = max_capacity
        self.ship_matrix = np.full((w, l), 0, dtype=object)
        self.id = id
        self.list_vehicles_in_ship = set()
    
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
        
        return self.calculate_ship_weight() + vehicle.weight >= self.max_capacity
    
    
    
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
    
    def random_state_ship(self, vehicles: set[Vehicle]):
        unplaced_vehicles = vehicles
        
        attempts = 0
        max_attempts = 100
        options = ["vertical", "horizontal"]
        
        while len(unplaced_vehicles) != 0 and attempts < max_attempts:
            attempts += 1
            
            
            selected_vehicle = np.random.choice(unplaced_vehicles)
            orientation_of_vehicle = np.random.choice(options)

            selected_vehicle.orientation = orientation_of_vehicle
            
            random_x = np.random.randint(0, self.w)
            random_y = np.random.randint(0, self.l)
        
            
            if self.inputing_vehicle_success(selected_vehicle, random_x, random_y):
                unplaced_vehicles.remove(selected_vehicle)
                attempts = 0 

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
        

    def change_orientation_success(self, vehicle: Vehicle):
        if vehicle not in self.list_vehicles_in_ship or vehicle.coor == [-1, -1]:
            return False
        
        original_orientation = vehicle.orientation
        x_coor = vehicle.coor[0]
        y_coor = vehicle.coor[1]
        vehicle.orientation = "vertical" if vehicle.orientation == "horizontal" else "horizontal"

        self.remove_vehicle_success(vehicle)
        if self.inputing_vehicle_success(vehicle, x_coor, y_coor):
            return True
        
        vehicle.orientation = original_orientation
        self.inputing_vehicle_success(vehicle, x_coor, y_coor)
        return False
    
    def move_vehicle_success(self, vehicle: Vehicle) -> bool:

        if vehicle not in self.list_vehicles_in_ship or vehicle.coor == [-1, -1]:
            return False

        old_x, old_y = vehicle.coor

        new_coor_x = np.random.randint(0, self.w)
        new_coor_y = np.random.randint(0, self.l)

        self.remove_vehicle(vehicle)

        if self.inputing_vehicle_success(vehicle, new_coor_x, new_coor_y):
            return True
       
        self.inputing_vehicle_success(vehicle, old_x, old_y)
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
    def __init__(self, ship_list: set):
        self.ship_list = ship_list
    
    def calculate_armada_shipping_fee(self) -> int:
        sum_shipping_fee = 0
        for ship in self.ship_list:
            sum_shipping_fee += ship.calculate_shipping_fee()

        return sum_shipping_fee
    
    def random_state_armada(Self, list_vehicles: set[Vehicle]):
        for ship in ship_list:
            ship.random_state_ship(list_vehicles)

    
    





    
    
    

ship1 = Ship(w=10, l=20, max_capacity=200, id = "f")
ship2 = Ship(w=10, l=20, max_capacity=200, id = "d")

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

ship1.random_state_ship(list_vehicles)
ship2.random_state_ship(list_vehicles)
ship_list = set()
ship_list.add(ship1)
ship_list.add(ship2)

ship1.display()
print(ship1.calculate_shipping_fee())

print(list_vehicles)
print(ship1.calculate_ship_weight())

ship2.display()
print(ship2.calculate_shipping_fee())

print(list_vehicles)
print(ship2.calculate_ship_weight())

armada1 = Armada(ship_list)
print(armada1.calculate_armada_shipping_fee())



# matriks mash bisa overlapp kalo lebih harusnya gagal input
# coordinat sistemnya masih array meaning x = vertikal y = horizontal
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
        print(self.ship_matrix)

ship1 = Ship(w=10, l=20, max_capacity=10)
vehicle1 = Vehicle(id="f", w=3, l=2, orientation="horizontal", shipping_fee=20, weight=10, eta=10)
vehicle2 = Vehicle(id="c", w=3, l=2, orientation="vertical", shipping_fee=20, weight=10, eta=10)
vehicle3 = Vehicle(id="d", w=3, l=2, orientation="horizontal", shipping_fee=20, weight=10, eta=10)




print(ship1.inputing_ship(vehicle1, 1, 18))
print(ship1.inputing_ship(vehicle2, 4, 1))
print(ship1.calculate_shipping_fee())

ship1.display()
print(vehicle1.coor)

# matriks mash bisa overlapp kalo lebih harusnya gagal input
# coordinat sistemnya masih array meaning x = vertikal y = horizontal
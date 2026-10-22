from starter import Vehicle, Ship, Armada
import math
import random
import copy
import time

class simulated_annealing:
    all_duration = []
    all_stuck_local_frequency = []
    all_shipping_fee_gain = []

  
    def __init__(self, armada: Armada, T: float, cooling_rate: float):
        self.armada = copy.deepcopy(armada)
        self.T = T  
        self.cooling_rate = cooling_rate

        self.duration = []
        self.stuck_local_frequency = 0
        self.shipping_fee_iteration = []
        self.history_acceptance_rate = []

    def move_success(self, neighbor: Armada) -> bool:
        if neighbor is None:  
            return False

        delta = neighbor.calculate_armada_shipping_fee() - self.armada.calculate_armada_shipping_fee()
        if delta >= 0:
            self.armada = neighbor
            self.T = self.T * self.cooling_rate 
            return True
        else:
            prob = math.exp(delta / self.T)
            self.history_acceptance_rate.append(prob)
            if random.random() < prob:
                self.armada = neighbor
                self.T = self.T * self.cooling_rate  
                return True
            else:
                self.stuck_local_frequency += 1
                self.T = self.T * self.cooling_rate
                return False
    
    def find_random_neighbour(self) -> Armada:
        move_found = False
        neighbour = copy.deepcopy(self.armada)  
        max_iteration = 500
        iteration = 0
        while iteration <= max_iteration:
            iteration += 1
            random_num = random.randint(1, 3)
            match random_num:

                case 1:
                    if (neighbour.switch_vehicle_success()):
                        move_found = True

                case 2:
                    chosen_ship = random.choice(list(neighbour.ship_list))
                    if len(chosen_ship.list_vehicles_in_ship) > 0:
                        chosen_vehicle = random.choice(list(chosen_ship.list_vehicles_in_ship))
                        if (chosen_ship.move_vehicle_success(chosen_vehicle)):
                            move_found = True

                case 3:
                    chosen_ship = random.choice(list(neighbour.ship_list))
                    if len(chosen_ship.list_vehicles_in_ship) > 0:
                        chosen_vehicle = random.choice(list(chosen_ship.list_vehicles_in_ship))
                        if (chosen_ship.change_orientation_success(chosen_vehicle)):
                            move_found = True

            if move_found: return neighbour
        return None

    def execute(self):
        start_time = time.time()
        iteration = 0
        max_iteration = 100
        initial_shipping_fee = self.armada.calculate_armada_shipping_fee()

        for ship in self.armada.ship_list:
            ship.display()
        print(f"shipping fee of the armada: {self.armada.calculate_armada_shipping_fee()}")
        
       
        while iteration <= max_iteration and self.T > 0.1:
            iteration += 1
            neighbour = self.find_random_neighbour()
            if self.move_success(neighbour):
                iteration = 0
                for ship in self.armada.ship_list:
                    ship.display()
                    print(ship.calculate_shipping_fee())
                self.shipping_fee_iteration.append(self.armada.calculate_armada_shipping_fee())
        
  
        gain = self.armada.calculate_armada_shipping_fee() - initial_shipping_fee
        simulated_annealing.all_shipping_fee_gain.append(gain)
        simulated_annealing.all_stuck_local_frequency.append(self.stuck_local_frequency)
        
        stop_time = time.time()
        duration = stop_time - start_time
        simulated_annealing.all_duration.append(duration)
        self.duration = duration

        for ship in self.armada.ship_list:
            ship.display()
        print(f"shipping fee of the armada: {self.armada.calculate_armada_shipping_fee()}")

if __name__ == "__main__":
    from starter import armada1
    
    # Menjalankan eksperimen 3 kali sesuai spesifikasi
    runs = []
    for i in range(5):
        print(f"\n==================== RUN {i+1} ====================")
        sa = simulated_annealing(armada=armada1, T=1000.0, cooling_rate=0.95)
        sa.execute()
        runs.append(sa)

    print("\n" + "="*50)
    print("         DETAIL HASIL TIAP RUN SIMULATED ANNEALING")
    print("="*50)
    
    for idx, sa_run in enumerate(runs, start=1):
        print(f"\n--- DETAIL RUN {idx} ---")
        print(f"Durasi Pencarian          : {sa_run.duration:.4f} detik")
        print(f"Stuck Local Frequency     : {sa_run.stuck_local_frequency} kali")
        print(f"Final Armada Shipping Fee : {sa_run.armada.calculate_armada_shipping_fee()}")
        print(f"Gain Shipping Fee         : {simulated_annealing.all_shipping_fee_gain[idx-1]}")
        print(f"Banyak Pencatatan Iterasi : {len(sa_run.shipping_fee_iteration)}")
        print(f"Shipping Fee Tiap Iterasi : {sa_run.shipping_fee_iteration}")
        print(f"History Acceptance Rate   : {[round(p, 4) for p in sa_run.history_acceptance_rate]}")
        
        # Menampilkan state akhir geladak kapal dan kendaraan di dalamnya
        placed_ids = set()
        print("\nState Akhir Geladak Kapal:")
        for ship in sa_run.armada.ship_list:
            print(f"  > Kapal '{ship.id}' (Fee: {ship.calculate_shipping_fee()}, Weight: {ship.calculate_ship_weight()}/{ship.max_capacity}):")
            ship.display()
            for v in ship.list_vehicles_in_ship:
                placed_ids.add(v.id)
                
        # Menampilkan kendaraan yang berada di luar kapal (unplaced)
        unplaced_vehicles = [v.id for v in sa_run.armada.list_all_vehicles if v.id not in placed_ids]
        print(f"Kendaraan di Luar Kapal   : {unplaced_vehicles}")

    print("\n=== REKAP KESELURUHAN 3 RUN ===")
    print("Durasi tiap run (detik)      :", [round(d, 4) for d in simulated_annealing.all_duration])
    print("Stuck frequency tiap run     :", simulated_annealing.all_stuck_local_frequency)
    print("Gain shipping fee tiap run   :", simulated_annealing.all_shipping_fee_gain)
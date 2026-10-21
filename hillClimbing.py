from starter import *
import random as rd
import copy
# hillclimb, armada dilakukan inisialisasi awal ->  switching, move vehicle -> hitung neighbor, 
# -> steepest pindah ke neighbor kalo ada yang lebih baik
# -> sideways pindah ke neighbor kalo sama atau lebih baik
# -> random restart -> bisa di restart


# randomize ukuran vehicle dengan ukuran yang sudah ada(misal 2x2, 3x4, 4x2, 5x2, dll) atau bisa di assign sendiri
# ukuran ship juga akan di randomize dengan ukuran yang sudah ada (50x50, 50x25, dll) atau bisa di assign sendiri
def get_neighbor(armada:Armada):
    neighbor = copy.deepcopy(armada)
    gerakan = rd.choice(["switch", "move", "rotate"])
    if gerakan == "switch":
        neighbor.switch_vehicle_success()
    else:
        ship = rd.choice(list(neighbor.ship_list))
        if ship.list_vehicles_in_ship:
            vehicle = rd.choice(list(ship.list_vehicles_in_ship))
            if gerakan == "move": 
                ship.move_vehicle_success(vehicle)
            else:
                ship.change_orientation_success(vehicle)
    return neighbor
    
def hill_climbing(armada, max_sideways=0, n_neighbors=50):
    fee_sekarang = armada.calculate_armada_shipping_fee()
    sideways = 0

    while True:
        fee_terbaik = -1
        kandidat = []

        for _ in range(n_neighbors):
            tetangga = get_neighbor(armada)
            f = tetangga.calculate_armada_shipping_fee()
            if f > fee_terbaik:
                fee_terbaik = f
                kandidat = [tetangga]
            elif f == fee_terbaik:
                kandidat.append(tetangga)

        if fee_terbaik > fee_sekarang:
            armada = rd.choice(kandidat)
            fee_sekarang = fee_terbaik
            sideways = 0
        elif fee_terbaik == fee_sekarang and sideways <  max_sideways:
            armada = rd.choice(kandidat)
            sideways += 1
        else:
            break
    return armada, fee_sekarang


def new_random_armada(armada):
    ships = set()
    for i in armada.ship_list:
        ships.add(Ship(i.w,i.l,i.max_capacity, i.id))
    vehicles = copy.deepcopy(armada.list_all_vehicles)
    for i in vehicles:
        i.coor = [-1,-1]
    fresh = Armada(ships,vehicles)
    fresh.random_state_armada(vehicles)
    return fresh

def random_restart(armada, max_sideways = 0, n_neighbor = 50, max_restart=100):
    best,best_fee = hill_climbing(armada, max_sideways, n_neighbor)
    for percobaan in range(1, max_restart + 1):
        hasil, fee = hill_climbing(best, max_sideways, n_neighbor)
        if fee > best_fee:
            best_fee = fee
            best = hasil
    return best, best_fee, percobaan

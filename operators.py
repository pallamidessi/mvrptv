# -*- coding:utf-8 -*-
import random
import model
import genome
import copy
import itertools

def init(ind_class, size, nb_vehicle, data):
    """
    Initialisation operator. Fill the inidividual's first part with a random permutation of
    appointement and compute the second part with a valid vehicle count.
    """
    remaining_size = size 
    second_part = []
    first_part = []

    # Create the second part of the individual
    # Choose random value while checking the upper bound
    for i in range(0, nb_vehicle):
        vehicle_capacity = random.randrange(1, 5)
        vehicle_capacity %= remaining_size
        remaining_size -= vehicle_capacity
        second_part.append(vehicle_capacity)

    # If there is still unassignated vehicles at the end
    # Assigned them to the last vehicle
    if remaining_size > 0:
        second_part[-1] += remaining_size

    # Create the first part of the chromosome 
    # Just a random permutation of indexes
    first_part = range(0, size)
    random.shuffle(first_part)
    
    mroute = []

    for appointement_idx in first_part:
        route = []
        for vehicle_size in second_part:
            for i in range(0, vehicle_size):
                insert_appointment(route, appointement_idx, data)
        mroute.append(route)
    
    first_part = list(itertools.chain(*mroute))

    # Create the individual and return it
    ind = ind_class((first_part, second_part))
    return ind

def insert_appointment(route, appointement_idx, list_appointment):
    appointement_to_insert = list_appointment[appointement_idx]
    it = 0 
    if len(route) == 0:
        route.append(appointement_idx)
    elif len(route) > 1:
        for idx in route:
            if list_appointment[idx].starting_time > appointement_to_insert.starting_time:
                route.insert(it, appointement_idx)
                return
            if it == len(route) and list_appointment[idx].starting_time < appointement_to_insert.starting_time:
                route.append(appointement_idx)
                return
        it +=1


def evaluate(individual, data, depot):
    """
    Evaluate the genome.
    """
    splitted_route = []
    idx = 0
    capacity_per_vehicle = 5
    distance = 0
    load = 0

    # Split the first part of the individual as a list of route using the second part
    for vehicle_size in individual.vehicles:
        splitted_route.append(individual.routes[idx:vehicle_size])
        idx += vehicle_size

    # For each vehicle (route)
    # Compute the distance travelled and the load 
    for route in splitted_route:
        if len(route) > 0:
            distance += model.euclidian_distance(depot, data[route[0]])
            for gene1, gene2 in zip(route[0:-1], route[1:]):
                distance += model.euclidian_distance(data[gene1], data[gene2])

            for gene1, gene2 in zip(route[0:-1], route[1:]):
                load += 1

            load -= capacity_per_vehicle

    # Return a tuple of fitness: the cost and the load 
    return distance, load


def insertAppointment(app, appList, data):
    """
    Appointment inserting function. Insert an appointment in a 2D
    appointment list.
    """
    tmp = len(appList)
    # Vehicle number
    numV = random.randrange(0, tmp)
    for idx in range(0, len(appList[numV])):
        if (data[appList[numV][idx]].starting_time > data[app].starting_time):
            appList[numV].insert(idx, app)
            return appList

    appList[numV].append(app)
    return appList



def cxRC(parent1, parent2, data):
    """
    Custom RC (or BCRC) crossover as describe in the article[1]

    [1]:
    """    
    
    child1 = copy.deepcopy(parent1)
    child2 = copy.deepcopy(parent2)

    child1.routes = []
    child1.vehicles = []

    # Can't compute offspring in this case
    if (len(parent1.routes) != len(parent2.routes)):
        return copy.deepcopy(parent1)

    appointmentsByVehicle1 = []
    appointmentsByVehicle2 = []

    tmpLen = len(parent1.vehicles)

    offset1 = 0
    offset2 = 0

    # Getting lists of lists containing all the appointments sorted by vehicle
    for i in range(0, tmpLen):

        newOffset1 = offset1 + parent1.vehicles[i]
        newOffset2 = offset2 + parent2.vehicles[i]

        appointmentsByVehicle1.append(
                parent1.routes[offset1:newOffset1]
                )

        appointmentsByVehicle2.append(
                parent2.routes[offset2:newOffset2]
                )

        offset1 = newOffset1
        offset2 = newOffset2

    # print("Before: ")
    # print(appointmentsByVehicle1)
    # print(appointmentsByVehicle2)

    # Picking and removing appointments associated to a vehicle in the second
    # parent from the first parent.
    tmpSelect = random.randrange(0, tmpLen)

    for element in appointmentsByVehicle2[tmpSelect]:
        for index in range(0, tmpLen):
            appointmentsByVehicle1[index] = \
                    [item for item in appointmentsByVehicle1[index] \
                    if item != element]

                    # Inserting back those elements in the list corresponding to the first
    # parent.
    for element in appointmentsByVehicle2[tmpSelect]:
        appointmentsByVehicle1 = insertAppointment(
                element,
                appointmentsByVehicle1,
                data
                )

    # print("After: ")
    # print(appointmentsByVehicle1)
    
    # Making new vehicles containing the right number of appointments for the
    # offspring.
    vehicleList = []

    for index in range(0, tmpLen):
        vehicleList.append(len(appointmentsByVehicle1[index]))

    # Flattening the 2D list to create the offspring.
    appointments = [i for subList in appointmentsByVehicle1 for i in subList]
    
    child1.routes = appointments
    child1.vehicles = vehicleList

    # Yay! Offspring!
    return child1

def crossover(parent1, parent2, data):
    child1 = cxRC(parent1, parent2, data)
    child2 = cxRC(parent2, parent1, data)
    
    return child1, child2

def constrainedSwap(ind, data):
    """
    A random swap following constraints.
    Need pretty heavy refactoring 
    """
    list_appointment = data
    splitted_route = []
    idx = 0 

    # Split the first part of the individual as a list route using the second part
    for vehicle_size in ind.vehicles:
        splitted_route.append(ind.routes[idx:vehicle_size])
        idx += vehicle_size

    # Randomly choose a non-empty route
    while True:
        rand_route = random.randrange(0, len(splitted_route))
        if len(splitted_route[rand_route]) > 0:
            break

    # Choose a random appointement in the selected route
    rand_appointement = random.randrange(0, len(splitted_route[rand_route]))

    # Now we insert this appointement into a ramdomly selected route if we can find
    # a place where it respect constraints. If not, we do nothing
    shuffled_route = range(0, len(splitted_route))
    random.shuffle(shuffled_route)

    for i in shuffled_route:
        if i != rand_route:
            ii = 0
            for appointement_idx in splitted_route[i]:

                # If the next element in the list start after the one we want to
                # insert, we emplace it here, and delete it from where we took it 
                if list_appointment[appointement_idx].starting_time > list_appointment[rand_appointement]:
                    splitted_route[i].insert(ii, rand_appointement)
                    del splitted_route[rand_route][rand_appointement]
                    return ind,

                # If the last appointement is starting before the one we want to insert,
                # We insert it at the end of of the route, and delete it from where we took it   
                elif ii == len(splitted_route[i]) - 1:
                    if list_appointment[appointement_idx].starting_time < list_appointment[rand_appointement]:
                        list_appointment.append(rand_appointement)
                        del splitted_route[rand_route][rand_appointement]
                        return ind,

    return ind,


# -*- coding:utf-8 -*-

"""
This file contains the description of the class individual.
"""
import itertools
from operators import window_bounds_checking
import model
import copy


class MvrpIndividual(object):
    """
    Genome definition. The genome is implemented a two-part chromosome
    described in the [insert link here] article[1].

    routes : A list of integer, referencing appointment by their indexes

    vehicles : A list of integer, where each values represent a vehicle and how
    many appointments it contained starting from the head of the list.

    Example:

    |1|2|3|4|5|6| || |2|2|2|

    Vehicle_1 contains |1|2|
    Vehicle_2 contains |3|4|
    Vehicle_3 contains |5|6|

    [1]:
    """
    def __init__(self, attributes):
        self.routes = attributes[0]
        self.vehicles = attributes[1]

    def __repr__(self):
        return ("<Individual routes %s vehicle %s> \n" %
                (self.routes, self.vehicles))

    def split(self):
        """
        Split the first part of the individual as a list of route using the
        second part
        """
        splitted_route = []
        idx = 0

        for vehicle in self.vehicles:
            splitted_route.append(self.routes[idx:vehicle.count() + idx])
            idx += vehicle.count()

        return splitted_route

    def is_time_constraint_respected(self, data):
        """
        Checks how many time constraints are violated by the individual.
        """
        tmp = self.decode(data)
        result = 0
        for sublist in tmp:
            if len(sublist) != 0:
                current = sublist[0]
                test = current.duration() > \
                    (current.window_end() - current.window_start())
                for i in range(1, len(sublist)):
                    if not window_bounds_checking(current, sublist[i]) or test:
                        result += 1
                    current = sublist[i]
        return result

    def is_load_respected(self):
        """
        Simple operation to check whether the individual respects the load
        constraint.
        """
        for vehicle in self.vehicles:
            if vehicle.count() > vehicle.capacity():
                return False
        return True

    #def is_load_always_respected(self, data):
    #    """
    #    Simple operation to check whether the individual respects the load
    #    constrait at each moment.
    #    """
    #    splitted_routes = self.split()
    #    idx = 0
    #    for vehicle in self.vehicles:
    #        current_count = 0
    #        for appointment in splitted_routes[idx]:
    #            # Departure
    #            if appointment._type == 0:

    def decode(self, data):
        """
        Decodes the individual using a dictionary of data.
        """
        list_appointment = data["appointment"]
        tmp = self.split()
        to_return = []
        index = 0
        for sublist in tmp:
            to_return.append([])
            for element in sublist:
                to_return[index].append(list_appointment[element])
            index += 1
        return to_return

    def encode(self, list_appointment, parent):
        """
        Encodes the individual using a list of appointments
        """
        self.vehicles = []
        index = 0
        for sublist in list_appointment:
            self.vehicles.append(copy.deepcopy(parent.vehicles[index]))
            self.vehicles[index].set_count(len(sublist))
            index += 1

        self.routes = list(itertools.chain.from_iterable(list_appointment))

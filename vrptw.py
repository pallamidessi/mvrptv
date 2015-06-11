# -*- coding:utf-8 -*-

import random
import numpy
import visualisation
import model
import genome
import operators
import copy

from deap import base
from deap import creator
from deap import tools
from deap import algorithms


def main():
    random.seed(666)

    # Problem's definition  
    depot = model.Point(500, 500)
    w = 1000
    h = 1000
    num_route = 2
    num_node_per_route = 5
    IND_SIZE = num_route * num_node_per_route

    # Genetic parameter
    pop_size = 3000
    elite_size = 1
    crossover_probability = 0.7
    mutation_probability = 0.1
    ngen = 50
    mu = pop_size
    _lambda = pop_size
    
    # Generate a the problem's data set
    # i.e: Generate N "route" of appointement 
    list_appointment = model.generate_route(num_route, 
                                             num_node_per_route,
                                             w,
                                             h,
                                             depot)
    # Set the routes color  
    color = visualisation.color_group(num_route)

    # Assign the custom individual class to the toolbox
    # And set the number of wanted fitnesses 
    toolbox = base.Toolbox()
    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0))
    creator.create("Individual", genome.MvrpIndividual, fitness=creator.FitnessMulti)

    # Assign the initialisation operator to the toolbox's individual
    # And describe the population initialisation  
    toolbox.register("individual", operators.init, creator.Individual,
                     size = IND_SIZE, nb_vehicle = num_route, data = list_appointment)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Set the different genetic oprator inside the toolbox
    toolbox.register("clone", copy.deepcopy)
    toolbox.register("mate", operators.cxRC, data=list_appointment)
    toolbox.register("mutate", operators.constrainedSwap, data=list_appointment)
    toolbox.register("select", tools.selNSGA2)
    toolbox.register("evaluate", operators.evaluate, data=list_appointment, depot=depot)

    # Create the global population
    # And an elite one  

    pop = toolbox.population(n=pop_size)
    hof = tools.HallOfFame(elite_size)

    # Create a statistic module to display stats at each generation 
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean, axis=0)
    stats.register("std", numpy.std, axis=0)
    stats.register("min", numpy.min, axis=0)
    stats.register("max", numpy.max, axis=0)


    # The genetic alogorithm in itself 
    algorithms.eaMuPlusLambda(pop, 
            toolbox,
            mu,
            _lambda,
            crossover_probability,
            mutation_probability,
            ngen,
            stats=stats, 
            halloffame=hof)

    # Create display of the problem and of the best solution  
    root = visualisation.Tk()
    root.geometry("" + str(w) + "x" + str(h))
    app = visualisation.Example(root, 
            list_appointment,
            color, 
            depot,
            visualisation.individual_as_appointment(hof[0], list_appointment))

    # Start the GUI main loop
    root.mainloop()  

if __name__ == '__main__':
    main()  

# -*- coding: utf-8 -*-
"""

This work was developed based on the following reference:

Prina, M.G. et al., 2018. Multi-objective optimization algorithm coupled to EnergyPLAN software: The EPLANopt model. Energy, 149: 213-221.
"""

from __future__ import print_function
import os
import shutil
import time
import numpy as np  
# 1.1 Types
from deap import base, creator
# 1.2 Initialization
import random
from deap import tools
from deap import algorithms
from libeplan_Yulin import Node
import multiprocessing
import libfun_Yulin as lf
from operator import mul, add
import json
import glob
import argparse
import functools

global VARIABLES, START, X, MOLT_FACTORS, INPUTFILE
global DNDC, OUT_FOLDER, FUNCTION_2_EVAL
global CONSTRAIN


#args='-i test/configurations_Yulin.json -o test.json'
# set up the optimazation algorithms, constrains, objectives, input, and output 
parser = argparse.ArgumentParser(description='DNDCopt')
parser.add_argument('-i', '--input', help='Input file name',
                    required=True)
parser.add_argument('-o', '--output', help='Output file name',
                    required=True)

args = parser.parse_args()

data = lf.load_json(args.input)


VARIABLES = tuple([dic['DNDC Name'] for dic in data["Variables"]])
X = [tuple(dic['Range']) for dic in data["Variables"]] # X is the model constrains
MOLT_FACTORS = [dic['Moltiplication factor'] for dic in data["Variables"]]
val = data["Genetic algorithm"][0]
FUNCTION_2_EVAL = [i['Value'] for i in val["Function to evaluate with DNDC"]]
INPUTFILE = data["Input file"]
DNDC = data["DNDC folder"]
OUT_FOLDER = data["Output folder"]

if "Constrains" in data.keys():
    CONSTRAIN = data["Constrains"]

if not(os.path.isfile(INPUTFILE)):
    try:
        directory = os.path.dirname(__file__)
        INPUTFILE = os.path.join(directory.replace("/", "\\"),
                                 data["Input file"])
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))


if not(os.path.isdir(OUT_FOLDER)):
    try:
        directory = os.path.dirname(__file__)
        OUT_FOLDER = os.path.join(directory.replace("/", "\\"),
                                  data["Output folder"])
    except IOError as e:
        print("I/O error({0}): {1}".format(e.errno, e.strerror))

START = Node(INPUTFILE, DNDC, OUT_FOLDER)
objs = tuple([i['Weight: negative minimization, positive maximization']
             for i in
             val["Function to evaluate with DNDC"]])



min_b = list(zip(*X))[0]
max_b = list(zip(*X))[1]
creator.create("FitnessMin", base.Fitness, weights=objs)
creator.create("Individual", list, fitness=creator.FitnessMin)

list_attr = []
toolbox = base.Toolbox()

for i, bnd in enumerate(X):
    attr = 'attr_l%i' % i
    toolbox.register(attr, random.randint, bnd[0], bnd[1])
    list_attr.append(toolbox.__getattribute__(attr))

toolbox.__dict__.keys()

# plz check the explanation here https://deap.readthedocs.io/en/master/api/tools.html
toolbox.register("individual", tools.initCycle, creator.Individual,list_attr, n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxUniform,indpb=0.5)
toolbox.register("mutate", tools.mutUniformInt,low=min_b, up=max_b, indpb=1.0/100)

# select NSGA-III
#The reference point set serves to guide the evolution into creating a uniform Pareto front in the objective space
ref_points = tools.uniform_reference_points(4, 12)
toolbox.register("select", tools.selNSGA3, ref_points=ref_points)


def excute_DNDC(individual):
    # Excute DNDC if output not already excuted else it returns the node to read it
    new_data = START.data   
    var_ep = [i*j for i, j in zip(MOLT_FACTORS, individual)]
    for i, key in enumerate(VARIABLES):
        new_data[key] = var_ep[i]

    resultsfile = r'%s\AnnualReport_CroppingSystem_yr1.txt' % OUT_FOLDER
                                   
    inputfile = INPUTFILE.replace('.dnd',
                                  '_'.join(map(str, individual)) +
                                  '_tmp.dnd')

    new_node = Node(inputfile, DNDC,
                    resultsfile, new_data)

    
    if os.path.exists(inputfile):
        while not os.path.exists(resultsfile):
            time.sleep(0.1)
        return new_node
    else:
        new_node.write_input()
        new_node.excute()
        os.remove(inputfile)
        return new_node
       
class feasible(object):
    #Decorator to the function f to add the penalty to f in case of constrains
    
    def __init__(self, target):
        self.target = target
        functools.update_wrapper(self, target)

    def __call__(self, individual):
        node = excute_DNDC(individual)
        annual_indicator = node.read_annual_indicator()
        c = []
        for constr in CONSTRAIN['Constr']:
            c.append(eval(constr))
        # the execution of constr return c
        if reduce(mul, c):   # reduce built-in funtion
            return tuple(map(add, self.target(individual),
                             tuple(CONSTRAIN['Penalty'])))
        return self.target(individual)


def f(individual):
    #Function to evaluate. It runs the DNDC.exe to compute the values to maximize or minimize 
    #:individual: indipendent variables for the function
    
    new_node = excute_DNDC(individual)
    dic = new_node.read_annual_indicator()
    path = lf.find_path_dictionary(FUNCTION_2_EVAL, dic)
    values = lf.find_value_from_path(FUNCTION_2_EVAL, path, dic)
    return lf.unpack(values, len(values)-1)


def ga(toolbox,
    evaluate, n_pop, n_gen, feasible=None, penalty=None):
    # Excute the GA algorithms.


    toolbox.register("evaluate", evaluate)
    print('register successful')

    pop = toolbox.population(n=n_pop)
    pop0 = pop
    print('POP successful ' + str(n_pop))
 
    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, pop)
    print(fitnesses)
    
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
    print('values done')
    
    ff0 = [ind.fitness.values for ind in pop]
    hist = {'population': {}, 'fitness': {}}
    hist['population'][0] = list(zip(*pop0))
    hist['fitness'][0] = list(zip(*ff0))

    pop = toolbox.select(pop, len(pop))
    for gen in range(1, n_gen):
        print("step: %s" % gen)  # to count the generation
        
        offspring = algorithms.varAnd(pop, toolbox, 1.0, 1.0)


        for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
            if random.random() <= 0.9:
                toolbox.mate(ind1, ind2)

            toolbox.mutate(ind1)
            toolbox.mutate(ind2)
            del ind1.fitness.values, ind2.fitness.values

        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        pop = toolbox.select(pop + offspring, n_pop)

        hist['population'][gen] = list(zip(*pop))
        fitnesses = [ind.fitness.values for ind in pop]
        hist['fitness'][gen] = list(zip(*fitnesses))

    ff = fitnesses

    return pop, ff, hist

def save_pareto(OUT_FOLDER, dic):
    # dominated 
    np.savetxt(os.path.join(OUT_FOLDER,'fitness_dominated.txt'), dic['fitness'][0][:],fmt='%1.3f')
    np.savetxt(os.path.join(OUT_FOLDER,'Population_dominated.txt'), dic['population'][0][:],fmt='%1.3f')

    #non-dominated
    np.savetxt(os.path.join(OUT_FOLDER,'fitness_non_dominated.txt'), dic['fitness'][len(dic['fitness'])-1][:],fmt='%1.3f') 
    np.savetxt(os.path.join(OUT_FOLDER,'Population_non_dominated.txt'), dic['population'][len(dic['population'])-1][:],fmt='%1.3f')

    
    print ('saving pareto results')
    
if __name__ == "__main__":
    if "Constrains" in data.keys():
        fun = feasible(f)
    else:
        fun = f

    pool = multiprocessing.Pool(processes=data["Number of process"])
    toolbox.register("map", pool.map)
    val = data["Genetic algorithm"][0]
    pop = toolbox.population(n=val['Size of population'])
    
    pop, ff, hist = ga(toolbox, fun,
                       val['Size of population'],
                       val['Number of generations'])

    pool.close()
    with open(r'%s\%s' % (OUT_FOLDER, args.output), 'w') as outfile:
        json.dump(hist, outfile)
    lf.plot_pareto(OUT_FOLDER, hist)
    save_pareto(OUT_FOLDER, hist)
    
    if "Debug" in data.keys():
        if data["Debug"] is False:
            for name in glob.glob(os.path.join(OUT_FOLDER, r'*_tmp.txt')):
                os.remove(name)
            for name in glob.glob(INPUTFILE.replace('.txt', '*tmp.txt')):
                os.remove(name)


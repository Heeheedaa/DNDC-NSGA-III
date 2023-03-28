# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 12:20:33 2021

@author: Environment Ecology

This work was developed based on the following reference:

Prina, M.G. et al., 2018. Multi-objective optimization algorithm coupled to EnergyPLAN software: The EPLANopt model. Energy, 149: 213-221.
"""

import json
from matplotlib import pyplot as plt
import os
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def find_path_dictionary(fun_2_eval, dic):
    """find the path in the dictionary for each key of the input list
    :fun_2_eval: list of string with the variables to evaluate
    :fun_2_eval:  ListType
    :dic: dictionary
    :type dic:  DictType
    :returns: for each variables the path in the dictionary
    >>> dic = {'a1': {'b1': 1, 'b2': 2, 'b3': 3}, 'a2': {'b4': {'c4': 4, 'c5': 5}}}
    >>> find_path_dictionary(['c4', 'b2'], dic)
    {'b2': ['a1', 'b2'], 'c4': ['a2', 'b4', 'c4']}
    """

    # TODO: error if fun is not in the dictionary
    
    path = {}
    for fun in fun_2_eval:
        for k in dic.keys():
            for i in dic[k].keys():
                if isinstance(dic[k][i], dict):
                    for j in dic[k][i].keys():
                        if fun in j:
                            path[fun] = [k, i, j]
                elif fun in i:
                    path[fun] = [k, i]
                    
                    print (path)
    return path

def find_value_from_path(fun_2_eval, path, dic):
    """find the value in a dictionary given the path
    :fun_2_eval: an orderd list with the function to evaluate
    :path: list with the keys of the dictionary
    :dic: dictionary
    :returns: an ordered list with float values
    >>> dic = {'a1': {'b1': 1, 'b2': 2, 'b3': 3}, 'a2': {'b4': {'c4': 4, 'c5': 5}}}
    >>> path = find_path_dictionary(['c4', 'b2'], dic)
    >>> find_value_from_path(['c4', 'b2'], path, dic)
    [4.0, 2.0]
    """
    l_value = []
    for f in fun_2_eval:
        inner_val = dic
        for k in path[f]:
            inner_val = inner_val[k]
        l_value.append(float(inner_val))
    return l_value


def load_json(filein):
    """load the data from the configurations.json file"""
    with open(filein) as data_file:
        data = json.load(data_file)
        return data


def unpack(seq, count):
    """unpack values from a list"""
    return seq[:count] + [seq[count:]][0]


def plot_pareto(OUT_FOLDER, dic):
    #fig,(ax1, ax2, ax3, ax4) = plt.subplots(4, nrows=2, ncols=2)
    fig, [[ax1, ax2], [ax3, ax4]] = plt.subplots(nrows=2, ncols=2,figsize=(15,15),dpi=500)
    """ 
    ax0.scatter(dic['population'][0][0], dic['population'][0][1], c='b')
    ax0.scatter(dic['population'][len(dic['population'])-1][0],
                dic['population'][len(dic['population'])-1][1], c='r')
    """
    ax1.scatter(dic['fitness'][0][0], dic['fitness'][0][1], c='b')
    ax1.scatter(dic['fitness'][len(dic['fitness'])-1][0],
                dic['fitness'][len(dic['fitness'])-1][1], c='r')
    
    ax2.scatter(dic['fitness'][0][0], dic['fitness'][0][2], c='b')
    ax2.scatter(dic['fitness'][len(dic['fitness'])-1][0],
                dic['fitness'][len(dic['fitness'])-1][2], c='r')
    
    ax3.scatter(dic['fitness'][0][1], dic['fitness'][0][2], c='b')
    ax3.scatter(dic['fitness'][len(dic['fitness'])-1][1],
                dic['fitness'][len(dic['fitness'])-1][2], c='r')
    
    ax4.scatter(dic['fitness'][0][1], dic['fitness'][0][3], c='b')
    ax4.scatter(dic['fitness'][len(dic['fitness'])-1][1],
                dic['fitness'][len(dic['fitness'])-1][3], c='r')
    
    fig.savefig(os.path.join(OUT_FOLDER, 'pareto.png'))



    fig = plt.figure(figsize=(15,15),dpi=500)
    ax = fig.add_subplot(2, 2, 1, projection='3d')
    ax.scatter(dic['fitness'][0][0], dic['fitness'][0][2], dic['fitness'][0][1], c='b',marker="o",alpha=0.5,  s=2)
    
    ax.scatter(dic['fitness'][len(dic['fitness'])-1][0],
               dic['fitness'][len(dic['fitness'])-1][2],
                dic['fitness'][len(dic['fitness'])-1][1], c='r',marker="o", alpha=0.6, s=6)
    ax.view_init(45, 0)
    
    
    ax = fig.add_subplot(2, 2, 2, projection='3d')
    ax.scatter(dic['fitness'][0][3], dic['fitness'][0][2], dic['fitness'][0][1], c='b',marker="o",alpha=0.5,  s=2)
    
    ax.scatter(dic['fitness'][len(dic['fitness'])-1][3],
               dic['fitness'][len(dic['fitness'])-1][2],
                dic['fitness'][len(dic['fitness'])-1][1], c='r',marker="o",  alpha=0.6,s=6)
    ax.view_init(45, 0)
    
    
    ax = fig.add_subplot(2, 2, 3, projection='3d')
    ax.scatter(dic['fitness'][0][0], dic['fitness'][0][3], dic['fitness'][0][1], c='b',marker="o",alpha=0.5,  s=2)
    
    ax.scatter(dic['fitness'][len(dic['fitness'])-1][0],
               dic['fitness'][len(dic['fitness'])-1][3],
                dic['fitness'][len(dic['fitness'])-1][1], c='r',marker="o", alpha=0.6, s=6)   
    ax.view_init(45, 0)
    
    
    ax = fig.add_subplot(2, 2, 4, projection='3d')
    ax.scatter(dic['fitness'][0][0], dic['fitness'][0][2], dic['fitness'][0][3], c='b',marker="o",alpha=0.5,  s=2)
    
    ax.scatter(dic['fitness'][len(dic['fitness'])-1][0],
               dic['fitness'][len(dic['fitness'])-1][2],
                dic['fitness'][len(dic['fitness'])-1][3], c='r',marker="o", alpha=0.6, s=6)    
    ax.view_init(45, 0)
    
    fig.savefig(os.path.join(OUT_FOLDER, '3D-Pareto.png'))

    
if __name__ == "__main__":

    import doctest
    doctest.testmod()

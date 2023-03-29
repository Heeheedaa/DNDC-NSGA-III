# -*- coding: utf-8 -*-
"""
Created on Wed Mar  3 12:20:33 2021

@author: Environment Ecology

This work was developed based on the following reference:
Prina, M.G. et al., 2018. Multi-objective optimization algorithm coupled to EnergyPLAN software: The EPLANopt model. Energy, 149: 213-221.
"""

import os
from os import listdir
from os.path import isfile, join
import numpy as np
from collections import OrderedDict
import os.path
import time
import subprocess
from libfun_Yulin import load_json
import pyautogui 



class Node(object):
    # of each node I have input values and input ditribution
    def __init__(self, inputfile, DNDCfolder,
                 resultsfile=None, data=None, distributions=None,
                 ):

        # TODO: check that the distribution is an object Distribution

        self.inputfile = inputfile
        self.DNDCfolder = DNDCfolder
        self.resultsfile = resultsfile
        if data is None:
            self.data = self.get_data()
        else:
            self.data = data
        # TODO: data is an order dictionary, to check

        self.distributions = distributions

    def get_data(self):
        # FIXME: fix order dictionary for 3.3
        with open(self.inputfile, 'r') as f:
            data = f.readlines()
            data = [row[:-1] for row in data]
            od = OrderedDict()
            # print data
            od['Node name'] = self.inputfile  # first key is node name
            print(data[0])
            
        for k in np.arange(0, len(data)):  # even rows contain keys
            val = data[k]
            val = val.split()
            if len(val)>1:
                val = val[1].strip()
            
            # convert val into float/int
            try:
                val = float(val)
                if val.is_integer():
                    val = int(val)
            except:
                pass
            od[data[k].strip()] = val

        # remove 'xxx' key, if present
        if 'xxx' in od:
            del od['xxx']

        self.data = od
        return self.data


    def write_input(self):
        """lod --- list of ordered dictionaries with the inputs to write,
        one for each node"""

        odi = self.data
        to_write = odi.copy()
        
        with open("C:\\DNDC\\DNDC_Validation_cases\\Korea_Cheorwon_Rice\\input_file\\test.dnd", 'r') as f:
            to_write = f.readlines()
        with open(self.inputfile, 'w') as f:
            
            to_write[83] = '______Planting_month %s\n'% odi['______Planting_month']            
            to_write[84] = '______Planting_day %s\n'% odi['______Planting_day']
            to_write[123] = '______Till_method %s\n'% odi['______Till_method']      
            to_write[131] = '______Nitrate %s\n'% odi['______Nitrate'] 
            to_write[169] = '______Start_day1 %s\n'% odi['______Start_day1']
            to_write[181] = '______Start_day2 %s\n'% odi['______Start_day2']
            to_write[193] = '______Start_day3 %s\n'% odi['______Start_day3']
            to_write[205] = '______Start_day4 %s\n'% odi['______Start_day4']
            to_write[217] = '______Start_day5 %s\n'% odi['______Start_day5']
            to_write[229] = '______Start_day6 %s\n'% odi['______Start_day6']
            to_write[241] = '______Start_day7 %s\n'% odi['______Start_day7']
            to_write[253] = '______Start_day8 %s\n'% odi['______Start_day8']
            to_write[265] = '______Start_day9 %s\n'% odi['______Start_day9']
            to_write[277] = '______Start_day10 %s\n'% odi['______Start_day10']
            



            for j in range(len(to_write)): 
                f.write('%s' % to_write[j])

    def excute(self):
        """execute DNDC.exe"""

        #control the duration of the delay between actions
        
        
        #Adjust the postision parameters accordingly  
        #Input 
        pyautogui.click(108, 67, button='left')
        
        pyautogui.PAUSE = 0.3
        #Open an input data file
        pyautogui.click(676, 341, button='left')
        

        pyautogui.PAUSE = 0.3       
        #Select input data,
        #make sure input data grouped by date and in descending order
        pyautogui.click(389, 482, button='left')
        

        #Open
        pyautogui.click(657, 604, button='left')
        
        #OK
        pyautogui.click(611, 797, button='left')
        
        #Run
        pyautogui.click(179, 63, button='left')
        
        time.sleep(2.5)
        
        
        
    def read_annual_indicator(self):
        """read the output file of DNDC and return a dictionary
        with the main annual indicators"""
        
        while not os.path.exists(self.resultsfile):
            time.sleep(1.0)
        #print("result file is", self.resultsfile)
        if os.path.isfile(self.resultsfile):
                                               
            with open(self.resultsfile, "r+") as raw_file:
                complete = raw_file.readlines()
                
                annual_CH4 = complete[32].split()[2] #kg C/ha/yr
                        
                annual_N2O = complete[37].split()[1]  #kg N/ha/yr
                        
                annual_grain_yield =complete[71].split()[3] #kg C/ha
                
                # Irrigation = Transpiration + Soil evaporation + Run off + Leaching + soil profile water change -Precipitation
                annual_water =float(complete[95].split()[1]) +float(complete[96].split()[2])+float(complete[97].split()[2])+float(complete[98].split()[1])+float(complete[99].split()[4][:5])-float(complete[99].split()[6]) -float(complete[91].split()[1])
                
                        
                y_ind = load_json("out_dict_Yulin.json")

                
                y_ind['object1']['annual_CH4'] = annual_CH4       
                y_ind['object2']['annual_grain_yield'] = annual_grain_yield 
                y_ind['object3']['annual_N2O'] = annual_N2O
                y_ind['object4']['annual_water'] = annual_water
                
                return y_ind
                    
            
                                                  
def recode(infile, outfile):
    pass


if __name__ == "__main__":
    import doctest
    doctest.testmod()

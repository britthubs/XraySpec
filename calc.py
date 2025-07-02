import matplotlib # not explicitely used, but needed for figure
import numpy as np
import logging

logging.debug("calc.py is running before fisx import.")

import fisx
from fisx import DataDir
import os
import sys

logging.debug("Fisx imported without crashing.")  # very first thing to confirm the file runs
logging.debug(f"DataDir module contents: {dir(fisx.DataDir)}") # print contents for debugging

if getattr(sys, 'frozen', False):  # running in a bundle
    data_dir = os.path.join(sys._MEIPASS, 'fisx/fisx_data')
    logging.debug(f"Running frozen, setting fisx data dir to: {data_dir}")
    fisx.DataDir.FISX_DATA_DIR = data_dir
    
else:
    logging.debug("Running in normal Python mode, using default fisx data dir.")
logging.debug(f"fisx.DataDir.FISX_DATA_DIR is now: {fisx.DataDir.FISX_DATA_DIR}")

# print the data dir after setting it
try:
    logging.debug(f"fisx data dir after setting: {DataDir.getDataDir()}")
except AttributeError:
    logging.warning("No getDataDir() method found in DataDir module.")

from PyMca5.PyMcaIO.ConfigDict import ConfigDict
from PyMca5.PyMcaPhysics.xrf import Elements

class specPlot():
    def __init__(self, pathnameCFG):
        self.pathnameCFG = pathnameCFG
        self.zerogain, self.names = self.readcfg() # zerogain and names needed for annotations
    
    def readcfg(self):
        logging.debug("Calculating zero and gain, saving elements.")
        config = ConfigDict()
        config.read(self.pathnameCFG)
        zerogain = [config['detector']['zero'], config['detector']['gain']]  # zero, gain
        names = []
        for el in config['peaks']:
            if isinstance(config['peaks'][el], list):
                for line in config['peaks'][el]:
                    names.append(el + ' ' + line)
            else:
                names.append(el + ' ' + config['peaks'][el])
    
        return zerogain, names
    
    def annotation(self, ax):
        logging.debug("Configuring annotations.")
        handles = ax.get_lines()  # get plotted data handles
        used_positions = []  # store used y-positions to avoid overlap
        
        for n in self.names:
            if n in ['Rayl', 'Compt']:
                continue  # skip Rayleigh and Compton scattering peaks
            
            element, transition = n.split(" ")  # separate element & transition based on the space inbetween
            
            energy = None
            label = None

            # K-series transitions
            if transition == 'K':  
                energy = Elements.getxrayenergy(element, 'KL3')
                label = f"{element} Kα"
            elif transition == 'Ka':
                energy = Elements.getxrayenergy(element, 'KL3')
                label = f"{element} Kα"
            elif transition == 'Kb':
                energy = Elements.getxrayenergy(element, 'KM3')
                label = f"{element} Kβ"

            # L&M-series transitions
            elif transition == 'L':
                energy = Elements.getxrayenergy(element, 'L3M5')
                label = f"{element} Lα"
            elif transition == 'L1':
                energy = Elements.getxrayenergy(element, 'L3M5')
                label = f"{element} Lα"
            elif transition == 'L2':
                energy = Elements.getxrayenergy(element, 'L2M4')
                label = f"{element} Lβ"
            elif transition == 'L3':
                energy = Elements.getxrayenergy(element, 'L2N4')
                label = f"{element} Lγ"
            elif transition == 'M':
                energy = Elements.getxrayenergy(element, 'M5N7')
                label = f"{element} Mα"
            if energy is None:
                continue
            
            # find closest x_data point
            x_data = handles[0].get_xdata()
            valid_indices = np.where(x_data <= energy)[0]
            if valid_indices.size > 0:
                idx = max(valid_indices)
            else:
                continue  # skip if no valid data point

            # get y-value at closest energy
            y_values = [hand.get_ydata()[idx] for hand in handles if len(hand.get_ydata()) > idx]
            if not y_values:
                continue
            
            yval = max(y_values)
            
            # text positions & specifics
            base_offset = 3 # adjust text height relative to peak
            final_yval = (yval - 0.01*yval) * base_offset  
            min_spacing_factor = 1.15  
            while any(abs(np.log10(final_yval) - np.log10(used_y)) < 0.1 for used_y in used_positions):
                final_yval *= min_spacing_factor  # push up slightly
            used_positions.append(final_yval)  # store adjusted position
            ax.annotate(
                label,
                xy=(energy, yval*1.2),  # arrow points to actual peak
                xytext=(energy, final_yval),  # adjusted text position
                arrowprops=dict(facecolor='black', arrowstyle='->', lw=0.5),
                fontsize=10,
                ha='center'
            )

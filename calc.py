import matplotlib.pyplot as plt
import numpy as np
from PyMca5.PyMcaIO.ConfigDict import ConfigDict
from PyMca5.PyMcaPhysics.xrf import Elements

class specPlot():
    def __init__(self, pathnameCFG):
        self.pathnameCFG = pathnameCFG
        self.zerogain, self.names = self.readcfg() # zerogain and names needed for annotations
    
    def readcfg(self):
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

# Import
import matplotlib.pyplot as plt
import csv
import numpy as np
class specPlot():
    def __init__(self, pathnameCSV, pathnameCFG, labelgraph, colour, offset=0):
        self.pathnameCSV = pathnameCSV
        self.pathnameCFG = pathnameCFG
        self.energy, self.counts = self.readcsv()
        self.zerogain, self.names = self.readcfg()
        self.labelgraph = labelgraph
        self.offset = offset
        self.colour = colour

    def readcsv(self):  # Read CSV file
        energy = []
        counts = []
        with open(self.pathnameCSV, 'r') as fileCSV:
            csv_reader = csv.reader(fileCSV)
            
            # skip first 29 rows & read the rest
            for _ in range(29):
                next(csv_reader, None)  # Avoid StopIteration error
            for row in csv_reader:
                if len(row) >= 2:
                    energy.append(float(row[0]))
                    counts.append(float(row[1]))

        return energy, counts
    
    def readcfg(self):
        from PyMca5.PyMca import ConfigDict
        config = ConfigDict.ConfigDict()
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
    
    def annotation(self):
        from PyMca5.PyMcaPhysics.xrf import Elements
        handles = plt.gca().get_lines()  # Get plotted data handles
        
        used_positions = []  # Store used y-positions to avoid overlap
        
        for n in self.names:
            if n in ['Rayl', 'Compt']:
                continue  # Skip Rayleigh and Compton scattering peaks
            
            element, transition = n.split(" ")  # Separate element & transition
            
            energy = None
            label = None

            # Handle K-series transitions (for Ka and Kb)
            if transition == 'K':  
                energy = Elements.getxrayenergy(element, 'KL3')
                label = f"{element} Kα"
            elif transition == 'Ka':
                energy = Elements.getxrayenergy(element, 'KL3')
                label = f"{element} Kα"
            elif transition == 'Kb':
                energy = Elements.getxrayenergy(element, 'KM3')
                label = f"{element} Kβ"

            # Handle L-series transitions
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
            
            # Find closest x_data point
            x_data = handles[0].get_xdata()
            valid_indices = np.where(x_data <= energy)[0]
            if valid_indices.size > 0:
                idx = max(valid_indices)
            else:
                continue  # Skip if no valid data point

            # Get y-value at closest energy
            y_values = [hand.get_ydata()[idx] for hand in handles if len(hand.get_ydata()) > idx]
            if not y_values:
                continue
            
            yval = max(y_values)

            # **Start with default spacing (same as your original)**
            base_offset = 3 # Adjust text height relative to peak
            final_yval = (yval - 0.01*yval) * base_offset  

            # **Overlap Fix: Adjust if labels are too close**
            min_spacing_factor = 1.15  
            while any(abs(np.log10(final_yval) - np.log10(used_y)) < 0.1 for used_y in used_positions):
                final_yval *= min_spacing_factor  # Push it up slightly

            used_positions.append(final_yval)  # Store adjusted position

            plt.annotate(
                label,
                xy=(energy, yval*1.2),  # Arrow points to actual peak
                xytext=(energy, final_yval),  # Adjusted text position
                arrowprops=dict(facecolor='black', arrowstyle='->', lw=0.8),
                fontsize=12,
                ha='center'
            )


    def plot(self):
        counts = [count + self.offset for count in self.counts]
        energy = np.array(self.energy)
        plt.plot((self.zerogain[0] + energy * self.zerogain[1]), counts, linewidth=1, label=self.labelgraph, color=self.colour)


# data
name = '2147'
spectra = [
    ('/Users/burrito/Stage KIKIRPA/CaseStudies/Klavecimbel-Ruckers/xrfCSV/0'+name+'-GeoExploration_xrf_spectrum.csv',
     '/Users/burrito/Stage KIKIRPA/CaseStudies/Klavecimbel-Ruckers/PyMCA/0'+name+'.cfg', "XRF-spectrum", "brown", 0, True)
]
plt.title(name, fontsize=20)
plt.xlim(1, 14)
plt.ylim(10, 10**6)


# plot spectrum and annotations
for pathnameCSV, pathnameCFG, labelgraph, colour, offset, anno in spectra:
    spec = specPlot(pathnameCSV, pathnameCFG, labelgraph, colour, offset)
    spec.plot()
    if anno == True:
        spec.annotation()

plt.xlabel("Energy [keV]", fontsize=18)
plt.yscale("log")
plt.ylabel("Intensity [Counts]", fontsize=18)
plt.legend(fontsize=13) 
plt.gcf().set_size_inches(15, 8)
plt.savefig('/Users/burrito/Stage KIKIRPA/CaseStudies/Klavecimbel-Ruckers/spectra/'+name+'.png', dpi=300)
plt.show()

import numpy as np
from nicegui import ui, events
import main

import pandas as pd 
from io import StringIO

    
def csv_file_loaded(e: events.UploadEventArguments):
    with StringIO(e.content.read().decode("utf-8")) as f:
        df = pd.read_csv(f, usecols=["channel", "counts"], sep = "\t")
    channels = (df['channel'].tolist())
    counts = (df['counts'].tolist())
    with fig:
        ax = fig.gca()
        x = [count + offset for count in counts]
        y = np.array(channels)
        energy = zerogain[0] + y * zerogain[1]
        ax.plot(energy , x, linewidth=0.5, label=labelgraph, color=colour)
        # settings spectra
        ax.set_title(title, fontsize=titlesize)
        ax.set_xlabel(xlabelInput.value, fontsize=sizeInput.value)
        ax.set_ylabel(ylabelInput.value, fontsize=sizeInput.value)
        ax.set_xlim(1, 14)
        ax.set_ylim(5, 10**6)
        ax.set_yscale("log")
        ax.legend(fontsize=10) 
    annoTrue()
        
    
    
# values for plot
cfg_file = '/Users/burrito/Library/CloudStorage/OneDrive-Personal/Stage KIKIRPA/CaseStudies/Klavecimbel-Ruckers/XRF/PyMCA/02145.cfg'
spec = main.specPlot(cfg_file, labelgraph="XRF-spectrum", offset=0)
zerogain, names = spec.readcfg()
title="Plot" 
titlesize=10
labelgraph = "test"
colour = "brown"
offset = 0
### GUI SCREEN ###
ui.markdown('### hXRF spectrum viewer')
# adjustable values in GUI

with ui.row():
    xlabelInput = ui.input('Label x-axis',value="Energy [keV]")
    sizeInput = ui.number('X-axis label font size', value=10, min=1)
xlabel = xlabelInput.value
size = sizeInput.value
ylabelInput = ui.input('Label y-axis', value="Intensity [Counts]")
ylabel = ylabelInput.value

def updates():
    with fig:
        ax = fig.gca()
        ax.set_xlabel(xlabelInput.value, fontsize=sizeInput.value)
        ax.set_ylabel(ylabelInput.value, fontsize=sizeInput.value)
    ui.update(fig)

def annotationUp():
    with fig:
        ax = fig.gca()
        spec.annotation(ax)
    ui.update(fig)
    
fig = ui.matplotlib(figsize=(15, 6)).figure

with ui.row():    
    ui.upload(on_upload=csv_file_loaded).props("accept=.csv").classes("max-w-full")
    def annoTrue():
        ui.upload(on_upload=annotationUp).props("accept=.cfg").classes("max-w-full")
ui.button('Update plot!', on_click=updates)
ui.run()
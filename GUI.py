import numpy as np
from nicegui import ui, events, native
import main
import tempfile
import pandas as pd 
from io import StringIO
import os

### functions ###
    
def csv_file_loaded(e: events.UploadEventArguments):
    with StringIO(e.content.read().decode("utf-8")) as f:
        df = pd.read_csv(f, usecols=["channel", "counts"], sep = "\t")
    global channels, counts
    channels = (df['channel'].tolist())
    counts = (df['counts'].tolist())
    
    anno.visible = True
    
    

def cfg_file_loaded(e: events.UploadEventArguments):
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.cfg', delete=False) as tmp:
        tmp.write(e.content.read().decode("utf-8"))
        tmp_path = tmp.name  # Store the file path
    global spec, zerogain, names
    spec = main.specPlot(tmp_path, offset=offset)
    zerogain, names = spec.readcfg()  # Update global values if needed
    os.remove(tmp_path)
    with fig:
        ax = fig.gca()
        ax.clear()
        x = [count + offset for count in counts]
        y = np.array(channels)
        energy = zerogain[0] + y * zerogain[1]
        ax.plot(energy , x, linewidth=0.5, color=colour)
        # settings spectra
        ax.set_title(titleInput.value, fontsize=tsizeInput.value)
        ax.set_xlabel(xlabelInput.value, fontsize=sizeInput.value)
        ax.set_ylabel(ylabelInput.value, fontsize=sizeInput.value)
        ax.set_xlim(minx.value, maxx.value)
        ax.set_ylim(miny.value, maxy.value)
        ax.set_yscale("log")
    
    annotationUp()


def annotationUp():
    with fig:
        ax = fig.gca()
        spec.annotation(ax)
    ui.update(fig)
    
def updates():
    with fig:
        ax = fig.gca()
        ax.set_title(titleInput.value, fontsize=tsizeInput.value)
        ax.set_xlabel(xlabelInput.value, fontsize=sizeInput.value)
        ax.set_ylabel(ylabelInput.value, fontsize=sizeInput.value)
        ax.set_xlim(minx.value, maxx.value)
        ax.set_ylim(miny.value, maxy.value)
    ui.update(fig)
        
# values for plot

colour = "brown"
offset = 0
    
### GUI SCREEN ###

ui.markdown('### **hXRF Spectrum Viewer**').classes('mx-auto text-center')
with ui.row().classes('w-full justify-center'):    
    with ui.column(): 
        ui.upload(label="Load .csv file here",on_upload=csv_file_loaded).props("accept=.csv").classes("max-w-full")
        anno = ui.upload(label="Load .cfg file here",on_upload=cfg_file_loaded).props("accept=.cfg").classes("max-w-full")
        anno.visible = False
        
    with ui.card().classes('items-center'):
        ui.markdown('**Adjust plot**').classes('mx-auto text-center')
        with ui.grid(columns=5):    
            xlabelInput = ui.input('Label x-axis',value="Energy [keV]")
            sizeInput = ui.number('Label font size', value=10, min=1)
            titleInput = ui.input('Title',value="XRF-spectrum")
            minx = ui.number('Min. value X-axis', value=1)
            miny = ui.number('Min. value Y-axis', value=5)
            
            ylabelInput = ui.input('Label y-axis', value="Intensity [Counts]")
            tsizeInput = ui.number('Title font size', value=10)              
            ui.button('Update plot!', on_click=updates)   
            maxx = ui.number('Max. value X-axis', value=15)
            maxy = ui.number('Max. value Y-axis', value=10**6)

                
                
# spectrum viewer
with ui.column():
    ui.markdown('### Spectrum').classes('mx-auto text-center')
    fig = ui.matplotlib(figsize=(15, 6)).figure
        
ui.colors(primary='#BC6F27')
ui.add_head_html('<style>body {background-color: #E2D4BC; }</style>')
ui.run(native=True, reload=False, port=native.find_open_port())
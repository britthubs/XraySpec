import FreeSimpleGUI as sg
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import main # file tha thas specplot class

# Function to draw the Matplotlib figure with a toolbar
def draw_figure_w_toolbar(canvas, fig, canvas_toolbar):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if canvas_toolbar.children:
        for child in canvas_toolbar.winfo_children():
            child.destroy()
    # Create the Matplotlib figure canvas
    figure_canvas_agg = FigureCanvasTkAgg(fig, master=canvas)
    figure_canvas_agg.draw()
    # Create the toolbar and attach it to the canvas
    toolbar = NavigationToolbar2Tk(figure_canvas_agg, canvas_toolbar)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='right', fill='both', expand=False)
    toolbar.pack(side="top", fill="x")

# Define your window layout
layout = [
    # First row: Import .csv file and Title input field beside it
    [sg.Push(), sg.Text("Import .csv file:"), sg.In(key='-CSV-'), sg.FileBrowse(),
     sg.Text("Title:", size=(20, 1)), sg.InputText("", key='-INPUT_FIELD-', size=(40, 1))],
    
    # Second row: Import .cfg file
    [sg.Push(), sg.Text("Import .cfg file:"), sg.In(key='-CFG-'), sg.FileBrowse(),
     sg.Text("Title font size:", size=(20, 1)), sg.InputText("", key='-INPUT_FIELD-', size=(10, 1))],
    
    # Third row: Ok and Cancel buttons
    [sg.Button('Ok'), sg.Button('Cancel')],
    
    # Fourth row: Canvas for the toolbar
    [sg.Canvas(key='controls_cv', size=(400, 100))],
    
    # Fifth row: Canvas for the plot
    [sg.Canvas(key='fig_cv', size=(800, 600))]
]

window = sg.Window('Create Spectrum', layout, size=(1000, 800))

spec = None  # Declare spec outside of the loop to make sure it's accessible

while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, 'Cancel'):  # Exit condition
        break

    if event == 'Ok':  # When 'Ok' button is pressed
        csv_file = values['-CSV-']
        cfg_file = values['-CFG-']

        if csv_file and cfg_file:
            # Initialize specPlot class
            spec = main.specPlot(csv_file, cfg_file, "XRF-spectrum", "brown", 0)
            
            # Retrieve the title from the input field if provided
            title = values['-INPUT_FIELD-'] if values['-INPUT_FIELD-'] else "XRF Spectrum"
            
            # Generate the plot with the title (passing the title to the plot function)
            fig = spec.plot(title)  # Pass the title here
            
            # Embed figure and toolbar in the GUI
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)


    if event == '-INPUT_FIELD-':  # This event triggers when the input changes
        if spec:  # Ensure spec is not None
            title = values['-INPUT_FIELD-']  # Get the value from the input field
            fig = spec.plot(title)  # Get the figure from the plot method

            # Update the plot with the new title
            draw_figure_w_toolbar(window['fig_cv'].TKCanvas, fig, window['controls_cv'].TKCanvas)

window.close()

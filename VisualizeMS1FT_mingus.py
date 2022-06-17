import pandas as pd
    # data anlysis toolkit
        # used to convert data table (from reading .csv file) into NumPy matrix array in
        # df_ms1ft = pd.read_csv(file_path)
import numpy as np
    # numpy: for working with arrays
        ''' weirdly can't find where we're using numpy '''
import tkinter as tk
    # tkinter: for Tcl/Tk GUI toolkit
        # makes one window, the hidden root window that runs the application before output is displayed
from bokeh.io import output_file, show
    # show: displays a bokeh object or application
        # used when show(grid) displays, where grid contains both interactive figures p (the heat map) and
        # iso_distrib (the chart triggered by clicking on a mass's bar on the heat map)
    # output_file: configures the default output state to generate output *saved to a file* when show() is called
        # used to display featuremap.html inline (opens figures in default web browser)
from bokeh.models import (BasicTicker, ColorBar, ColumnDataSource, CustomJS, TapTool,
                          LogColorMapper, PrintfTickFormatter, HoverTool)
    ''' need to read about these but their names say plenty '''
from bokeh.events import Tap
    # Tap: clicking in a certain spot (x,y) on the screen triggers some callback
        # used to make data in heat map clickable and trigger isotopic distribution chart
        ''' confused about what's going on with (x,y) in CustomJS but idk JS so there's that.
            i guess this just does something fancy to say (x,y) is on mass_blah's bar? '''
from bokeh.plotting import figure, curdoc
    # figure: creates a Figure model (which composes axes, grids, tools,... and has methods to add error bars etc.)
        # used to create featuremap figures, the charts i think
    # curdoc: returns the default document object
        ''' never used? '''
from bokeh.sampledata.unemployment1948 import data
    ''' downloads sample data set. was this used for testing? not finding it used anywhere now. '''
from bokeh.transform import transform
    # transform(field_name: str, transform: Transform): creates a DataSpec dict that applies an arbitrary
    # client-side Transform to a ColumnDataSource column
        # used once, I think to color the clickable mass (?) bars by abundance in the isotopic distribution heat map?
        # mass = p.rect(x, y, width, height, source, line_color, fill_color=transform('Abundance', mapper))
from bokeh.layouts import gridplot
    # gridplot: a function which arranges bokeh plots in a grid and merges all plot tools into a single
    # toolbar so that each plot in the grid has the same active tool
        # used to merge both heatmap and 
from bokeh.resources import INLINE
    # INLINE: provides minified BokehJS from library static directory
        ''' not sure where this is used, or how. maybe it's used to configure the output html file inline:
                            output_file("featuremap.html", mode='inline') '''
from tkinter import filedialog
    # filedialog: provides a set of dialogs to use when working with file, such as open, save, etc.
        # used to upload & open ms1ft .csv files


root = tk.Tk()          # creates an instance of tkinter frame, the root window
root.withdraw()         # hides window w/o destroying it internally, deiconify() to reveal


'''
ENVELOPE HISTOGRAM
    INPUT - ms1ft file (.csv) has the following columns in this order:
        FeatureID, MinScan, MaxScan, MinCharge, MaxCharge, MonoMass,
        RepScan, RepCharge, RepMZ, Abundance, ApexScanNum, ApexIntensity,
        MinElutionTime, MaxElutionTime, ElutionLength, Envelope, Likelihood Ratio 
    OUTPUT - updates data in input file, adds isotope and abundance lists to columns 'C13' and 'IsoAbd'?
    DESCRIPTION - Takes an MS1FT file and organizes relevant data from the Envelope column so it can be used in
    making charts (one heat map as well as an isotope distribution for each mass). Called in app after uploading input file.
'''
def EnvelopeHistogram(df_ms1ft):
    envelope = list(df_ms1ft['Envelope'])               # creates a list out of the data in the Envelope column [P1, P2, P3, ...]
                                                        # each cell of this column contains a list of pairs of numbers a,b;c,d;e,f;...
                                                            ''' first element is the isotope or idx and second element is the abundance or val? '''
                                                        # each pair is separated by ; and elements of the pair are separated by ,
    carb_isotope = []
    carb_abundance = []
    convert = []
    pool_c13 = []
    pool_isoabd = []
     
    for distribution in envelope:                       # for each data point in Envelope, I think a list [a,b;c,d;e,f;...]?
        v=[]                                                    # create an empty array
        for idx, val in enumerate(distribution):                # iterate through... each pair a,b in the list? no
            if val == ',':                                          # , implies second element in the same pair, add data as int to carb isotope array
                link = "".join(convert)                                 ''' not sure what this is doing. can we remove this '''
                carb_isotope.append(int(link))                          ''' and do carb_isotope.append(int(convert)) here? '''
                convert = []
            elif val == ';':                                        # ; implies new pair, first element, add data as float to carb abundance array
                link = "".join(convert)                                 ''' same here '''
                carb_abundance.append(float(link))                      ''' same here '''
                convert = []
            else:
                convert.append(val)                                 # not , or ; implies element, add to temp var convert and decide where it goes later
                                                                    # last element in last pair gets appended to abundance array since it is followed by ;
        
        pool_c13.append(carb_isotope)                           # appends carb isotope array to pool_c13
        pool_isoabd.append(carb_abundance)                      # appends carb abundance array to pool_isoabd
        carb_isotope,carb_abundance = [],[]                     # resets isotope and abundance arrays 

    # after going through all datapoints in envelope, add gathered data to columns 'C13' and 'IsoAbd' in df_ms1ft .csv file?
    df_ms1ft['C13'],df_ms1ft['IsoAbd'] = pool_c13, pool_isoabd 


''' Rest of Code '''
# Upload file (retrieve file path)
file_path = filedialog.askopenfilename(title="Select an MS1FT .csv File", filetypes=[("Select an MS1FT .csv File","*.csv")])

# Extract file name from path
filename = []
for character in file_path:
    filename.append(character)
filename.reverse()
temp_name =[]
for character in filename:
    if character != '/':
        temp_name.append(character)
    else:
        break
temp_name.reverse()
ext_filename = ''.join([str(elem) for elem in temp_name])
                
if len(file_path) >0:
    df_ms1ft = pd.read_csv(file_path)
    df_ms1ft = df_ms1ft.sort_values('MonoMass').set_index('MonoMass')
else:
    exit()
    
output_file("featuremap.html", mode='inline')

EnvelopeHistogram(df_ms1ft)

source = ColumnDataSource(df_ms1ft)
source2 = ColumnDataSource(data=dict(x=[], y=[]))

colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
mapper = LogColorMapper(palette=colors, low=df_ms1ft['Abundance'].min(), high=df_ms1ft['Abundance'].max())

p = figure(width=1000, height=800, title="Feature Map of "+ext_filename,
           x_range=(0,df_ms1ft['MaxElutionTime'].max()+1), y_range=(0,df_ms1ft.index.max()+1),
           toolbar_location="right",  x_axis_location="below",active_drag="box_zoom",active_scroll="wheel_zoom",)

iso_distrib = figure(width = 500, height = 400, title="Isotopic Distribution",x_axis_label="C13", tools="pan,box_zoom,wheel_zoom,reset,undo,save",
                    active_scroll="wheel_zoom",y_axis_label="Rel. Abundance", active_drag="box_zoom")
 
z = iso_distrib.vbar(x='x', width=0.5, bottom=0, top='y', color="red", source=source2)


mass = p.rect(x="MinElutionTime", y="MonoMass", width='ElutionLength', height=10, source=source,
       line_color=None, fill_color=transform('Abundance', mapper))


p.add_tools(TapTool())

p.js_on_event(Tap, CustomJS(args=dict(source=source, source2=source2,title=iso_distrib.title), code="""
    // get data source from Callback args
    let data = Object.assign({}, source.data);
    source2.data.x = data.C13[source.selected.indices];
    source2.data.y = data.IsoAbd[source.selected.indices];
    title.text = 'Isotopic Distribution for: '+(new String(data.MonoMass[source.selected.indices]));
    source2.change.emit();
""")
)

color_bar = ColorBar(color_mapper=mapper, title="Log Abundance")

p.add_layout(color_bar, 'right')

p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.xaxis.axis_label = 'Retention Time (min)'
p.yaxis.axis_label = 'Monoisotopic Mass'
p.axis.major_label_text_font_size = "20px"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = 1.0
p.axis.axis_label_text_font_size = "20px"

grid = gridplot([[p,iso_distrib]], merge_tools=False)       # p is heat map, iso_distrib are individual charts you get from clicking on masses?
show(grid)

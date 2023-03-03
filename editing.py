"""
TITLE: Mass_Finder_and_Quantifier.py

INPUT: msalign file(s) (.csv)
*must be in same folder as application

OUTPUT: interactive quant graphs (.html), quant data (.csv)

DESCRIPTION: This application takes the msalign file(s) resulting from running
FlashDECONV on the mass spectrum of some sample(s), and uses this data along with
user input retrieved in app to plot the mass vs. abundance of all samples on the same
interactive mass vs. abundance graph. User input is straightforward & minimal:
   - Users will be prompted to upload msalign files (at least one is required).
   - Each file can be re-labeled (e.g. "control group", "stage 1") in app immediately
   after uploading. These labels help distinguish between samples on the graph legend.
   A default label ("exp. group") is provided.
   - Users are prompted to specify the mass ranges, retention times, etc that they are
   interested in seeing plotted. Default values are provided.
The interactive output graph (with a quality control graph for each file uploaded)
is generated in browser, where users can further inspect & compare the samples'
data. A csv file containing the same information as the main graph is saved to the
same folder as the application and input files.

NOTE: While the program runs, many additional features (such as the "New Analysis"
and "Test" buttons) are broken and the code (& console) are messy. Currently we've been
working on switching to pandas, so several functions have "two versions" of code with
one commented out. This switch has been difficult because of these functions kind of 
depend on each other. So all of the commented code (attempts to use pandas) result in
errors, but I'm not sure if that's because I'm doing things wrong or just because without
everything in the same format throughout, I get a bunch of inconsistencies. I'm running
into a similar problem with what I was hoping would be a solution, the "Test" function -
I don't know how to get all these functions from different classes to talk to each other.
"""

import timeit
    # used to determine function runtime while editing & testing
import pandas as pd
    # data anlysis toolkit
        # used to convert data table (from reading .csv file) into NumPy matrix array in
        # df_ms1ft = pd.read_csv(file_path)
import numpy as np
    # numpy: for working with arrays
    # append, reshape, array
import tkinter as tk
    # tkinter: for Tcl/Tk GUI toolkit (standard, n  ot necessarily best?)
    # Frame, Button, Label, Entry, Checkbutton
import time, sys    # -----------------------------------------------------------------> import time?
    # time: for time-related functions, such as strptime() used in output_quant_file and qc_graph
    # sys: to access system-specific parameters and functions, i/o
        # seemse like it's only being used for one output line, which is commented out
import matplotlib                               # remove and test
import matplotlib.pyplot as plt
    # pyplot: makes matplotlib work like matlab, used for plotting qc graphs
import matplotlib.backends._tkagg
matplotlib.use("TkAgg")
    # backends._tkagg: to use matplotlib with tkinter, more imports from here below
from matplotlib import style
style.use('ggplot')
    # style: used to customized appearance of plots,
    # ggplot: a style that emulates the ggplot package for R
import os, time     # -----------------------------------------------------------------> import time?
    # os: "provides a portable way of using operation system dependent functionality"
    # i'm guessing these are just used to access the date&time on the computer, for plotting?
import statistics
    # statistics: don't think we need everything in here, just pstdev and mean
    # used in calculate_avg_stdev() in QuantOutput
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    # FigureCanvasTkAgg: interface between the Figure and Tkinter Canvas
    # NavigationToolbar2Tk: built-in toolbar for the figure on the graph
    # these make the graph interactive as desired
    # in makegraph(), specifications for toolbar are passed in as parameters
from matplotlib.figure import Figure
    # Figure: contains all plot elements, used to control spacing of subplots & container
    # needed for multiple qc graphs in case of multiple msalign file uploads
from operator import itemgetter, attrgetter         # not sure how/where these are used
    # itemgetter: constructs a callable that assumes an iterable object and returns the nth element
    # attrgetter: returns a callable object that fetches one/more attributes from its operand
from datetime import datetime
    # datetime: such as datetime, used in output_quant_file and qc_graphs
from tkinter import filedialog as fd                                    # REMOVE
    # filedialog: provides a set of dialogs to use when working with file, such as open, save, etc.
    # used askopenfilename once in msalignfile() in FileSelection
from tkinter import messagebox as mb
    # messagebox: provides a template base class for messageboxes
    # used to display error messages during file uploads
from tkinter import ttk
    # ttk: provides acces to Tk themed widge set - buttons, etc.
from tkinter import *                           # remove and test
from collections.abc import Iterable
    # Iterable: provides abstract base classes that can be used to test whether a class
    # provides a particular interface, so like issubclass() or isinstance()
from bokeh.models import ColumnDataSource, Whisker, HoverTool, Legend, LegendItem
    # ColumnDataSource: provides data to the glyphs of plot so you can pass in lists, etc.
    # Whisker: adds a whisker for error margins
    # HoverTool: passive inspector tool, for actions to occur when cursor hovering
    # Legend: allows us more advanced control of the legend object provided by bokeh for the graphs
    # LegendItem: set True to have legend visible, False to hide legend
from bokeh.plotting import figure, show
    # figure: a function that creates a Figure model, which composes axes, grids, default tools, etc.
    # and includes methods for adding different kinds of glyphs (shapes & things) to a plot
    # show: displays the figure
from bokeh.layouts import gridplot
    # gridplot: a function which arranges bokeh plots in a grid and merges all plot tools into a single
    # toolbar so that each plot int he grid has the same active tool
from bokeh.io import output_file
    # output_file: configures the default output state to generate output saved to a file when show()
    # is called
from bokeh.palettes import Category20b, Category20c
    # Category20b: 4 purple, 4 green, 4 brown, 4 red, 4 pink
    # Category20c: 4 blue, 4 orange, 4 green, 4 purple, 4 grey
from bokeh.transform import dodge
    # dodge: creates a DataSpec dict that applies a client-side Dodge transformation to a
    # ColumnDataSoure column. has parameters:
        # field_name (str) - a field name to configure DataSpec with
        # value (float) - the fixed offset to add to column data
        # range (Range, optional) - a range to use for computing synthetic coordinates when necessary,
        # e.g. a FactorRange when the column data is categorical (not the fun kind)
from tkinter import filedialog
    # filedialog: provides a set of dialogs to use when working with file, such as open, save, etc.
        # used to upload & open ms1ft .csv files

LARGE_FONT= ("Verdana", 12)

"""
APP - uses tkinter to build application
init() - builds app window (Frame) and pages (frame)
show_frame(page_name) - displays given page
new_analysis() - refreshes app for new analysis (BROKEN)
"""
class App(tk.Tk):
    msalign_filearray = []      # [filelabel (file's unique id), ext_filename (file name), ...] (2 vals for each msalign file)
    processed_filearray = []
    expgroup = []
    total_files = 0
    Test = True                # shows test button, which performs a test run of n identical files (for testing only, WIP)

    def __init__(self, *args, **kwargs):
        # must call __init__ to use tkinter objects (self throughout)
        tk.Tk.__init__(self, *args, **kwargs)                   # not sure if all args needed since only one App
        tk.Tk.wm_title(self,"Mass Finder and Quantifier")       # App title is "Mass Finder and Quantifier"

        # create the Frame the App is contained in (container for App)
        container = tk.Frame(self)
        container.grid(column=0, row=0, sticky='news')
        container.grid_rowconfigure(0, weight=1)                # container index 0 has width x1 (regular)
        container.grid_columnconfigure(0, weight=1)             # container index 0 has height x1 (regular)
        self.geometry("1280x740")                               # size of window (width x height) in pixels

        # creates the frames (pages in the App)
        self.frames = {}
        for F in (StartPage, FileSelection, SearchParams, QuantOutput, QCGraphs):
            frame = F(container, self)                          # creates a frame for each page
            self.frames[F] = frame                              # adds to App's array self.frames
            frame.grid(row=0, column=0, sticky="news")

        # app opens with Start Page
        self.show_frame(StartPage)

    # show_frame(): shows a page of the app (usually called when a button is pressed, except above)
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # new_analysis(): BROKEN probably because code execution stops with app.mainloop()
    # so python's not reading anything after the "New Analysis" button is pressed
    def new_analysis(self):
        app = App()
        app.mainloop()

    # test_app(): BROKEN want this to run one selected file through the program (some number of times),
    # keeping track of runtimes of each function with timeit. currently timing is placed throughout the
    # code and outputs to console and .csv. once this is done we only calculate & output runtimes when
    # running this test function.
    def test_app():
        file_path = filedialog.askopenfilename(title="Please select an MS1 MSALIGN file", filetypes=[('All files','*.*')])
        return


"""
START PAGE - builds 'Start Page' with all its buttons.
This is immediately displayed upon running the app.
"""
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        # Start Page creation & initialization
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        # Each button has a lambda calling show_frame to display a certain page
        # all buttons are in the same row (0) but different columns (0,1,2,3)

        # File Selection Button
        button1 = ttk.Button(self, text="MS1 File Selection",
                            command=lambda: controller.show_frame(FileSelection))
        button1.grid(column=0, row=1, sticky='w')

        # Search Parameters Button
        button2 = ttk.Button(self, text="Search Parameters",
                            command=lambda: controller.show_frame(SearchParams))
        button2.grid(column=1, row=1, sticky='w')

        # Results Output Button
        button3 = ttk.Button(self, text="Results Output",
                            command=lambda: controller.show_frame(QuantOutput))
        button3.grid(column=2, row=1, sticky='w')

        # QC Graphs Button
        button4 = ttk.Button(self, text="Quality Control Graphs",
                            command=lambda: controller.show_frame(QCGraphs))
        button4.grid(column=3, row=1, sticky='w')

        # Test Button - still building but also don't know how to call this???
        # this fn feeds constant input file to program n times and
        # bypasses all user input including parameter entries and button clicks
        # while running all functions normally and timing them...
        if App.Test==True:
            button5 = ttk.Button(self, text="Test n Files",
                                command=lambda: test_app())
            button5.grid(column=4, row=1, sticky='w')


"""
FILE SELECTION
Clicking "MS1 File Selection" on the 'Start Page' leads to the
'MS1 File Selection' page, which has two buttons, one for "New Analysis"
and one for "Add File". Once one file has been uploaded, a button to
"Process Files" appears, created within msalignfile().
- temp: can add max of 20 files
"""
class FileSelection(tk.Frame):
    gridrow = 4
    gridcolumn = 0
    button_identities = []
    filelabel_identities = []
    group_identities = []

    def __init__(self, parent, controller):
        # File Selection Page creation & initialization
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="MS1 File Selection", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        # New Analysis Button
        button2 = tk.Button(self, text="New Analysis",
                            command=lambda: controller.new_analysis())
        button2.grid(column=1, row=1, sticky='w')

        # Add File Button
        addbutton = tk.Button(self, text='Add File',  fg="green", command=(lambda : self.msalignfile()))
        addbutton.grid(column=0, row=2,sticky='w')

        self.controller = controller


    # MSALIGNFILE(): uploads a new msalign file and builds/updates File Selection Page
    # throughout upload process, called each time "Add File" button is pressed.
    def msalignfile(self):
        if App.total_files > 20:                # 20 file max (temporary)
            mb.showerror("Warning","Cannot load more files. Maximum files (20) reached.")
            
        else:
            # Retrieve file path from upload
            file_path = filedialog.askopenfilename(title="Please select an MS1 MSALIGN file", filetypes=[('All files','*.*')])

            # Extract file name from file path
                # given file_path = './.../.../.../filename.ext'
                # slice reverse, to get 'txe.emanelif/.../.../.../.'
                # append all chars until first '/' to temp array, to get 'txe.emanelif' (as array)
                # reverse temp array then convert to string, to get 'filename.ext'
            temp_name = []                      # temp_name will store name as it builds
            for char in file_path[::-1]:        # step thru each char in reversed file_path
                if char != '/':
                    temp_name.append(char)      # append all non-'/' chars to temp_name
                else:
                    break                       # stop process at first '/'
            temp_name.reverse()                 # reverse to get chars in original order
            ext_filename = ''.join([str(char) for char in temp_name])   # store as string

            # Display uploaded files in app frame (one per row) while
                # allowing user to label each file by group (e.g. 'exp group', 'ctrl group')
                # allowing user remove individual uploaded files with a button
            if ext_filename != "":
                # build filelabel, static box for uploaded file (displays ext_filename, not whole path)
                # also used as unique id in msalign_filearray?
                filelabel = Label(self, text = 'File: '+ ext_filename)
                filelabel.grid(row=FileSelection.gridrow, column=FileSelection.gridcolumn, sticky='w')
                FileSelection.filelabel_identities.append(filelabel)

                # entry box for editable file label (default is 'exp. group')
                group_label_entry = tk.Entry(self, width=13)
                group_label_entry.grid(row=FileSelection.gridrow, column=int(FileSelection.gridcolumn)+1, sticky='w')
                group_label_entry.insert(0,'<exp. group>')
                FileSelection.group_identities.append(group_label_entry)

                # removebutton is created alongside & specific to each uploaded file
                # it uses a lambda that calls the function "Xclick", defined below this fn
                removebutton = tk.Button(self, text='X', fg="red", command=(lambda : Xclick(filelabel,group_label_entry,removebutton)))
                removebutton.grid(row=FileSelection.gridrow, column=int(FileSelection.gridcolumn)+2)
                FileSelection.button_identities.append(removebutton)

                # update File Selection Page with the stuff we just made
                FileSelection.gridrow += 1
                App.msalign_filearray.append(filelabel)
                App.msalign_filearray.append(ext_filename)
                App.total_files+=1

            # timing has to start after user interaction so I guess I'll start it here...
            start_time = timeit.default_timer()
                
            # only show "Process Files" button once there are files to process
            if len(App.msalign_filearray) == 2:         # if something uploaded, msalign_file array should have 2 vals (file label & name)
                processbutton = tk.Button(self, text='Process File(s)', name='processbutton',  fg="green", command=(lambda : populate_entries()))
                processbutton.grid(column=0, row=20, sticky='w')

        # timing end
        total_time = timeit.default_timer() - start_time
        print('Fileselection \t msalignfile \t\t\t', total_time)
        with open("timing_0_msalignfile_blah.csv", "a") as out_file:
            out_file.write(str(total_time))
            out_file.write("\n")


        # XCLICK(): for a selected file, destroys its boxes on the File Selection Page
        # (filelabel, entry box, and removebutton) and the corresponding values in
        # the identity arrays for those 3 values, then destroys its 2 values in
        # msalign_filearray and updates the app's total number of files, removing
        # the "Process Files" button if this is 0. Result is as though the
        # selected file was never uploaded.
        def Xclick(filelabel, group_label_entry, removebutton):
            # timing start
            start_time = timeit.default_timer()

            # idk what this commented out part is, keeping in case important
            # n = FileSelection.filelabel_identities.index(filelabel)

            # destroy file's boxes on File Selection page
            filelabel.destroy()
            group_label_entry.destroy()
            removebutton.destroy()
            
            # destroy file's vals in identity arrays
            FileSelection.filelabel_identities.remove(filelabel)
            FileSelection.group_identities.remove(group_label_entry)
            FileSelection.button_identities.remove(removebutton)
            
            # remove file's name and label from msalign_filearray
            for i in App.msalign_filearray:
                if i == filelabel:
                    del App.msalign_filearray[App.msalign_filearray.index(i)+1]
                    del App.msalign_filearray[App.msalign_filearray.index(i)]

            # update total # of files, if 0 remove "Process Files" button
            App.total_files-=1
            if len(App.msalign_filearray) == 0:
                self.nametowidget('processbutton').destroy()

            # timing end
            total_time = timeit.default_timer() - start_time
            print('FileSelection \t Xclick \t\t\t', total_time)
            with open("timing_0_Xclick_blah.csv", "a") as out_file:
                out_file.write(str(total_time))
                out_file.write("\n")


        # POPULATE_ENTRIES(): fills msalign_filearray with data from group_identities array,
        # called after all input files are uploaded and 'Process Files' button is pressed
        def populate_entries():
            # timing start
            start_time = timeit.default_timer()

            # Fill expgroup (array) with group names (e.g. 'exp. group')
            # parse through group_identities, one per file but many can hold same string val
            for group in self.group_identities:     # TO DO could be one line?
                group_name = group.get()            # group_label_entry in msalignfile()
                App.expgroup.append(group_name)     # ^ these fill prev empty array expgroup

            ''' TO DO time consuming nested for loops and seems unnecessary
                but making the changes suggested below results in
                IndexError in makegraph, in this line
                max_graphs = len(QCGraphs.total_qc_graph_array[0][1])'''
            # abbreviate msalign MS1 filenames for graphing display
            # for each file (2 vals per file in this array, so skip=2)
            for i in range(1,len(App.msalign_filearray),2):     # len(...) = # of input files
                # get each file's name from... its name?
                # i wanted to delete from here ------------------------------
                filename = []
                for character in App.msalign_filearray[i]:
                    filename.append(character)
                filename.reverse()
                temp_name =[]
                for character in filename:
                    if character != '/':
                          temp_name.append(character)
                    else:
                        break
                temp_name.reverse()
                temp_name_to_str = ''.join([str(elem) for elem in temp_name])
                # to here ---------------------------------------------------
                # and replace argument in line below with other line (commented out)
                SearchParams.abrv_filenames.append(temp_name_to_str)
                # SearchParams.abrv_filenames.append(App.msalign_filearray[i])

                # i think current process outputs each file's name? uncomment below to see
                # print(App.msalign_filearray[i] == temp_name_to_str)
                # this is why I want to rewrite this function but I have something wrong

            # timing end
            total_time = timeit.default_timer() - start_time
            print('FileSelection \t populate_entries \t\t', total_time)
            with open("timing_0_populate_entries_blah.csv", "a") as out_file:
                out_file.write(str(total_time))
                out_file.write("\n")

            # When done processing input files, show 'Search Parameters' page
            self.controller.show_frame(SearchParams)


"""
SEARCH PARAMS
Clicking "Search Parameters" on the 'Start Page' leads to the
'Search Parameters' page, which defaults to static mode, where the user
can specify the values of 6 parameters. This page has a button which initially
displays "Static", but if you click on it you can change it to "Dynamic",
which allows the user to search by mass range. 
"""
class SearchParams(tk.Frame):
    abrv_filenames = []             # abbreviate filenames for display purposes
    entries = []                    # actual entries (to ?) 
    dynamic_entries = []            # ('file name1', ('start ret time1', entry1),('end ret time1, entry1'),'file name2',...)
    dynamic_counter = 1             # this will be used for file-specific search conditions (e.g., retention times)

    def __init__(self, parent, controller):
        # Search Parameters Page creation & initialization
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Search Parameters", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        # Mass Range Entry
        self.entry_frame = tk.Frame(self)
        self.entry_frame.grid(row=3, column = 0)
        self.mass_range = IntVar()

        # Search Modes: Static, Dynamic
        option_list = ['Static','Dynamic']
        self.search_optn = StringVar(self)          # search_optn changes mode
        self.search_optn.set('Static')              # default is Static
        self.popupMenu = OptionMenu(self, self.search_optn, *option_list)
        # menu label
        label2 = tk.Label(self, text="Search Mode:")
        label2.grid(row = 0, column = 1)
        self.popupMenu.grid(row = 0, column =2)
        self.search_optn.trace('w',self.get_parameters)

        # Pre-populate search options w/(default static) parameters
        self.controller = controller
        self.get_parameters(self)

        # 'Process Files' Button calls process_msalign_files()
        processbutton = tk.Button(self, text='Process File(s)', name='pbutton',  fg="green", command=(lambda : self.process_msalign_files()))
        processbutton.grid(column=0, row=2, sticky='w')

        # Set up for progress()
        self.e=StringVar()
        self.e.set("Loading")


    # GET_PARAMETERS(): displays approriate parameters for user entry (in static vs dynamic mode,
    # search by mass range vs. simple massses input).
    ''' timing note: get_parameters and change_range have too much user input for me to time '''
    def get_parameters(self,*args):
        SearchParams.entries = []               # search parameter entries in Static Mode
        SearchParams.dynamic_entries = []       # search parameter entries in Dynamic Mode

        # CHANGE_RANGE(): allows a user to search normally or by mass range in Dynamic Mode. in the default
        # mode, users can only enter a list of masses, but checking 'Search by mass range' also allows the
        # user to specify the min, max, and interval of the masses they want to analyze.
        def change_range(self,*args):
            print('mass_range get',self.mass_range.get())   # for testing?
            # In Dynamic Mode, user has the option to "Search by mass range"
            if self.mass_range.get() == 1:      # if "Search by mass range" selected, allow additional input
                self.mass_field.config(text = 'Mass range (min, max, interval): ')
                self.mass_max.grid(row=3, column=2,sticky='news')
                self.mass_interval.grid(row=3, column=3,sticky='news')
            if self.mass_range.get() == 0:      # if "Search by mass range" not selected, only take masses
                self.mass_max.grid_forget()
                self.mass_interval.grid_forget()
                self.mass_field.config(text = 'Masses: ')

        # In Static Mode, create buttons and entry boxes
        if self.search_optn.get() == "Static":
            for child in self.entry_frame.winfo_children():
                child.destroy()
            self.mass_range.set(0)

            self.entry_frame = tk.Frame(self)
            self.entry_frame.grid(row=3, column = 0, sticky='w')

            # s_fields are input fields in Static Mode
            s_fields = ('Start scan', 'End scan', 'Start ret. time', 'End ret. time', 'Masses','Mass Tolerance (Da)')
            i=3  #start grid at row 3

            # for each entry in Static Mode, enter the field name and entry as a pair into SearchParams.entries
            for field in s_fields:
                lab = tk.Label(self.entry_frame, width=20, text=field, anchor='w')
                ent = tk.Entry(self.entry_frame, width=8)
                lab.grid(row=i, column=0,sticky='news')
                ent.grid(row=i, column=1,sticky='w')
                SearchParams.entries.append((field, ent))
                i+=1

            """ CHANGEABLE PARAMETERS HERE: H3, H2A """
            # pre-set parameters / can be changed by user
            # H4 [11318,11332,11346,11360,11374,11388,11402,11416,11430,11444,11458,11472,11486,11500,11514,11528,11542,11556]
            # H4ox [11334, 11348, 11362,11376,11390,11404,11418,11432,11446,11460,11474,11488,11502,11516,11530,11544,11558]
            H3 = [15168,15182,15196,15210,15224,15238,15252,15266,15280,15294,15308,15322,15336,15350,15364,15378,15392,15406,15430,15444,15458,15472,15486,15500]
            H2A = [13488,13530,13572,13545,13587,13629,13700,13742,13784,13713,13755,13797]

            SearchParams.entries[0][1].insert(0,1)     # Start scan
            SearchParams.entries[1][1].insert(0,11111) # End scan
            SearchParams.entries[2][1].insert(0,1)     # Start ret. time
            SearchParams.entries[3][1].insert(0,11111) # End ret. time
            SearchParams.entries[4][1].insert(0,H3)    # Masses
            SearchParams.entries[5][1].insert(0,2)     # Mass Tolerance (Da)

        # In Dynamic Mode, create buttons and entry boxes
        if self.search_optn.get() == "Dynamic":         # in dynamic mode
            for child in self.entry_frame.winfo_children():         # again possibly to destroy static mode stuff while dynamic?
                child.destroy()
            self.mass_range.set(0)                      # automatically sets default "search by mass range" off?

            self.entry_frame = tk.Frame(self)           # populates frame with dynamic mode input
            self.entry_frame.grid(row=3, column = 0, sticky='w')

            s_fields = ('Mass Tolerance (Da)',)
            d_fields = ('Start ret. time', 'End ret. time')

            # Search by mass range button
            self.mass_range_btn = tk.Checkbutton(self.entry_frame, text="Search by mass range: ", variable=self.mass_range, command=(lambda : change_range(self)))
            self.mass_range_btn.grid(row=0,column=3, columnspan=2, sticky='news')

            # fixed 'Masses' to index 0 of entries. the entry will either serve as a mass list OR the min mass   # entries=['Masses', ...]?
            # for dynamic searching                                                                              # TODO how does this work?
            self.mass_field = tk.Label(self.entry_frame, width=20, text='Masses', anchor='w')
            self.mass_field_ent = tk.Entry(self.entry_frame, width=8)
            self.mass_field.grid(row=3, column=0,sticky='news')
            self.mass_field_ent.grid(row=3, column=1,sticky='w')
            self.mass_max = tk.Entry(self.entry_frame, width=8) #make entry, but don't show until needed
            self.mass_interval = tk.Entry(self.entry_frame, width=8) #make entry, but don't show until needed
            SearchParams.entries.append(('Masses',self.mass_field_ent,self.mass_max,self.mass_interval))

            i=4 #start grid at row 3

            # masses will be at row 3 (label at column 0, entry at column 1)             # unsure of what's happening here
            for field in s_fields:
                lab = tk.Label(self.entry_frame, width=20, text=field, anchor='w')
                ent = tk.Entry(self.entry_frame, width=8)
                lab.grid(row=i, column=0,sticky='news')
                ent.grid(row=i, column=1,sticky='w')
                SearchParams.entries.append((field, ent))
                i+=1

            for files in SearchParams.abrv_filenames:
                lab = tk.Label(self.entry_frame, width=20, text=str(files), anchor='w')
                lab.grid(row=i, column=0,columnspan=3,sticky='news')
                SearchParams.dynamic_entries.append(files)
                j=2
                for field in d_fields:
                    lab = tk.Label(self.entry_frame, width=20, text=field, anchor='w')
                    ent = tk.Entry(self.entry_frame, width=8)
                    lab.grid(row=i, column=j, columnspan=1, sticky='news')
                    ent.grid(row=i, column=j+1, sticky='w')
                    SearchParams.dynamic_entries.append((field, ent))
                    j+=2
                i+=1


    # PROCESS_MSALIGN_FILES(): checks for potential errors (no files, empty search params) before
    # processing (and tracking progress on) input files according to user-given search parameters.
    def process_msalign_files(self):
        # timing start
        start_time = timeit.default_timer()
                
        # Start assuming no Error
        error = False
        
        # Check for potential Errors
        # No files were uploaded (nothing to process)
        if len(App.msalign_filearray) == 0:
            mb.showerror("Warning","There are no files to process.")
        # Static Mode: some search parameter field(s) not filled out
        if self.search_optn.get() == "Static":
            for field in SearchParams.entries:
                if len(field[1].get()) == 0:
                    mb.showerror("Warning", "All search parameter fields must be filled out.")
                    error = True
                    break
        # Dynamic Mode: some search parameter field(s) not filled out
        if self.search_optn.get() == "Dynamic":
            # in main entries (default masses search)
            for field in SearchParams.entries:
                if len(field[1].get()) == 0:
                    mb.showerror("Warning", "All search parameter fields must be filled out.")
                    error = True
                    break
            # in dynamic entries (search by mass range)
            for field in range(len(SearchParams.dynamic_entries)):
                if len(SearchParams.dynamic_entries[field]) == 2:
                    if len(SearchParams.dynamic_entries[field][1].get()) == 0:
                        mb.showerror("Warning", "All search parameter fields must be filled out.")
                        error = True
                        break

        # If there are files to process & no errors, process msalign files according to search params
        if len(App.msalign_filearray) > 0 and error == False:
            # create loading box
            self.loading = tk.Label(self, textvariable=self.e)
            self.loading.grid(column=0, row=2, columnspan=1, sticky="w")
            # for i=1...# of input files, update progress then process ith file
            for i in range(1,len(App.msalign_filearray),2):
                self.update_progress((i/len(App.msalign_filearray)))
                SearchParams.process(self,App.msalign_filearray[i])
            # When all the calculations are complete, destroy loading page & move to Output page
            self.loading.destroy()
            self.controller.show_frame(QuantOutput)

        # timing end
        total_time = timeit.default_timer() - start_time
        # output timing data to diff files to see static vs. dynamic performance
        if self.search_optn.get() == "Static":
            print('SearchParams \t process_static_msalign_files \t', total_time)
            with open("timing_0_process_static_msalign_files_blah.csv", "a") as out_file:
                out_file.write(str(total_time))
                out_file.write("\n")
        if self.search_optn.get() == "Dynamic":
            print('SearchParams \t process_dynamic_msalign_files \t', total_time)
            with open("timing_0_process_static_dynamic_files_blah.csv", "a") as out_file:
                out_file.write(str(total_time))
                out_file.write("\n")

        
    # UPDATE_PROGRESS(): updates progress as msalign files are being processed.
    # called for each input file alongside process() in process_msalign_files().
    # this fn updates the progress bar and sends a message in case of error.
    def update_progress(self,progress):
        # timing start
        start_time = timeit.default_timer()
        
        barLength = 15                  # modify this to change the length of the progress bar
        status = ""
        # convert to float if progress is int (should be under our control, TO DO check)
        if isinstance(progress, int):
            progress = float(progress)
        # error if progress not float
        if not isinstance(progress, float):
            progress = 0
            status = "error: progress var must be float\r\n"
        # error if progress negative
        if progress < 0:
            progress = 0
            status = "Halt...\r\n"
        # done if progress = 1
        if progress >= 1:
            progress = 1
            status = "Done...\r\n"
        block = int(round(barLength*progress))
        progresstext = "\rLoading (%): [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), int(progress*100), status)
        self.e.set(progresstext)
        #sys.stdout.write(progresstext)

        # timing end
        total_time = timeit.default_timer() - start_time
        print('SearchParams \t update_progress \t\t', total_time)
        with open("timing_0_update_progress_blah.csv", "a") as out_file:
            out_file.write(str(total_time))
            out_file.write("\n")


    ''' WIP PANDAS IMPLEMENTATION IN THIS FUNCTION
    Note: This has been a really slow process because I can't test this function 
    independently, so unless I get it working exactly perfectly with output in the
    exact right format, the code breaks down in concurrent & later processes, making
    it hard to tell what's happening here '''
    # PROCESS(): processes an msalign file, preparing its data to be used in calculations.
    # called for each input file alongside update_progress() in process_msalign_files().
    # An example msalign file looks like this:
        # BEGIN IONS
        # ID=5
        # SCANS=5
        # RETENTION_TIME=13.20
        # ACTIVATION=
        # 3003.671375 165210.66
        # END IONS
        #
        # (repeat)
    def process(self,filename):
        # timing start
        start_time = timeit.default_timer()
        
        # For each scan, the format is [ID,SCANS,RETENTION_TIME,[ARRAY OF MS1 IONS]]
        # The array of MS1 ions is [Mass,Intensity,Charge]
        global scan_ions # for now, leave global, but this will be a passed array eventually
        scan_ions = []
        temp_array = [0,0,0,0]  # temp array for each scan
        ms1_ions = []           # last in scan array
        ms1events = 0           # times actual data is encountered (counts each digit)
        convert = []            # file data fills here as it is being converted
        lines = []              # lines/rows of data fill here until pandas switch works

        # RMV_CHARS(): takes a string and returns a string of only the numbers and .'s,
        # called on lines gathered from input files to filter out headings/labels
        # while gathering data for calculations (e.g. RETENTION_TIME=13.20 -> 13.20)
        def rmv_chars(string):
            getVals = list([val for val in string
                if (val.isnumeric() or val==".")])
            return "".join(getVals)

        # Open file
        with open(filename) as fp:
            data = fp.read()                        # reads whole file as massive string
        ''' USE PANDAS to open file (reads csv file row by row)
        should only require the line below '''
        #df = pd.read_csv(filename)

        # Separate file data by line (append to lines array)
        # currently we go thru each char in file, remove commas, newlines, and spaces
        # and append to lines every time one of these chars is encountered (because
        # usually new types of data come after newlines and commas).
        for i in data:
            if i == ',' or i == '\n':
                link = "".join(convert)
                link.strip()
                if len(link) > 1:
                    lines.append(link)
                    convert = []
            else:
                convert.append(i)
        ''' PANDAS automatically sorts data by rows, so no need to replace above when
        implementation is complete - can just delete above and move to next block '''

        # Extract data (decimal numbers) from lines using rmv_chars()
        # switch to pandas means we will no longer be parsing through this
        # as a string, so this will change, but make sure you understand the
        # general structure first.
        while (len(lines)-1)>0:
            text = str(lines[0])
            if text.startswith('ID='):
                temp_array[0] = int(rmv_chars(text))
                self.update()
            elif text.startswith('SCANS='):
                temp_array[1] = int(rmv_chars(text))
            elif text.startswith('RETENTION_TIME='):
                temp_array[2] = float(rmv_chars(text))
            elif text[0].isdigit():
                while lines[0]!='END IONS':
                    ms1_ions = np.append(ms1_ions,[float(s) for s in lines[0].split("\t")])
                    del lines[0]
                ms1_ions = np.reshape(ms1_ions,(int(len(ms1_ions)/3),3))
                temp_array[3] = ms1_ions
                scan_ions.append(temp_array)
                temp_array = [0,0,0,0]
                ms1_ions = []
                ms1events+=1
            del lines[0]
        ''' USE PANDAS to remove unnecessary chars (keep data only)
        each line of data from the input files is in a separate row, in
        the second column (the first column numbers the rows 0,1,2...).
        to read and edit this data using pandas, it seems like we need
        headers, but we don't have them... '''
        #for index, row in df.iterrows():
            # almost same loop as above goes here, but remove references to lines
            # for testing: to print the second column using df.iterrws()?
            #print(index, row['BEGIN IONS'])     # no header bc format is diff

        # for testing: to print the first block (up to END IONS) with pandas
        #print(df.iloc[0:6])
            
        # at this point, scan_ions should be the same as before implementing pandas,
        # so we shouldn't necessarily have to change anything in mass_selection(),
        # but we may want to reformat the scan_ions array for efficiency if possible.

        ''' TEMPORARILY have scan_ions empty while messing with pandas
        removes some of the errors I'm getting while working on this'''
        #scan_ions = []
        
        # IMPORTANT! Final format of the np array (scan_ions?):
            # For each scan, the format is [ID, SCANS, RETENTION_TIME, ARRAY OF MS1 IONS]
            # where ARRAY OF MS1 IONS = [Mass, Intensity, Charge]
        # forced pass, will change later to be user-controlled
        SearchParams.mass_selection(self,scan_ions)

        # timing end
        total_time = timeit.default_timer() - start_time
        print('SearchParams \t process \t\t\t', total_time)
        with open("timing_0_progress_blah.csv", "a") as out_file:
            out_file.write(str(total_time))
            out_file.write("\n")


        # TESTING remove later (hoping this will end here)
        #
        
        
    # MASS_SELECTION(): given scan_ions array from process(), where
    # scan_ions = [[[ID, SCANS, RETENTION_TIME, [Mass, Intensity, Charge]]],...],
        # gathers parameter data from user input
        # converts all mass data (idx, val) from string to float
        # forms found_masses, masses, tolerance arrays from mass data & parameters
    def mass_selection(self,scan_ions):
        # timing start
        start_time = timeit.default_timer()

        masses = []
        input_masses = [0]

        # Gather entries from parameters in Static Mode
        if self.search_optn.get() == "Static":
            scan_min = float(SearchParams.entries[0][1].get())          # Start Scan
            scan_max = float(SearchParams.entries[1][1].get())          # End Scan
            retention_min = float(SearchParams.entries[2][1].get())     # Start Ret. Time
            retention_max = float(SearchParams.entries[3][1].get())     # End Ret. Time
            input_masses = str(SearchParams.entries[4][1].get())        # Masses
            mass_tolerance = float(SearchParams.entries[5][1].get())    # Mass Tolerance (Da)

        # Gather entries from parameters in Dynamic Mode
        if self.search_optn.get() == "Dynamic":
            scan_min = 0                                                # default to ret time min?
            scan_max = 30000                                            # default to ret time max?
            retention_min = float((SearchParams.dynamic_entries[SearchParams.dynamic_counter][1]).get())
            retention_max = float((SearchParams.dynamic_entries[SearchParams.dynamic_counter+1][1]).get())
            SearchParams.dynamic_counter+=3
            if self.mass_range.get() == 1:                              # gather 'Search by masses' data
                min_mass = float(SearchParams.entries[0][1].get())
                max_mass = float(SearchParams.entries[0][2].get())
                mass_interval = float(SearchParams.entries[0][3].get())
                mass_tolerance = float(SearchParams.entries[1][1].get())
                masses = [min_mass]

                temp_mass = min_mass
                while temp_mass <= max_mass:
                    temp_mass+=mass_interval
                    masses.append(temp_mass)
                print('mass range=',masses)
            else:                                                       # 'Search by masses' not selected
                input_masses = str(SearchParams.entries[0][1].get())    # only additional data to gather is
                mass_tolerance = float(SearchParams.entries[1][1].get())    # Masses and Mass tolerance (Da)


        found_masses = []
        graph_found_masses = []         # this array will pass on 0 intensity values for QC graphs
        convert = []
        pool = []

        # convert string masses to float so their data can be used in calculations
        if type(input_masses[0]) == str:
            masses = []
            for idx, val in enumerate(input_masses):
                if val == ',' or val == ' ':
                    link = "".join(convert)
                    pool.append(link)
                    convert = []
                elif idx == (len(input_masses)-1) and input_masses[idx].isnumeric():
                    convert.append(input_masses[idx])
                    link = "".join(convert)
                    pool.append(link)
                else:
                    convert.append(val)

            for i in pool:
                masses.append(float(i))

        # Search through scan_ion array using parameters above and output array
        # [retention time, mass, intensity] for each mass in the array.
        for i in scan_ions:
            if scan_min <= (i[1]) <= scan_max and retention_min <= (i[2]) <= retention_max:
                for l in i[3]:
                    temp_array = []
                    graph_temp_array = []
                    for mass in masses:
                        if (mass - mass_tolerance) <= l[0] <= (mass + mass_tolerance):
                            temp_array.extend((i[2],l[0],l[1]))
                            found_masses.append(temp_array)
                            graph_temp_array.extend((i[2],l[0],l[1]))
                            graph_found_masses.append(graph_temp_array)
                if len(graph_temp_array) == 0:
                    for mass in masses:
                        graph_found_masses.append(([i[2],mass,0]))

        # Perform mass quantification on found masses
        SearchParams.mass_quantification(self,found_masses, masses, mass_tolerance)

        # Build qc graph result from found masses, masses, and mass tolerance arrays
        # and append this to total_qc_graph_array.
        QCGraphs.graph_found_masses, QCGraphs.masses, QCGraphs.mass_tolerance = graph_found_masses, masses, mass_tolerance
        qc_graph_result = [graph_found_masses, masses, mass_tolerance]              # qc_graph_result = [graph_found_masses, masses, mass tolerance]
        QCGraphs.total_qc_graph_array.append(qc_graph_result)                       # QCGraphs.total_qc_graph_array[0][2] = qc_graph_result?

        # timing end
        total_time = timeit.default_timer() - start_time
        print('SearchParams \t mass_selection \t\t', total_time)
        with open("timing_0_mass_selection_blah.csv", "a") as out_file:
            out_file.write(str(total_time))
            out_file.write("\n")


    # MASS_QUANTIFICATION(): Given found_masses, masses, and mass_tolerance arrays
    # from mass_selection(), calculates intensities of masses and appends these
    # values to summed_intensities array. These are used to calculate total_intensity,
    # which is used alongside summed_intesities to calculate percent_intesities,
    # which contains the ratio of the individual intensities of the masses to the
    # total intensity.
    def mass_quantification(self,found_masses,masses, mass_tolerance):
        # timing start
        start_time = timeit.default_timer()

        # Start with empty intensity arrays (summed, percent) and 0 total intensity
        summed_intensities = []
        total_intensity = 0
        percent_intensities = []

        # For each mass found, determine its intensity based on avgs
        for i in masses:
            intensity = 0
            for j in found_masses:
                if (j[1] - mass_tolerance) <= i <= (j[1] + mass_tolerance):
                    intensity = intensity + j[2]
            summed_intensities.append([i,intensity])

        # Total intensity is sum of all summed_intensities
        for i in summed_intensities:
            total_intensity = total_intensity + i[1]

        # If total_intensity > 0 we can calculate ratio of individual summed
        # intensities to total_intensity calculated above. Append these values
        # to percent_intensities.
        if total_intensity > 0:
            for i in summed_intensities:
                percent_intensities.append([i[0],(i[1]/total_intensity*100)])

            App.processed_filearray.append(percent_intensities) #((mass1,percent1),(mass2,percent2),...)
        # If total_intensity nonpositive, cannot calculate percentages (div by 0 or meaningless if -).
        else:
            mb.showerror("Warning","No masses found for one or more of the inputted files.")
            self.controller.show_frame(SearchParams)

        # timing end
        total_time = timeit.default_timer() - start_time
        print('SearchParams \t mass_quantification \t\t', total_time)
        with open("timing_0_mass_quantification_blah.csv", "a") as out_file:
            out_file.write(str(total_time))
            out_file.write("\n")


"""
QUANT OUTPUT
Takes calculated data from SearchParams to form output graphs & csv files.
"""
class QuantOutput(tk.Frame):
    averaged_data = [] #[[averages],[stdev]]

    def __init__(self, parent, controller):                                 # creating buttons for quant output: output, calc data, search params
        # Quant Output Page creation & initialization
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Results Output", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        # Calculate Avg & Std Dev Button
        button1 = tk.Button(self, text="Calculate Avg and Stdev", fg='green',
                            command=lambda: self.analyze_data())
        button1.grid(column=0, row=1, sticky='w')

        # Search Parameters Button
        button2 = ttk.Button(self, text="Search Parameters",
                            command=lambda: controller.show_frame(SearchParams))
        button2.grid(column=1, row=1, sticky='w')

        self.controller = controller


    # ANALYZE_DATA(): given data in processed_filearray and expgroup, groups data
    # then calculates avg and std deviation. this data is appended to the arrays
    # grouped_data and calc_avg_stdev, the latter of which is passed to QC Graphs
    # (to form error bars?).
    def analyze_data(self):
        # timing start
        start_time = timeit.default_timer()

        # arrays we are filling in this function
        restructured_data = []
        grouped_data = []
        calc_avg_stdev = []
        temp_array = []
        # arrays that contain the data to be used in calculations
        processed_filearray_temp = App.processed_filearray
        expgroup_temp = App.expgroup

        # restructure data into a new array [[group1, [data1]], [group2, [data2]],...]
        # where [data] is [mass, intensity]
        if len(expgroup_temp) == 0 or len(processed_filearray_temp) == 0:
            mb.showerror("Warning","No masses found for one or more of the inputted files.")
            self.controller.show_frame(SearchParams)
        else:
            for i in range(len(expgroup_temp)):
                temp_array = [expgroup_temp[i],processed_filearray_temp[i]]
                restructured_data.append(temp_array)

        # sort data based on group name
        # [[group1, [data1]], [group1, [data2]], [[group2],[data1]],...]
        restructured_data = sorted(restructured_data, key=lambda x: x[0])
        while len(restructured_data) != 0:
            if len(restructured_data) == 1:
                grouped_data.append(restructured_data[0][1])
                calc_avg_stdev.append(([restructured_data[0][0],(self.calculate_avg_stdev(grouped_data))]))
                del restructured_data[0]
            elif restructured_data[0][0] == restructured_data[1][0]:
                grouped_data.append(restructured_data[1][1])
                del restructured_data[1]
            else:
                grouped_data.append(restructured_data[0][1])
                calc_avg_stdev.append(([restructured_data[0][0],(self.calculate_avg_stdev(grouped_data))]))
                del restructured_data[0]
                grouped_data =[]

        # the final product [[group1, [avg,stdev]],[group2, [avg,stdev],...]
        # will be sent to the same variable in the QCGraphs for graph creation
        QCGraphs.calc_avg_stdev = calc_avg_stdev
        self.output_quantification_file()
        self.controller.show_frame(QCGraphs)

        # timing end
        total_time = timeit.default_timer() - start_time
        print('QuantOutput \t analyze_data \t\t\t', total_time)
        with open("timing_0_analyze_data_blah.csv", "a") as out_file:
            out_file.write(str(total_time))
            out_file.write("\n")


    # CALCULATE_AVG_STDEV(): calculates average and standard deviation of grouped data
    # in analyze_data() above. this is called for each subarray in grouped_data.
    def calculate_avg_stdev(self,grouped_data):
        # timing start
        start_time = timeit.default_timer()

        # fill these arrays with calculated values
        averaged_values = []
        stdev_values = []
        mass_array = []

        # for each user-defined search mass, create an array of
        # all data for that single mass, append to mass_array
        for mass in QCGraphs.total_qc_graph_array[0][1]:
            temp_array = []
            temp_array.append(mass)
            for i in grouped_data:
                for j in i:
                    if j[0] == mass:
                        temp_array.append(j[1])
            mass_array.append(temp_array)
        #print('mass array',mass_array)

        # use statistics to calculate std dev and mean of full subarrays
        for i in mass_array:
            stdev_values.append(statistics.pstdev(i[1:]))
            averaged_values.append(statistics.mean(i[1:]))
            
        # timing end
        total_time = timeit.default_timer() - start_time
        print('QuantOutput \t analyze_data \t\t\t', total_time)
        with open("timing_0_analyze_data_blah", "a") as out_file:
            out_file.write(str(total_time))
            out_file.write("\n")

        # return array with avg & std dev vals for all masses
        calculated_group_data = [averaged_values,stdev_values]
        return calculated_group_data


    # OUTPUT_QUANTIFICATION_FILE(): 
    def output_quantification_file(self):
        # timing start
        start_time = timeit.default_timer()

        # qc graphs will be named by date (up to second)
        date = datetime.today().strftime('%Y%m%d_%H%M%S')   # calculate exact time/date
        filenames = []
        a = []

        # check if any files were uploaded (if not, Error generating output)
        if (len(App.processed_filearray)) == 0:
            mb.showerror("Warning", "Based on your search criteria, no results were generated.")
        else:
            # name output files by date, calculated above
            # output data (SearchParams.abrv_filenames, App.processed_filearray) to file
            filename = "MS1_quantification"+"_"+date+".csv"
            with open(filename,"a") as out_file:
                for i in range(len(SearchParams.abrv_filenames)):
                    out_file.write(str(SearchParams.abrv_filenames[i])+"\n")
                    for j in App.processed_filearray[i]:
                        x,y = str(j[0]),str(j[1])
                        temp = (x+','+y+',')
                        out_file.write(temp)
                    out_file.write(" \n")

        # timing end
            total_time = timeit.default_timer() - start_time
            print('QuantOutput \t output_quantification_file \t', total_time)
            with open("timing_0_output_quantification_file_blah.csv", "a") as out_file:
                out_file.write(str(total_time))
                out_file.write("\n")


"""
QUALITY CONTROL GRAPHS
This class contains the actual QC graphs so its only function is makegraph().
"""
class QCGraphs(tk.Frame):
    total_qc_graph_array = []   #([[graph_found_masses, masses, mass_tolerance],...])
    calc_avg_stdev = []         # array of calculated averages & std deviations

    def __init__(self, parent, controller):
        # QC Graphs Page creation & initialization
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Results with quality control graphs", font=LARGE_FONT)
        label.grid(column=0, row=0, sticky='w')

        # Show QC Graphs Button
        button1 = tk.Button(self, text="Show QC Graphs", fg ='green',
                            command=lambda: self.makegraph())
        button1.grid(column=0, row=1, sticky='w')

        # Search Parameters Button
        button2 = ttk.Button(self, text="Search Parameters",
                            command=lambda: controller.show_frame(SearchParams))
        button2.grid(column=1, row=1, sticky='w')

        # New Analysis Button
        button3 = tk.Button(self, text="New Analysis",
                            command=lambda: controller.new_analysis())
        button3.grid(column=2, row=1, sticky='w')


    # MAKEGRAPH(): uses data from calculations above to form QC Graphs,
    # displayed in browser (will change to display in App later).
    def makegraph(self):
        # timing start
        start_time = timeit.default_timer()

        # max number of graphs is total number of input files
        # plus one for main graph w data averaged across conditions
        max_graphs = len(QCGraphs.total_qc_graph_array[0][1])
        qc_plots = []
        group_plots = []
        str_mass_names = []

        # change font size for QC graphs depending on number of masses
        if max_graphs < 7:
            graph_font_size = '16px'
            glyph_size = 20
        elif 8 <= max_graphs <= 12:
            graph_font_size = '12px'
            glyph_size = 10
        elif max_graphs > 13:
            graph_font_size = '10px'
            glyph_size = 6
        else:
            graph_font_size = '12px'
            glyph_size = 20

        # data is organized in chart by mass, abundance, and condition
        TOOLTIPS = [("Mass: ", "@x"),("Abundance (%): ", "@top"),("Condition: ", "@desc"),]
        TOOLTIPSQC = [("index", "$index"),("(x,y)", "($x, $y)"),("desc", "@desc"),]

        # averaged plot displayed first
        averaged_plot = figure(title="Averaged MS1 Data per Condition", x_axis_label="Mass", y_axis_label="Abundance (%)", tools="pan,box_zoom,wheel_zoom,reset,undo,save", active_drag="box_zoom",
                               active_scroll="wheel_zoom", x_range=((min(QCGraphs.masses)-100), (max(QCGraphs.masses)+100)),tooltips=TOOLTIPS, width=1080, height=740)

        # convert searched masses to string values for legend
        for i in QCGraphs.masses:
            str_mass_names.append(str(i))

        # color selection variable used to change color AND
        # serves as the off-set for grouped data bar graphs
        color_selection = 0
        offset = 0.25
        for group_data in QCGraphs.calc_avg_stdev:
            group_name = []
            #adding stdev to avgs to get bar placement on graph (TO DO fix)
            lower, upper = [], []
            for i in range(len(group_data[1][0])): #average values
                lower.append(group_data[1][0][i]-group_data[1][1][i]) #average value for a mass i - stdev
                upper.append(group_data[1][0][i]+group_data[1][1][i]) #average value for a mass i + stdev
                group_name.append(group_data[0])

            color_palette = Category20c[20]                             # color palette 
            if color_selection == 19:                                   # once all colors used, reset & cycle back
                color_palette = Category20b[20]
                color_selection = 0

            data = {"x": QCGraphs.masses,
                    "lower": lower,                                     # can we just do this in a for loop
                    "upper": upper,                                     # with the calculations in the for loop above
                    "top": group_data[1][0],                            # and just get rid of the lower & upper vars
                    "desc": group_name}                                 # and the for loop up there

            source = ColumnDataSource(data=data)

            averaged_plot.vbar(x=dodge("x",offset), width=2, bottom=0, top="top",source=source,
                                legend_label="Condition: "+str(group_data[0]), color=color_palette[color_selection])
            averaged_plot.add_layout(Whisker(source=source, base=dodge("x",offset), upper="upper", lower="lower"))

            color_selection+=1
            offset+=2


        for j in QCGraphs.total_qc_graph_array:                 # where j is each processed msalign file as an array
            idx = QCGraphs.total_qc_graph_array.index(j)        # used to title the graph after the cooresponding filename

            color_selection = 0
            color_palette = Category20c[20]

            p = figure(title="QC Graph for "+str(SearchParams.abrv_filenames[idx]),x_axis_label="Ret. time(s)", tools="pan,box_zoom,wheel_zoom,reset,undo,save",
                       active_scroll="wheel_zoom",y_axis_label="Intensity", tooltips=TOOLTIPSQC, active_drag="box_zoom", width=1080, height=740)
            offset = .25
            v=[]
            for i in QCGraphs.masses:                           # for each mass... is this ret time?
                ret_time = []                                   # create empty arrays for ret_time, intensity, and mass
                intensity = []
                mass = []

                if color_selection == 19:                       # if reached end of color options
                    color_palette = Category20b[20]             # reset & cycle back
                    color_selection = 0

                for k in j[0]:              # j[0] is [graph_found_masses] of msalign file j and k is [ret. time, mass, intensity]
                    if (k[1] - QCGraphs.total_qc_graph_array[0][2]) <= i <= (k[1] + QCGraphs.total_qc_graph_array[0][2]):
                        ret_time.append(k[0])                   # if ret_time - ? <= mass??
                        mass.append(k[1])
                        intensity.append(k[2])
                mass_coord = [ret_time,mass,intensity]
                mass_coord = np.array(mass_coord)

                if len(mass_coord[0]) >=1:                      # if mass_coord nonempty
                    color_selection+=1

                    data = {"x": mass_coord[0],
                            "y": mass_coord[2],
                            "desc": mass_coord[1]}

                    source = ColumnDataSource(data=data)

                    z = p.vbar(x=dodge('x',offset), width=0.25, bottom=0, top='y', color=color_palette[color_selection], source=source) #legend_label=str(i))
                    v.append(z)
                    offset+=0.25
            legend_items = [LegendItem(label=str_mass_names[i]+"Da", renderers=[r]) for i, r in enumerate(v)]
            legend = Legend(items=legend_items,label_text_font_size=graph_font_size,glyph_width=5,label_standoff=1,
                            glyph_height=glyph_size,padding=1,spacing=1,margin=5,label_text_line_height=0.1,label_height=0)
            p.add_layout(legend,'right')
            p.legend.click_policy="hide"
            qc_plots.append(p)
            del p

        date = datetime.today().strftime('%Y%m%d_%H%M%S')
        filename = "MS1_quant_graphs"+"_"+date+".html"      # names qcgraph file by date
        output_file(filename)                               # from bokeh, outputs file containing quant graphs \

        # make a grid
        grid = gridplot([[averaged_plot,None],qc_plots], merge_tools = False, toolbar_location="left", width=800, height=500)
        show(grid)

        ''' TO DO once "New Analysis" button fixed, move this there '''
        # clear out graphing data
        QCGraphs.total_qc_graph_array,QCGraphs.calc_avg_stdev,QuantOutput.averaged_data, App.processed_filearray = [],[],[],[]
        SearchParams.dynamic_counter = 1                                # need to reset counter if another search is done

        # timing end
        total_time = timeit.default_timer() - start_time
        print('QCGraphs \t makegraph \t\t\t', total_time)
        with open("timing_0_makegraph_blah.csv", "a") as out_file:
            out_file.write(str(total_time))
            out_file.write("\n")

        # QC Graph output is last step of app but don't close app, just return
        return

print('Class\t\t Function \t\t\t Runtime (s)')
print('-------\t\t ----------\t\t\t -----------')

app = App()
app.mainloop()

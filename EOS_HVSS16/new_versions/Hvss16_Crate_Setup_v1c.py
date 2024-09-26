# Import Module

from tkinter import ttk, Tk, Menu
from tkinter.ttk import Notebook 
from tkinter.filedialog import askopenfilename, asksaveasfilename
import pandas as pd
import json, os
from Hvss16_Setup_ctrl_v2f import create_widgets
from Hvss16_Setup_ctrl_v2f import Hvss16_Control

TP_MASK = 0x20
NHIT_MASK = 0x25

#fg = "BLACK"
class Hvss_App(Tk):
    def __init__(self, title, size):

        #Main setup
        super().__init__()
        self.title(title)
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(size[0], size[1])

        # Create main canvas for widgets
        Mainframe = ttk.Frame(self, height=400, width=200)#background ='green'
        Mainframe.grid(row = 1, columnspan=4,padx=10, pady=8)    
        self.notebook = ttk.Notebook(Mainframe)
         #Place widgets on the canvas
        self.layout = Hvss_Menu(self, Mainframe)
        self.setup_ctrl = Hvss16_Control(self)
        #Create Menu
        self.menu_bar = Menu(self)
        self.config(menu=self.menu_bar)
        self.file_menu = Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open_Spreadsheets", command= lambda:(self.layout.open_file()))
        self.file_menu.add_command(label ="Save As...", command = lambda:(self.layout.save_as_file(self.layout.get_data_tobe_saved()))) 
        self.file_menu.add_separator() 
        self.file_menu.add_command(label ='Refresh', command = lambda:(self.setup_ctrl.InitMcp230XX()))
        self.file_menu.add_separator() 
        self.file_menu.add_command(label ='Exit', command = self.destroy) 
        

        self.mainloop()

class Hvss_Menu(ttk.Frame):
    def __init__(self, parent, Mainframe):
        super().__init__(parent) 
        self.create_widgets=create_widgets
        self.main = Mainframe
        self.tabdata = {}

    def open_file(self):
        file_formats = [('CSV files', '*.csv'), ('JSON files', '*.json'), ('All files', '*.*')]
        filename = askopenfilename(initialdir="home/pi/EOS_HVSS16/", 
                                title="Open A File",
                                filetypes=file_formats)
        
        if filename:
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension == '.csv':
                df = pd.read_csv(filename)
            elif file_extension == '.json':
                with open(filename, 'r') as file:
                    data = json.load(file)
                    df = pd.DataFrame(data)
                #df = pd.DataFrame.from_dict(data)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
            
            self.create_widgets(df, self.main, self.tabdata)


    def save_as_file(self, dataframe):
        file_formats = [('CSV files', '*.csv'), ('JSON files', '*.json'), ('All files', '*.*')]
        filename = asksaveasfilename(defaultextension=(".json",".csv"), 
                                    initialdir="home/pi/EOS_HVSS16/", 
                                    title="Save file",
                                    filetypes=file_formats)
        
        if filename:
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension == '.csv':
                dataframe.to_csv(filename, index=False)
            elif file_extension == '.json':
                dataframe.to_json(filename, orient='records')
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
        
    def get_data_tobe_saved(self):
        DataSize = 48
        CHAN =[]
        #CHAN = list(range(DataSize))
        for index in range(DataSize):
            CHAN.append(index)
      

        # Create a dictionary to store data from each tab
        tab_data = {
            tbname: [float(spinbox.get()) for i, spinbox in enumerate(self.tabdata[tbname]) if i < 48]
            for tbname in sorted(self.tabdata.keys())
        }

         # Create a new DataFrame from the tab data dictionary with the correct row and column order
        new_df = pd.DataFrame(tab_data, index=CHAN)
        new_df = new_df[sorted(new_df.columns)]


        #print ("DF=",new_df)
        return new_df
    
    
Hvss_App('HVSS Crate Setup v1c', (610, 700))#(W,H)


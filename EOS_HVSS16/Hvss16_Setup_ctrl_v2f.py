from tkinter import ttk
import tkinter as tk
import  math, time, struct
from Adafruit_I2C import Adafruit_I2C
from Adafruit_MCP230xx import Adafruit_MCP230XX
import RPi.GPIO as GPIO

TP_MASK = 0x20
NHIT_MASK = 0x25
ADC = 0x34
ID_EEPROM = 0X50


class create_widgets:
    def __init__(self, dataframe, defaultcanvas,tabdata = None):

       
        self.notebook = ttk.Notebook(defaultcanvas)
        self.tabdata = tabdata
        self.defaultcanvas = defaultcanvas

        TabNames =  ['hvss0','hvss1','hvss2','hvss3','hvss4','hvss5','hvss6','hvss7','hvss8']
        Buttons =   ['Update','Read Baseline','Update_Tp_Mask','Update_NHIT_Mask']#,'Init_Mask']
        Frames =    ['frame0','frame1','frame2','frame3','frame4','frame5','frame6','frame7','frame8']
        ColumnNames = ['CH','Threshold Adj','WidthAdj','Test pluse Amplitude', 'TestPulse Mask', 'NHIT Mask',
                        'NHit_Baseline', 'An_Sum_Baseline','<-- An_Sum_Bal', '<-- NHit_Bal      ']
        self.ChkButtonNames =['TpClkEn0','TpClkEn1','TpClkEn2','TpClkEn3','TpClkEn4','TpClkEn5','TpClkEn6','TpClkEn7']
        self.ChkButtonVars =['TpClkVar0','TpClkVar1','TpClkVar2','TpClkVar3','TpClkVar4','TpClkVar5','TpClkVar6','TpClkVar7']
        self.ChkButtons=[]
        self.TpClkEn_default = []
        self.create_Checkbuttons()
        #***********************************************************
        #create hvss Update all button
        #***********************************************************
        UpdateAll = ttk.Button(defaultcanvas,text = 'UPDATE_ALL HVSS BOARDS SEQUENTIALLY', command = lambda:self.hvss16_Ctrl.GetNbData(All=True))
        UpdateAll.grid(row = 40,column=0, columnspan = 2, padx=6, pady=8)


        i =0
        for tabname in TabNames:

            self.Ch =[]
            AnalogData=[]
            self.tabdata[tabname] = AnalogData
            frame = Frames[i]
            #***********************************************************
            #create hvss tabs for notebook
            #***********************************************************
            frame = ttk.Frame(self.notebook,height=500, width=210)
            self.notebook.add(frame, text=tabname)
            self.notebook.grid(row = 1, columnspan=4,padx=10, pady=8)
            self.hvss16_Ctrl = Hvss16_Control(self.tabdata, tabname, AnalogData, self.notebook)

            self.hvssButtons(Buttons,frame,AnalogData)
            self.FunctionNames(ColumnNames,frame)
            self.ChanLabels(self.Ch, frame)
            self.GetDacDefault_Data(dataframe,frame,tabname,AnalogData)

            '''Place widgets on the canvas'''
            self.Insert_cols(AnalogData, 1, 2, 16)

            i+=1
        
        # Update the hvss right away 
        self.hvss16_Ctrl.GetNbData(All=True)


    def hvssButtons(self,Buttons,frame,AnalogData_List):
        '''#create hvss Update and Read ADC buttons on all tabs
        '''
        bi = 0 #button index
        cbi = 0 #check buttons

        for b in Buttons:
            buttontext = b
            if buttontext == 'Init_Mask':
                b = ttk.Button(frame,text = buttontext, command = lambda:self.hvss16_Ctrl.InitMcp230XX)
                b.grid(row = 16, column = 4, padx=6, pady=8)
            if buttontext == 'Update':
                b = ttk.Button(frame,text = buttontext, command = lambda:self.hvss16_Ctrl.GetNbData())
            elif buttontext == 'Read Baseline':
                b = ttk.Button(frame,text = buttontext, command = lambda:self.hvss16_Ctrl.GetADCValues(AnalogData_List))
            elif buttontext == 'Update_Tp_Mask':
                b = ttk.Button(frame,text = buttontext, command = lambda:self.hvss16_Ctrl.updateMask(TP_MASK))
            elif buttontext == 'Update_NHIT_Mask':
                b = ttk.Button(frame,text = buttontext, command = lambda:self.hvss16_Ctrl.updateMask(NHIT_MASK))
            b.grid(row = 20, column = bi+1, padx=6, pady=8)
            bi+=1


    def ckb(self,cb,ckvar,index):
        cb = ttk.Checkbutton(self.defaultcanvas,
            text=cb,
            command=lambda:self.hvss16_Ctrl.TestPulseClk_Enable(ckvar.get(),index),
            variable=ckvar,
            onvalue=True,
            offvalue=False
            )
        self.ChkButtons.append(cb)


    def create_Checkbuttons(self):

        TpClkVars = []
        for cb_var in self.ChkButtonVars:
            cb_var = tk.StringVar()
            TpClkVars.append(cb_var)

        i = 0
        for cbn in self.ChkButtonNames:
            self.ckb(cbn, TpClkVars[i],i)
            i+=1
        cbi = 0
        for cb in self.ChkButtons:
            if cbi in range(0,4):
                cb.grid(row = 23, column=cbi, sticky="w",padx=8,pady=4)
            if cbi in range(4,8):
                cb.grid(row = 25, column=cbi-4, sticky="w",padx=8,pady=4)

            #cb.configure(font=("Times New Roman", 10, NORMAL))
            cbi+=1

    def createRadio(self,frame,header_name,sorting_options,which_row, which_column, sort_options):
        row_pos = which_row
        for text, sort in sorting_options:
            r = ttk.Radiobutton(frame, text=text, value=sort, variable= sort_options,command = lambda:self.hvss16_Ctrl.TestPulseClk_Enable())
            row_pos = row_pos + 1
            r.grid(row = row_pos, column=which_column, sticky="w",padx=4)

        header = tk.Label(frame, text=header_name, justify='left')
        header.grid(row = row_pos-1, column = which_column-1, padx = 0,pady=1)
        header.configure(font=("Times New Roman", 12, tk.NORMAL))

    def FunctionNames(self,header_names,frame):
        '''
        #Place array of FunctionNames Label
        '''
        col = 0
        label_pos = 0
        function_Index =0
        for fname in header_names:
            #print("func_Index/labels:",function_Index, fname)
            if col >= 4:
                fname=(ttk.Label(frame, text= fname, justify='left')) #Build Text Label Array for Chan ID
                if function_Index in range(4,10):
                    if label_pos in range(5,9):
                        #print("label_pos1:",function_Index, label_pos, fname)
                        label_pos-=1
                        fname.grid(row = label_pos, column= col, padx = 6,pady=2)
                        label_pos+=3
                        #print("label_pos2:",function_Index, label_pos, fname)
                    elif label_pos in range(0,7):
                        fname.grid(row = label_pos, column= col, padx = 6,pady=2)
                        label_pos+=3
                        #print("Sum labels:",function_Index,label_pos, fname)
                    elif label_pos in range(9,24):
                        fname.grid(row = label_pos, column= col, padx = 6,pady=2)
                        label_pos+=1
                       # print("Mask labels:",function_Index,label_pos, fname)
            else:
                fname=(ttk.Label(frame,text= fname, justify='left')) #Build Text Label Array for Chan ID
                fname.grid(row = 0, column= col, padx = 6,pady=2)
                col +=1
                #print("reg labels:",function_Index,label_pos, fname)
            function_Index+=1

    def ChanLabels(self, Ch, frame):

        '''
        create arrays of Chan Labels with DAC locations on each tab
        '''
        rowe = 2
        for c in range(16):
            Ch.append(ttk.Label(frame, text= c, justify='left')) #Build Text Label Array for Chan ID
            Ch[c].grid(row = rowe+c, column= 0, padx = 6,pady=2)

    def GetDacDefault_Data(self,data,frame,tabname,AnalogData_List):
        spinbox_width = 6
        '''
        create arrays of spinbox widgets and insert DAC values from csv for each tab
        '''
        #ADC_List=[]
        #self.ADC_ReadOut=[]
        for rowe in data.axes[0]:
            AnalogData_List.append(ttk.Spinbox(frame, justify = 'left',width= spinbox_width,from_= 0, to = 5)) #Build Text Widget Array for DAC Values
            #AnalogData_List.append(tk.Text(frame, height = 1.3, width= spinbox_width+2)) #Build Text Widget Array for ADC Values #Build Text Widget Array for DAC Values
            AnalogData_List[rowe].delete(0,tk.END) # clear text box
            #AnalogData_List[rowe].delete("1.0",END) # clear text box
            AnalogData_List[rowe].insert(tk.END, data.at [rowe, tabname])#insert data into spin boxes

        '''
        ***********************************************************
        create arrays of Spinbox widgets
        to hold ADC values and Mask control for each tab
        ***********************************************************
        '''
        row = 0
        rowe = 47
        for row in range(5):
            if row in range(1,3):
                AnalogData_List.append(ttk.Spinbox(frame, justify = 'left',width= spinbox_width,from_= 0, to = 5)) #Build Text Widget Array for DAC Values
                AnalogData_List[rowe+row].delete(0,tk.END)  #clear text box
                AnalogData_List[rowe+row].insert(tk.END, 0) #insert data into spin boxes
            if row in range(3,5):
                AnalogData_List.append(ttk.Spinbox(frame, justify = 'left',width= spinbox_width)) #Build Text Widget Array for ADC Values

        '''
        ***********************************************************
        #Place widgets on the canvas
        ***********************************************************
        '''

    def Insert_cols(self,list, column = 0,row_pos=0,row_num = 16):
        self.fg='Black'
        i=0
        r = 0
        col_num= 5
        col_inc = column
        row_pos = row_pos
        adc_pos = 6
        for rowe in list:
            coltracker = (row_num + i)/row_num
            ''' MASK '''
            if i in range(48,50):
                rowe.configure(font=("Times New Roman", 12,tk.NORMAL), foreground= self.fg,increment= 1)
                #rowe.configure(font=("Times New Roman", 12,  tk.NORMAL), foreground= self.fg)
                rowe.grid(row = row_pos + r, column= col_inc, padx = 6,pady=2)
                r+=1

            #print("row/column trackers: ",row_num, coltracker,  col_inc,  i,  r)
            ''' ADC '''
            if i in range(50,52):
                #rowe.delete("1.0",tk.END) # clear text box
                #rowe.insert(tk.END, 0)
                rowe.delete(0,tk.END)  #clear text box
                rowe.insert(tk.END, 0) #insert data into spin boxes
                rowe.configure(font=("Times New Roman", 12,  tk.NORMAL), foreground= self.fg)
                rowe.grid(row = adc_pos, column= 4, padx = 8,pady=2)
                adc_pos+=2

            #''' DAC '''
            if i in range(0,48):
                rowe.configure(font=("Times New Roman", 12,tk.NORMAL), foreground= self.fg,increment= .001)
                rowe.grid(row = row_pos + r, column= col_inc, padx = 6,pady=2)
            r+=1

            if r >= row_num:
                r = 0
                col_inc +=1

            if coltracker >= col_num:
                break
            i+=1

class Hvss16_Control():
    def __init__(self,tabdata=None, tabname=None, list=None, notebook=ttk.Notebook):
        ''' Discription??'''


        '''Rpi Pin Definitons'''
        self.Rpi_hvss_gpio = [14,17,27,23,10,25,8,5,12,19,26]
        self.Rpi_TP_gpio   = [15,18,22,24, 9,11,7,6,13,16,20]
        clr   = 21 # Broadcom pin 40

        GPIO.setwarnings(False)
        # Pin Setup:
        GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
        GPIO.setup(clr, GPIO.OUT) # clr pin set as output

        [GPIO.setup(gpio_pin, GPIO.OUT) for gpio_pin in self.Rpi_hvss_gpio]  # Board_Sel pin set as output
        [GPIO.setup(gpio_pin, GPIO.OUT) for gpio_pin in self.Rpi_TP_gpio]    # Test pulse_Sel pin set as output
        [GPIO.output(gpio_pin, GPIO.LOW) for gpio_pin in self.Rpi_hvss_gpio] # Initialize crate with all Test pulse deselected
        [GPIO.output(gpio_pin, GPIO.LOW) for gpio_pin in self.Rpi_TP_gpio]   # Initialize crate with all boards deselected
      
        GPIO.output(clr, GPIO.HIGH)

        self.notebook = notebook
        self.tabdata = tabdata
        self.tabdata[tabname] = list

        self.DACAddress=[0x48,0x49,0x4A,0x4B,0x4C,0x4D]
        self.DAC=[]
        if tabname!= None:
            self.Board_select(tabname, mode=1)
            print("Initialize",tabname)
            self.mcp1 = Adafruit_MCP230XX(address = TP_MASK, num_gpios = 16) # MCP23016
            self.mcp2 = Adafruit_MCP230XX(address = NHIT_MASK, num_gpios = 16)
            self.adc  = Adafruit_I2C(address = ADC, debug=True)
            [self.DAC.append(Adafruit_I2C(address = a, debug=True)) for a in self.DACAddress]
            self.id = Adafruit_I2C(address = ID_EEPROM, debug=True)
        self.fg='Black'

    def updateDAC(self, datalist,board_id):
        ''' Discription??'''
        index=0
        i = 0
        vref = 3.3  #DAC voltage reference
        bits = 10   #DAC resolution
        DACdataOut = [0,0] #cache for i2c block data transfer out
        DACdataIn  = [0,0] #cache for i2c block data transfer in
        old_dacIndex = 0

        for index in range(len(datalist)-4):
            #Pull data from spinbox[index]
            data = (float(datalist[index]))
            #convert data to DAC value
            cvrtdata = self.ConvDacValue(bits,vref,data)
            print("HEX:",datalist[index],index)

            #shift Integer value to the left 6 times to satisfy DAC requirements
            cvrtdata = cvrtdata<<6
            #**************TBD***********************
            #Only update values that have been changed
            #if Converted_data != actual_data[index]:
            #****************************************
            dacIndex = self.dacIndex(index)
            #********************************************
            #Six channels per Dac Address
            if dacIndex != old_dacIndex:
                i = 0
                old_dacIndex= dacIndex

            #Command and Access Byte
            WCA = 0x30+i #DAC register write command
            RCA = 0x00+i #DAC register read command
            #********************************************

            #split into 2 bytes then add to DACdata list
            DACdataOut[0] = cvrtdata>>8  # The value of x shifted 8 bits to the right, creating upper byte
            DACdataOut[1] = cvrtdata % 256 # The remainder of x / 256, creating lower byte.
  
            #write data to DAC
            self.Board_select(board_id)
            self.DacWrite(WCA,DACdataOut,dacIndex)
            #Read back Dac registers
            DACdataIn = self.DacRead(RCA, dacIndex)

            print("DAC_Data I/O:",cvrtdata, DACdataOut,DACdataIn, dacIndex, board_id)
            i+=1

    def dacIndex(self,index):
        dac_cnt = 6
        i = (48-index)/8
        dac_index = int(dac_cnt- i)
        print("Dac Index =:", dac_index)
        return  dac_index

    def DacWrite(self,cmd,list,index = 0):
        self.DAC[index].writeList(cmd,list)
        print("DAC",index,cmd,list)
        time.sleep(0.01)

    def DacRead(self,cmd, index = 0):
        Dataword=[0,0]
        self.DAC[index].write8(cmd, 0)
        Dataword = self.DAC[index].readList(cmd,2)
        #time.sleep(0.2)
        return Dataword

    def ConvDacValue(self, bits,vref,volts):
        ''' Discription??'''
        resolution = vref/(math.pow(2,bits))
        DACvalue = (round(volts/resolution))
        return DACvalue

    def ConvAdcValue(self,bits,vref,hexvalue):
        ''' Discription??'''
        resolution = vref/(math.pow(2,bits))
        volts = float(hexvalue*resolution)
        return volts

    def updateAdcValues(self,AnalogData_List,value,index):
        ''' Discription??'''
        AnalogData_List[index+50].delete(0,tk.END) # clear text box
        AnalogData_List[index+50].insert(tk.END, value)
        AnalogData_List[index+50].configure(font=("Times New Roman", 12,tk.NORMAL),state ='disabled', foreground= self.fg)

    def GetADCValues(self, list):
        ''' Discription??'''
        index=0
        vref = 3.3  #ADC voltage reference
        bits = 12   #ADC resolution
        data = [0,0,0,0,0,0,0,0,0,0,0,0]


        REG_SETUP = 0x80
        REG_CONFIG = 0x07
        LENGTH =8
        self.Board_select(None)

        self.adc.write8(REG_SETUP, REG_CONFIG)
        time.sleep(0.5)

        data = self.adc.readList(REG_CONFIG, LENGTH)
        print("ADC Channels: ",data)
        i = 0
        for index in range(0,4):
            raw_val=(data[i]&0x0f)<<8 | data[i+1]
            volts =round(self.ConvAdcValue(bits,vref,raw_val),4)
            if i in range(0,4):
                self.updateAdcValues(list,volts,index)
            print("ADC Chan",index, raw_val, volts)
            i+=2

    def float_to_hex(self,f):
        ''' Discription??'''
        return hex(struct.unpack('<I', struct.pack('<f', f))[0])

    def format_hex(self, _object):
        """Format a value or list of values as 2 digit hex."""
        try:
            values_hex = [self.to_hex(value) for value in _object]
            return '[{}]'.format(', '.join(values_hex))
        except TypeError:
            # The object is a single value
            return self.to_hex(_object)

    def to_hex(self, value):
        return '0x{:02X}'.format(value)

    def GetNbData(self,All = False, updateDac=True):
        ''' Discription??'''
        activeTabName = self.notebook.tab(tk.CURRENT)
        tabname=activeTabName['text']
        if All == True:
            for tbname in sorted(self.tabdata.keys()):
                print("TAB NAMES:",self.tabdata.keys())
                print("Currently",tbname)
                datalist=[]
                for i,spinbox in enumerate(self.tabdata[tbname]):
                    if hasattr(spinbox,'get'):
                        datalist.append(spinbox.get())
                    else:
                        raise ValueError(f"Expected a widget with .get() method, but got {type(spinbox)}.") 
                    word = tbname.split('s')
                    index = int(word[2]) #Get hvssx index 'x'
                    print("GETNBDATA",tbname, i,index, spinbox.get())
                if updateDac == True:
                    self.updateDAC(datalist,index)
                return datalist
        else:
            active_tab_id = self.notebook.index(self.notebook.select())
            active_tab_name = self.notebook.tab(active_tab_id, 'text')
            datalist=[]
            for tbname in sorted(self.tabdata.keys()):
                if tbname == tabname:
                    for i,spinbox in enumerate(self.tabdata[tabname]):
                        datalist.append(spinbox.get())
                        word = tabname.split('s')
                        index = int(word[2])#Get hvssx index 'x'

                    print(tabname,"\n",index, i, spinbox.get())
                    #print(tabname)
                    if updateDac == True:
                        self.updateDAC(datalist,index)
                    return datalist

    def InitMcp230XX(self):
        self.mcp1 =  Adafruit_MCP230XX(address = TP_MASK, num_gpios = 16) # MCP23016
        self.mcp2 =  Adafruit_MCP230XX(address = NHIT_MASK, num_gpios = 16)# MCP23016
        print("Done Refresh!!")

    def updateMask(self, mcp):
        self.Board_select(None)
        # self.mcp2 = Hvss16_I2C(address = NHIT_MASK, num_gpios = 16)
        # ''Discription??''
        data = self.GetNbData(updateDac=False)
    # print(data[48], data[49],int(data[48],16),int(data[49],16),hex(int(data[48],16)),hex(int(data[49],16)))

        if mcp == TP_MASK:
            self.mcp1.write16(int(data[48],16))
            print('TP DATA=:',hex(int(data[48],16)), self.mcp1.readU16())
        elif mcp == NHIT_MASK:
            self.mcp2.write16(int(data[49],16))
            print('NHIT DATA=:',hex(int(data[49],16)), self.mcp2.readU16())

    def Board_select(self, board_name = None, mode=0):

        board_id = 0
        if mode == 0:
            if board_name==None:
                activeTabName = self.notebook.tab(tk.CURRENT)
                tabname=activeTabName['text']
                word = tabname.split('s')
                board_index = int(word[2])#Get hvssx index 'x'
            else:
                board_index = board_name
        if mode == 1:
            word = board_name.split('s')
            board_index = int(word[2])#Get hvssx index 'x'
            
        '''Deselect all boards'''
        [GPIO.output(gpio_pin, GPIO.LOW) for gpio_pin in self.Rpi_hvss_gpio]
        '''select board for current tab'''
        board_id = self.Rpi_hvss_gpio[board_index]
        GPIO.output(board_id, GPIO.HIGH)
        if mode == 0:
            print("Board Name", board_name,"\nRPi GPIO",board_id,)
        return board_id

    def TestPulseClk_Enable(self,sw,board_index):

        Tp_id = 0

        print("Message",sw, board_index)

        Board_id = self.Board_select(None)
        print("HVSS GPIO:",Board_id)

        if sw == '0':
            '''select board for current tab'''
            Tp_id = self.Rpi_TP_gpio[board_index]
            GPIO.output(Tp_id, GPIO.LOW)
            print("Disable Rpi_TP_gpio", Tp_id)
        if sw == '1':
            '''select board for current tab'''
            Tp_id = self.Rpi_TP_gpio[board_index]
            GPIO.output(Tp_id, GPIO.HIGH)
            print("Enable Rpi_TP_gpio", Tp_id)

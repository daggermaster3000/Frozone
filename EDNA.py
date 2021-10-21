# -*- coding: utf-8 -*-
"""
Spyder Editor
Code for the frozone...
Very basic but it works


"""

import matplotlib
matplotlib.use('TkAgg')  # this has to go before the other imports
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import tkinter as Tk
import pyvisa as visa
from simple_pid import PID

import openpyxl
from openpyxl.chart import LineChart,Reference






def main():
   
    # set up a PyVISA instrument and a list for the data
    rm = visa.ResourceManager()
    data = []
    time = []
    global elapsed_time
    elapsed_time = 0
    
    try:
        U1272a = rm.open_resource('ASRL4::INSTR')       # Insert here the name of thermometer module
        DLM6010 = rm.open_resource('GPIB0::29::INSTR')      #Insert here the name of power supply (find names in the NIMAX software in scan devices)
        DLM6010.write('SOUR:CURR 5.0') 
    except:
        pass
    
    def refresh():
      data.clear()
   
    
    # make a Tkinter window
    root = Tk.Tk()
    root.title("Frozone")
    root.iconbitmap("icon.ico")
    root.geometry('800x600')
    leftframe = Tk.Frame(root)
    leftframe.pack(side=Tk.LEFT)
    rightframe = Tk.Frame(root)
    rightframe.pack(side=Tk.RIGHT)
   
    # add widgets to window
    label = Tk.Label(leftframe,text="Target Temperature")
    label2 = Tk.Label(leftframe,text="Real Temperature")
    refresh_button = Tk.Button(text='Refresh',command=refresh)
    time_label = Tk.Label(text="Time [ms]")
    instant_time = Tk.Label(text='0')
    #spinbox widget
    v = Tk.StringVar(root, value='0')
    e = Tk.Spinbox(leftframe,from_=-50, to=20, increment=0.1, textvariable=v, wrap=False)
    
    '''Function to output excel graph'''
    def write_excel():
      
        wb = openpyxl.Workbook()
        sheet = wb.active
          
        # write in 1st column of the active sheet
        for i in data:
            sheet.append([i])
      
        yvalues = Reference(sheet, min_col = 1, min_row = 1,max_col = 1, max_row = len(data))
            # Create object of LineChart class
        chart = LineChart()
          
        chart.add_data(yvalues)
          
        # set the title of the chart
        chart.title = " Temp vs time "
          
        # set the title of the x-axis
        chart.x_axis.title = " time "
        #chart.x_axis.tickLblSkip = 100
          
        # set the title of the y-axis
        chart.y_axis.title = " temperature C° "
          
        # add chart to the sheet
        # the top-left corner of a chart
        # is anchored to cell E2 .
        sheet.add_chart(chart, "E2")
          
        # save the file
        wb.save("Temp_chart.xlsx")   

    
    target_temp = Tk.Label(leftframe,text="---")
    realtemp = Tk.Label(leftframe,text="---")
    exit_button = Tk.Button(root, text="Exit", command=root.destroy)

    # add a matplotlib figure to the Tk window
    fig = Figure()
    ax = fig.add_subplot(111)
    canv = FigureCanvasTkAgg(fig, master=root)
    
    
    
    label.pack()
    e.pack()
    #e_rate.pack()
    target_temp.pack()
    canv.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canv, root)
    toolbar.update()
    canv.get_tk_widget().pack(fill=Tk.BOTH,expand=True,ipadx=10,ipady=10)
    label2.pack()
    
    realtemp.pack()
    time_label.pack(side=Tk.BOTTOM)
    instant_time.pack(side=Tk.BOTTOM)
    exit_button.pack(side=Tk.BOTTOM)
    refresh_button.pack(side=Tk.BOTTOM)

    
    '''pid function'''
    def main_pid(p,i,d,setpoint,temp_sense,lim_min):
      p = -9
      i =-23
      d =-1
      
      
      controlled_system = temp_sense
      pid = PID(p, i, d, setpoint)
      pid.output_limits = (0, 14) 
    
      # Assume we have a system we want to control in controlled_system
      v = controlled_system
    
      while True:
          # Compute new output from the PID according to the systems current value
          control = pid(v)
    
          # Feed the PID output to the system and get its current value
          #print("correct: ", control)
          #print("target: ", setpoint)
          return(control)
    
   
    ''' a function that is called periodically by the event loop'''
    def plot_update():
        global elapsed_time
        #PID stuff
        try:
          target=float(v.get())
          corr = main_pid(-7,-5,-0,target,float(U1272a.query('FETC?')[:-2]),0)
          DLM6010.write(f'SOUR:VOLT {corr}')
          target_temp.configure(text=str(target))
        except:
          pass
        
        
        # add a new measure to the data
        data.append(float(U1272a.query('FETC?')[:-2]))
        #data.append(float(1))
        time.append(float(elapsed_time))
        elapsed_time+=200
        #display live temperature
        realtemp.configure(text=str(float(U1272a.query('FETC?')[:-2])))
        #display time
        instant_time.configure(text=str(time[-1]))
        # replot the data in the Tk window
        ax.clear()    
        ax.set_title("Live Temperature")
        ax.set_xlabel("Time")
        ax.set_ylabel("C°")
        ax.plot(data)
        fig.tight_layout()
        
        canv.draw()
        write_excel()
        # wait a 100 ms before the next plot
        root.after(100, plot_update)
    
    
    root.after(100, plot_update)
    root.mainloop()
    


if __name__ == "__main__":
    main()

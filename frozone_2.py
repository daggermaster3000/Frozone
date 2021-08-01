from numpy.core.shape_base import block
from simple_pid import PID
import pyvisa as visa
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime
from multiprocessing import Process

#graph output
def animate(i,xs,ys,timeLastCall,U1272A,frameNb,ax):

    temperature = float(U1272A.query('FETC?')[:-2])
    #print(f'frame: {frameNb}', end='\r',flush=True)

    xs.append(datetime.datetime.now().timestamp()-timeLastCall)
    ys.append(temperature)

    #draw x and y lists
    ax.clear()
    ax.plot(xs, ys)

    #format plot
    plt.xticks(rotation = 45, ha = 'right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Temperature over time')
    plt.ylabel('Temperature C°')


#setup instruments






#pid function
def main_pid(p,i,d,setpoint,temp_sense):
  controlled_system = temp_sense
  pid = PID(p, i, d, setpoint)
  pid.output_limits = (0, 14) 
  # Assume we have a system we want to control in controlled_system
  v = controlled_system

  while True:
      # Compute new output from the PID according to the systems current value
      control = pid(v)

      # Feed the PID output to the system and get its current value
      print("correct: ", control)
      print("target: ", setpoint)
      return(control)




def runGraph(U1272A):
        
        frameNb = 0
        fig = plt.figure(figsize=(6,4))
        ax = fig.add_subplot(1,1,1)
        plt.title('Dynamic axes')
        xs=[]
        ys=[]
        aniLastCall = datetime.datetime.now().timestamp()
        
        ani = animation.FuncAnimation(fig,animate,fargs=(xs,ys,aniLastCall,U1272A,frameNb, ax),interval=1000)
        aniLastCall = datetime.datetime.now().timestamp()
        frameNb += 1
        plt.show()
        





def main(U1272A,DLM6010):

  while True:
      real_temp = float(U1272A.query('FETC?')[:-2])
  
      
      print("T°: ",real_temp)
      corr = main_pid(-100,0,0,-5,real_temp)
      #DLM6010.write('SOUR:VOLT ',real_temp)
      DLM6010.write(f'SOUR:VOLT {corr}')

      
      time.sleep(1)    #wait 1s
              



if __name__ == '__main__':

  rm = visa.ResourceManager()
  Visa_name = 'ASRL7::INSTR'
  VisaDLM6010 = 'GPIB0::29::INSTR'
  with rm.open_resource(Visa_name) as U1272A:
        print('connected to ', end='')
        print(U1272A.query('*IDN?'))

        with rm.open_resource(VisaDLM6010) as DLM6010:
            print(DLM6010.query('*IDN?'))
            DLM6010.write('SOUR:CURR 5.0')

            p1=Process(target=runGraph(U1272A))
            p2=Process(main(U1272A,DLM6010))
            p2.start()
            p1.start()
            

            
            
            
            
          
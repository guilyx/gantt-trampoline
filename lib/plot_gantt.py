# Importing the matplotlb.pyplot 
import matplotlib.pyplot as plt 
import numpy as np

class GanttPlot():
    def __init__(self, ylim, xlim):
        self.fig, self.gnt = plt.subplots()
        self.gnt.set_ylim(0, ylim)
        self.gnt.set_xlim(0, xlim)
        self.ylim = ylim

        # Setting labels for x-axis and y-axis 
        self.gnt.set_xlabel('Time(s)') 
        self.gnt.set_ylabel('Tasks')

        # Setting graph attribute 
        self.gnt.grid(True)

        # Define available y position
        self.available_y = []
        index = 0
        while index < ylim:
            self.available_y.append((index, 2))
            index += 3

        #Initiate labels
        self.ylabels = [str(elem) for elem in range(ylim)]
        self.gnt.set_yticks([elem[0]+1 for elem in self.available_y]) 

        self.numberTasks = 0
    
    def addTask(self, task):
        if self.numberTasks == int(self.ylim/3):
            print('Task was not added, gantt diagram full. Extend ylim to add more tasks.')
        else:
            y_index = self.available_y[self.numberTasks]
            self.ylabels[self.numberTasks] = task.name
            self.gnt.set_yticklabels(labels=self.ylabels)
            self.gnt.broken_barh(task.runningPeriods, y_index, facecolors=np.random.rand(3,))
            self.gnt.plot(task.terminationTime, y_index[0], c='red', marker='o')
            self.gnt.arrow(task.activationTime, y_index[0]-0.2, 0, 2, color='red', width=0.8, head_width=0.6)
            self.numberTasks += 1
    
    def show(self):
        plt.show()

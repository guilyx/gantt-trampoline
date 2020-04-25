# Importing the matplotlb.pyplot
import matplotlib.pyplot as plt
import numpy as np


class GanttPlot():
    def __init__(self, ylim, xlim):
        self.fig, self.gnt = plt.subplots(figsize=(12, 8))
        self.gnt.set_ylim(0, ylim)
        self.gnt.set_xlim(0, xlim)
        self.ylim = ylim
        self.tasksYticks = {}
        self.tasksColors = {}
        self.tasks = {}

        # Setting labels for x-axis and y-axis
        self.gnt.set_xlabel('Time(s)')
        self.gnt.set_ylabel('Tasks')

        # Setting graph attribute
        self.gnt.grid(True)

        # Define available y position
        self.available_y = []
        index = 1
        while index < ylim:
            self.available_y.append((index, 2))
            index += 3

        # Initiate labels
        self.ylabels = [str(_) for _ in range(ylim)]
        self.gnt.set_yticks([_[0]+1 for _ in self.available_y])

        self.numberTasks = 0

    def addTask(self, task):
        # print(self.tasksYticks[task.name])
        if task.name in self.tasksYticks:
            self.gnt.broken_barh(
                task.runningPeriods, self.tasksYticks[task.name], facecolor=self.tasksColors[task.name])
            # self.gnt.plot(task.terminationTime, self.tasksYticks[task.name][0], c='red', marker='o')
            # self.gnt.arrow(task.activationTime, self.tasksYticks[task.name][0]-0.2, 0, 2, color='red', width=0.8, head_width=0.6)
        else:
            print("Warning : Tried to run a task that was not ready.")

    def activateTask(self, task):
        y_index = self.available_y[self.numberTasks]

        if self.numberTasks == int(self.ylim/3):
            print(
                'Task was not added, gantt diagram full. Extend ylim to add more tasks.')
        else:
            self.tasksColors[task.name] = np.random.rand(3,)
            self.tasks[task.name] = task
            self.tasks[task.name].ready = True
            self.tasksYticks[task.name] = y_index
            self.ylabels[self.numberTasks] = task.name
            self.gnt.set_yticklabels(labels=self.ylabels)
            self.numberTasks += 1
            self.gnt.arrow(
                task.activationTime, y_index[0]-0.2, 0, 2, color='red', width=1, head_width=0.6)

    def terminateTask(self, task):
        y_index = self.tasksYticks[task.name]

        if task.name not in self.tasksYticks:
            print("Can't terminate a task that was not registered.")
        else:
            self.tasks[task.name].ready = False
            self.gnt.plot(task.terminationTime,
                          y_index[0], c='red', marker='o')

    def show(self):
        plt.show()

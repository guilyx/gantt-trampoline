'''
__author__ : Erwin Lejeune <erwin.lejeune15@gmail.com>
__date__   : 23/04/2020
__brief__  : Task class
'''

import numpy as np
from lib.plot_gantt import GanttPlot

# A Task has an activation time, running periods and a termination time

# Tony Masters strikes again, this time it's only to check if tasks are scheduled correctly though...

# To DO : Priorities

class TaskMaster():
    def __init__(self):
        self.tasks = dict()
        self.tasks_n = 0
        self.conflicts = 0
        self.maxRunningTime = 0
        self.timelineAvailability = [True for _ in range(0, 200)]
        self.lastTask = None

    def registerTask(self, task):
        resolved = self.__checkConflicts(task)
        if resolved:
            self.__scheduleTask(task)
            self.tasks[task.name] = task
            self.tasks_n += 1
            self.__newMaxRunningTime()

    def deleteTask(self, task):
        self.tasks.pop(task.name)
        self.tasks_n -= 1
        self.__newMaxRunningTime()

    def __checkConflicts(self, task):
        index_running = []
        conflicts = 0

        for elem in task.runningPeriods:
            for index_ in range(elem[0], elem[0] + elem[1]):
                index_running.append(index_)

        for index in index_running:
            if self.timelineAvailability[index] == False:
                conflicts += 1
        
        if conflicts:
            print("Conflicts when scheduling task == ", task.name, "== not scheduling it !")
            return False
        else: 
            return True

    def __newMaxRunningTime(self):
        lastTaskKey = max(
            self.tasks, key=lambda o: self.tasks[o].terminationTime)
        self.lastTask = self.tasks[lastTaskKey]
        self.maxRunningTime = self.lastTask.terminationTime
    
    def __scheduleTask(self, task):
        index_used = []
        for elem in task.runningPeriods:
            for index_ in range(elem[0], elem[0] + elem[1]):
                index_used.append(index_)
        for index in index_used:
            self.timelineAvailability[index] = False
            
    # ------------ # Graphic Methods # ---------------- #

    def plotGantt(self):
        if self.tasks_n > 0:
            self.gnt = GanttPlot(self.tasks_n*3, self.maxRunningTime)
            for elem in self.tasks:
                currentTask = self.tasks[elem]
                self.gnt.addTask(currentTask)
            self.gnt.show()
        else:
            print("Warning : trying to plot a schedule without task")

    def printTasksInfo(self):
        for elem in self.tasks:
            self.tasks[elem].__str__()


class Task():
    def __init__(self, name, runningPeriods):
        self.name = name
        self.activationTime = runningPeriods[0][0]
        self.runningPeriods = runningPeriods
        self.periodActivations = [_[0] for _ in runningPeriods]
        self.terminationTime = runningPeriods[-1][0] + runningPeriods[-1][1]

    def __str__(self):
        data = {
            "Name": self.name,
            "ActivationTime": self.activationTime,
            "RunningPeriods": self.runningPeriods,
            "TerminationTime": self.terminationTime
        }
        print(data)

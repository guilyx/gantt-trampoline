'''
__author__ : Erwin Lejeune <erwin.lejeune15@gmail.com>
__date__   : 23/04/2020
__brief__  : Task class
'''

import numpy as np
from lib.plot_gantt import GanttPlot

# A Task has an activation time, running periods and a termination time


class ReadTrace():
    def __init__(self):
        pass

# Tony Masters strikes again, this time it's only to check if tasks are scheduled correctly though...


class TaskMaster():
    def __init__(self):
        self.tasks = dict()
        self.tasks_n = 0
        self.conflicts = 0
        self.maxRunningTime = 0
        self.lastTask = None

    def registerTask(self, task):
        self.tasks[task.name] = task
        self.tasks_n += 1
        self.__newMaxRunningTime()
        self.checkSchedule()

    def deleteTask(self, task):
        self.tasks.pop(task.name)
        self.tasks_n -= 1
        self.__newMaxRunningTime()

    def checkSchedule(self):
        tempDic = self.tasks.copy()

        for tsk in self.tasks:
            tempDic.pop(tsk)
            activation_times = [
                tempDic[elem].activationTime for elem in tempDic]
            termination_times = [
                tempDic[elem].terminationTime for elem in tempDic]

            for period in self.tasks[tsk].runningPeriods:
                # This only check if activation and termination occur during another task's execution
                if ((any(activation_times) > period[0] and
                     any(activation_times) < (period[0] + period[1])) or
                    (any(termination_times) > period[0] and
                     any(termination_times) < (period[0] + period[1]))):
                    print("This task encountered an issue : ")
                    self.tasks[tsk].__str__()
                    self.conflicts += 1
                    
                # Now checking if any range(start, stop) of each period are superposed
                if True:
                    pass

        if self.conflicts > 0:
            print("Found ", self.conflicts, " conflicts in the schedule...")

    def __newMaxRunningTime(self):
        lastTaskKey = max(
            self.tasks, key=lambda o: self.tasks[o].terminationTime)
        self.lastTask = self.tasks[lastTaskKey]
        self.maxRunningTime = self.lastTask.terminationTime

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
        self.terminationTime = runningPeriods[-1][0] + runningPeriods[-1][1]

    def __str__(self):
        data = {
            "Name": self.name,
            "ActivationTime": self.activationTime,
            "RunningPeriods": self.runningPeriods,
            "TerminationTime": self.terminationTime
        }
        print(data)

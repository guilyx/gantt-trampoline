'''
__author__ : Erwin Lejeune <erwin.lejeune15@gmail.com>
__date__   : 23/04/2020
__brief__  : Task class
'''

import numpy as np

# A Task has an activation time, running periods and a termination time
class ReadTrace():
    def __init__(self):
        pass

# Tony Masters strikes again, this time it's only to check if tasks are scheduled correctly though...
class TaskMaster():
    def __init__(self):
        self.tasks = dict()
        self.tasks_n = 0
    
    def registerTask(self, task):
        self.tasks[task.name] = task
        self.tasks_n += 1
    
    def deleteTask(self, taskId):
        self.tasks.pop(taskId)
        self.tasks_n -= 1
    
    def checkSchedule(self):
        # Implement method to check if there are schedule conflict with registered tasks
        pass

class Task():
    def __init__(self, name, runningPeriods):
        self.name = name
        self.activationTime = runningPeriods[0][0]
        self.runningPeriods = runningPeriods
        self.terminationTime = runningPeriods[-1][0] + runningPeriods[-1][1]
    
    def __str__(self):
        data = {
            "Name" : self.name,
            "ActivationTime" : self.activationTime,
            "RunningPeriods" : self.runningPeriods,
            "TerminationTime" : self.terminationTime
        }
        print(data)
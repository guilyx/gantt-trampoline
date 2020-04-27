'''
__author__ : Erwin Lejeune <erwin.lejeune15@gmail.com>
__date__   : 23/04/2020
__brief__  : Task classes
'''

import json
import sys
import numpy as np
from lib.plot_gantt import GanttPlot
from lib.readTrace import TraceGenerator

# A Task has an activation time, running periods and a termination time

# Tony Masters strikes again, this time it's only to check if tasks are scheduled correctly though...

DEFAULT_TASK_DURATION = 30

class TaskMaster():
    def __init__(self):
        self.tasks = dict()
        self.tasks_n = 0
        self.conflicts = 0
        self.maxRunningTime = 0
        self.timelineAvailability = [True for _ in range(0, 1000000)]
        self.lastTask = None

    def registerTask(self, task, running=True):
        resolved = self.__checkConflicts(task)
        if resolved:
            if task.name not in self.tasks:
                self.tasks[task.name] = task
                self.tasks_n += 1
            else:
                self.tasks[task.name].runningPeriods.append(*(task.runningPeriods))
                self.tasks[task.name].updateTimes()
        if running:
            self.__scheduleTask(task)
            self.__newMaxRunningTime()

    def deleteTask(self, task):
        self.tasks.pop(task.name)
        self.tasks_n -= 1
        self.__newMaxRunningTime()

    def __resolveConflicts(self, task, running_, conflicts):
        # resolve conflicts if any
        return False

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
            print("Conflicts when scheduling task == ",
                  task.name, "== ! Resolving...")
            resolved = self.__resolveConflicts(task, index_running, conflicts)
            return resolved
        else:
            return True

    def generateGanttFromJson(self, staticInfoFilename='../data/tpl_static_info.json', traceFilename='../data/trace.json'):
        generator = TraceGenerator(staticInfoFilename, traceFilename)

        xlim = 0
        for elt in generator.trace:
            if elt['type'] == 'proc':
                state = generator.taskStates[int(elt['target_state'])]
                if state is 'RUNNING':
                    xlim += DEFAULT_TASK_DURATION
            
            elif elt['type'] == 'set_event':  # send event
                # handle set events
                pass

            elif elt['type'] == 'reset_event':  # reset event
                # handle resets events
                pass
        

        gantt = GanttPlot(len(generator.procNames)*3, xlim)
        self.timelineAvailability = [True for _ in range(0, xlim)]

        last_task = None

        for elt in generator.trace:
            if elt['type'] == 'proc':
                # print(self.maxRunningTime)
                start_time = elt['ts']
                taskname = generator.procNames[int(elt['proc_id'])]
                state = generator.taskStates[int(elt['target_state'])]
                if state is 'READY':
                    pass
                elif state is 'SUSPENDED':
                    # print('A task has been terminated...')
                    task_ = Task(taskname, [(self.maxRunningTime, 0)])
                    self.registerTask(task_, running=False)
                    gantt.terminateTask(task_)
                elif state is 'RUNNING':
                    # print('A task is running...')
                    task_ = Task(taskname, [(self.maxRunningTime, DEFAULT_TASK_DURATION)])
                    self.registerTask(task_, running=True)
                    gantt.addTask(task_)
                elif state is 'WAITING':
                    pass
                elif state is 'AUTOSTART':
                    pass
                elif state is 'READY_AND_NEW':
                    # print('A task is ready..')
                    task_ = Task(taskname, [(self.maxRunningTime, DEFAULT_TASK_DURATION)])
                    self.registerTask(task_, running=False)
                    gantt.activateTask(task_)
            
            elif elt['type'] == 'set_event':
                # Put event graphical interpretation here
                pass
        
            elif elt['type'] == 'reset_event':
                # Put event graphical interpretation here
                pass

            else:
                #print('Type from Trace not supported yet')
                pass
            
        gantt.show()

    # ------------ # Graphic Methods # ---------------- #

    def plotGantt(self):
        if self.tasks_n > 0:
            self.gnt = GanttPlot(self.tasks_n*3, self.maxRunningTime)
            for elem in self.tasks:
                currentTask = self.tasks[elem]
                self.gnt.activateTask(currentTask)
                self.gnt.addTask(currentTask)
                self.gnt.terminateTask(currentTask)
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

        self.ready = False

    def updateTimes(self):
        self.activationTime = self.runningPeriods[0][0]
        self.terminationTime = self.runningPeriods[-1][0] + self.runningPeriods[-1][1]

    def __str__(self):
        data = {
            "Name": self.name,
            "ActivationTime": self.activationTime,
            "RunningPeriods": self.runningPeriods,
            "TerminationTime": self.terminationTime
        }
        print(data)

'''
__author__ : Erwin Lejeune <erwin.lejeune15@gmail.com>
__date__   : 23/04/2020
__brief__  : ManualTask classes
'''

import json
import sys
import numpy as np
from math import gcd
from lib.plot_gantt import GanttPlot
from lib.readTrace import TraceGenerator

# A ManualTask has an activation time, running periods and a termination time

# Tony Masters strikes again, this time it's only to check if tasks are scheduled correctly though...

DEFAULT_TASK_DURATION = 30


class ManualTask():
    def __init__(self, name, runningPeriods):
        self.name = name
        self.activationTime = runningPeriods[0][0]
        self.runningPeriods = runningPeriods
        self.periodActivations = [_[0] for _ in runningPeriods]
        self.terminationTime = runningPeriods[-1][0] + runningPeriods[-1][1]
        self.ready = False

    def updateTimes(self):
        self.activationTime = self.runningPeriods[0][0]
        self.terminationTime = self.runningPeriods[-1][0] + \
            self.runningPeriods[-1][1]

    def __str__(self):
        data = {
            "Name": self.name,
            "Priority": self.priority,
            "ActivationTime": self.activationTime,
            "RunningPeriods": self.runningPeriods,
            "TerminationTime": self.terminationTime
        }
        print(data)


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
                self.tasks[task.name].runningPeriods.append(
                    *(task.runningPeriods))
                self.tasks[task.name].updateTimes()
        if running:
            self.__scheduleTask(task)
            self.__newMaxRunningTime()

    def deleteTask(self, task):
        if task.name in self.tasks:
            self.tasks.pop(task.name)
            self.tasks_n -= 1
            if self.tasks_n != 0:
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
                if state == 'RUNNING':
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
                if state == 'READY':
                    pass
                elif state == 'SUSPENDED':
                    # print('A task has been terminated...')
                    task_ = ManualTask(taskname, [(self.maxRunningTime, 0)])
                    self.registerTask(task_, running=False)
                    gantt.terminateTask(task_)
                elif state == 'RUNNING':
                    # print('A task is running...')
                    task_ = ManualTask(
                        taskname, [(self.maxRunningTime, DEFAULT_TASK_DURATION)])
                    self.registerTask(task_, running=True)
                    gantt.addTask(task_)
                elif state == 'WAITING':
                    pass
                elif state == 'AUTOSTART':
                    pass
                elif state == 'READY_AND_NEW':
                    # print('A task is ready..')
                    task_ = ManualTask(
                        taskname, [(self.maxRunningTime, DEFAULT_TASK_DURATION)])
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

class AutomaticTask():
    def __init__(self, name, offset, computation, period, deadline):
        self.name = name
        self.offset = offset
        self.period = period
        self.computation = computation
        self.deadline = deadline
    
    def setUtilizationFactor(self, ui):
        self.ui = ui

    def __str__(self):
        data = {
            "Name": self.name,
            "Offset": self.offset,
            "Period": self.period,
            "Computation": self.computation,
            "Deadline": self.deadline
        }
        print(data)

class JobScheduler():
    def __init__(self):
        self.algorithms = {
            "RateMonotonic": self.schedRateMonotonic,
            "DeadlineMonotonic": self.schedDeadlineMonotonic
        }
        self.tasks = dict()

    def registerTask(self, task):
        if task.name not in self.tasks:
                self.tasks[task.name] = task
        else:
            print("Tried to add the same task twice.")
        
    def removeTask(self, task):
        if task.name not in self.tasks:
            print("Tried to remove a task that was not added.")
        else:
            self.task.pop(task.name)
    
    def check_feasibility(self):
        u = 0
        for t in self.tasks:
            ui = self.tasks[t].computation/self.tasks[t].period
            self.tasks[t].setUtilizationFactor(ui)
            u += ui
        
        self.utilization_factor = u
        if u > 1:
            print("The Job is not feasible.")
            return(False)
        else:
            return(True)
    
    def schedRateMonotonic(self, plot=True):
        feasible = self.check_feasibility()
        self.__calcLCM()
        if feasible:
            self.__checkRM()
            if not self.rm_schedulable:
                pass
            else:
                ranked_tasks = []
                temp_tasks = self.tasks.copy()
                for t in self.tasks:
                    highest_p = min(temp_tasks, key=lambda o: temp_tasks[o].period)
                    ranked_tasks.append(temp_tasks[highest_p])
                    del temp_tasks[highest_p]
                if plot:
                    self.__plotRM(ranked_tasks)

    def schedDeadlineMonotonic(self):
        pass

    def __plotRM(self, job):
        gnt = GanttPlot(3*len(self.tasks), self.hyperperiod)
        availability = [True for _ in range(self.hyperperiod)]
        arrows_n = dict()
        reverse_arrows_n = dict()
        for t in job:
            arrows_n[t.name] = [i*t.period for i in range(gnt.xlim//t.period + 1)]
            reverse_arrows_n[t.name] = [i*t.deadline for i in range(1, gnt.xlim//t.period + 1)]
            for elem in arrows_n[t.name]:
                gnt.plotArrow(t, elem)
            for elem in reverse_arrows_n[t.name]:
                gnt.plotReverseArrow(t, elem)

            for elem in arrows_n[t.name]:
                ok = False
                if elem == arrows_n[t.name][-1]:
                    continue
                for i in range(self.hyperperiod):
                    if availability[elem + i] == True:
                        for j in range(t.computation):
                            if availability[elem + i + j] == True:
                                ok = True
                            else:
                                ok = False
                        
                        if ok is True:
                            for j in range(t.computation):
                                availability[elem + i + j] = False
                            break
                gnt.plotAutoTask(t, [(elem + i + j - 1, t.computation)])
         
        gnt.show()

    def __checkRM(self):
        self.rm_optimal = True
        self.rm_schedulable = True
        offsets = [self.tasks[t].offset for t in self.tasks]
        computations = [self.tasks[t].computation for t in self.tasks]
        periods = [self.tasks[t].period for t in self.tasks]
        deadlines = [self.tasks[t].deadline for t in self.tasks]
        uis = [self.tasks[t].ui for t in self.tasks]

        # all tasks are synchronous
        if any(offsets) != 0:
            self.rm_optimal = False
        if deadlines != periods:
            self.rm_optimal = False

        ll73 = len(self.tasks)*(2**(1/len(self.tasks)) - 1)
        if self.utilization_factor <= ll73:
            self.rm_schedulable = True
        
        if sum(uis) + 1 <= 2:
            self.rm_schedulable = True
        
        if self.rm_schedulable and not(self.rm_optimal):
            print("Rate Monotonic not optimal, do you want to use another algorithm ? --> ")
        
        elif not(self.rm_schedulable):
            print("Rate Monotonic not schedulable, do you want to use another algorithm ? --> ")

    def __checkDM(self):
        pass

    def __calcLCM(self):
        period_list = [self.tasks[t].period for t in self.tasks]
        lcm = period_list[0]
        for elem in period_list[1:]:
            lcm = lcm*elem//gcd(lcm, elem)
        self.hyperperiod = lcm
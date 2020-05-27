'''
__author__ : Erwin Lejeune <erwin.lejeune15@gmail.com>
__date__   : 23/04/2020
__brief__  : ManualTask classes
'''

import json
import sys
import numpy as np
from math import gcd
from lib.GanttPlot import GanttPlot
from lib.Trace import TraceToolbox
import os

current_directory = os.getcwd()
DEFAULT_TPL_PATH = current_directory + "/data/tpl_static_info.json"
DEFAULT_TRACE_PATH = current_directory + "/data/trace.json"
DEFAULT_TASK_DURATION = 5


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
            for index_ in range(int(elem[0]), int(elem[0] + elem[1])):
                index_used.append(index_)
        for index in index_used:
            self.timelineAvailability[index] = False

    def __checkConflicts(self, task):
        index_running = []
        conflicts = 0

        for elem in task.runningPeriods:
            for index_ in range(int(elem[0]), int(elem[0] + elem[1])):
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

    def generate_gantt_from_trace(self, staticInfoFilename=DEFAULT_TPL_PATH, traceFilename=DEFAULT_TRACE_PATH):
        xlim = 0
        trace_toolbox = TraceToolbox(staticInfoFilename, traceFilename)
        procs = []
        for raw_event in trace_toolbox.reader.getEvent():
            ts = raw_event['ts']
            if raw_event['type'] == 'proc':        #proc state udpdate
                i = int(raw_event['proc_id'])
                st= int(raw_event['target_state'])
                state_name = trace_toolbox.evaluator.staticInfo.procStates[st]
                proc_name  = trace_toolbox.evaluator.staticInfo.procNames[i]

                if proc_name not in procs:
                    procs.append(proc_name)

                if state_name=='RUNNING': #//change to running
                    xlim += DEFAULT_TASK_DURATION

            else:
                pass

        gantt = GanttPlot(len(procs)*3, xlim)
        self.timelineAvailability = [True for _ in range(0, xlim)]

        for raw_event in trace_toolbox.reader.getEvent():
            ts = raw_event['ts']
            if raw_event['type'] == 'proc':        #proc state udpdate
                i = int(raw_event['proc_id'])
                st= int(raw_event['target_state'])
                proc_name  = trace_toolbox.evaluator.staticInfo.procNames[i]
                state_name = trace_toolbox.evaluator.staticInfo.procStates[st]

                if state_name == 'READY':
                    pass
                elif state_name == 'SUSPENDED':
                    # print('A task has been terminated...')
                    task_ = ManualTask(proc_name, [(self.maxRunningTime, 0)])
                    self.registerTask(task_, running=False)
                    gantt.terminateTask(task_)
                elif state_name == 'RUNNING':
                    # print('A task is running...')
                    task_ = ManualTask(
                        proc_name, [(self.maxRunningTime, DEFAULT_TASK_DURATION)])
                    self.registerTask(task_, running=True)
                    gantt.addTask(task_)
                elif state_name == 'WAITING':
                    pass
                elif state_name == 'AUTOSTART':
                    pass
                elif state_name == 'READY_AND_NEW':
                    # print('A task is ready..')
                    task_ = ManualTask(
                        proc_name, [(self.maxRunningTime, DEFAULT_TASK_DURATION)])
                    self.registerTask(task_, running=False)
                    gantt.activateTask(task_)
    
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
    '''
    |-------| - Earliest deadline first 
    | TO DO | - Least slack time
    |-------| - ...
    '''
    def __init__(self, name, offset, computation, period, deadline):
        self.name = name
        self.offset = offset
        self.period = period
        self.computation = computation
        self.deadline = deadline
        self.priority = None
    
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
            print("Utilization = ", u)
            print("The Job is not feasible.")
            return(False)
        else:
            return(True)
    
    def response_time_analysis(self, task, algorithm):
        response_time = dict()
        for t in self.tasks:
            response_time[t] = []
        ri = dict()

        if algorithm == "Deadline Monotonic" or algorithm == "dm" or algorithm == "deadline monotonic" or algorithm ==  "deadline Monotonic":
            self.__compute_priorities(1)
        elif algorithm == "Rate Monotonic" or algorithm == "rate monotonic" or algorithm == "rm" or algorithm == "rate Monotonic":
            self.__compute_priorities(0)
        else:
            print("Algorithm not found, exiting...")
            sys.exit()

        task_set = self.__get_subset()

        for t in self.tasks:
            ri[t] = .1
            response_time[t] = 0

        k = 0
        for t in self.tasks:
            if k == 0:
                response_time[t][k] = self.tasks[t].computation
            else:
                while response_time[t] != ri[t]:
                    ri[t] = response_time[t]
                    response_time[t] = self.tasks[t].computation
                    for tj in task_set[t]:
                        response_time[t] = response_time[t] + (ri[t]/tj.period)*tj.computation
            k += 1
        return response_time
        
    
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

    def schedDeadlineMonotonic(self, plot=True):
        feasible = self.check_feasibility()
        self.__calcLCM()
        if feasible:
            self.__checkDM()
            if not self.dm_schedulable:
                pass
            else:
                ranked_tasks = []
                temp_tasks = self.tasks.copy()
                for t in self.tasks:
                    highest_p = min(temp_tasks, key=lambda o: temp_tasks[o].deadline)
                    ranked_tasks.append(temp_tasks[highest_p])
                    del temp_tasks[highest_p]
                if plot:
                    self.__plotDM(ranked_tasks)

    def __plotRM(self, job):
        gnt = GanttPlot(3*len(self.tasks), self.hyperperiod, "Rate Monotonic Schedule")
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
                if ok is True:
                    gnt.plotAutoTask(t, [(elem + i, t.computation)])
         
        gnt.show()

    def __plotDM(self, job):
        gnt = GanttPlot(3*len(self.tasks), self.hyperperiod, "Deadline Monotonic Schedule")
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
                if ok is True:
                    gnt.plotAutoTask(t, [(elem + i, t.computation)])
         
        gnt.show()

    def __checkRM(self):
        '''
        To do : if rm doesnt have sufficient condition, it MIGHT be schedulable
        '''
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
        '''
        To do : if dm doesnt have sufficient condition, it MIGHT be schedulable
        '''
        self.dm_optimal = True
        self.dm_schedulable = True
        offsets = [self.tasks[t].offset for t in self.tasks]
        computations = [self.tasks[t].computation for t in self.tasks]
        periods = [self.tasks[t].period for t in self.tasks]
        deadlines = [self.tasks[t].deadline for t in self.tasks]
        uis = [self.tasks[t].ui for t in self.tasks]

        # all tasks are synchronous
        if any(offsets) != 0:
            self.dm_optimal = False

        for t in self.tasks:
            k = 0
            ranked_tasks = []
            temp_tasks = self.tasks.copy()
            subset = dict()
            while k < len(self.tasks) - 1:
                highest_p = min(temp_tasks, key=lambda o: temp_tasks[o].deadline)
                if temp_tasks[highest_p].deadline < self.tasks[t].deadline:
                    ranked_tasks.append(temp_tasks[highest_p])
                del temp_tasks[highest_p]
                k += 1
            subset[t] = ranked_tasks

        for i in range(len(deadlines)):
            if deadlines[i] > periods[i]:
                self.dm_optimal = False
            
        for t in self.tasks:
            ci = self.tasks[t].computation
            eps = 0
            if t in subset.keys():
                for ts in subset[t]:
                    eps += (self.tasks[t].deadline/ts.period)*ts.computation
                if ( ci + eps ) > self.tasks[t].deadline:
                    self.dm_schedulable = False
                    break
                else:
                    self.dm_schedulable = True
        
        if self.dm_schedulable and not(self.dm_optimal):
            print("Deadline Monotonic not optimal, do you want to use another algorithm ? --> ")
        
        elif not(self.dm_schedulable):
            print("Deadline Monotonic not schedulable, do you want to use another algorithm ? --> ")
    

    def __calcLCM(self):
        period_list = [self.tasks[t].period for t in self.tasks]
        lcm = period_list[0]
        for elem in period_list[1:]:
            lcm = lcm*elem//gcd(lcm, elem)
        self.hyperperiod = lcm

    def __compute_priorities(self, algorithm):
        current_priority = len(self.tasks)
        for i in range(len(self.tasks)):
            if algorithm == 1:
                highest_p = min(self.tasks, key=lambda o: self.tasks[o].deadline)
            elif algorithm == 0:
                highest_p = min(self.tasks, key=lambda o: self.tasks[o].period)
            else:
                print("Priority computation failed.")
            self.tasks[highest_p].priority = current_priority
            current_priority -= 1

    def __get_subset(self):
        subset = dict()
        for t in self.tasks:
            subset[t] = []
            t_copy = self.tasks.copy()
            t_copy.pop(t)
            for sub_t in t_copy:
                if (t_copy[sub_t].priority > self.tasks[t].priority):
                    subset[t].append(self.tasks[t])
        return subset
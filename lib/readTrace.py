#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
import json
import sys

class ReadTrace():
    def __init__(self, static_info_filename, trace_filename):
        
        #---------------------------------
        #read static information JSON file
        #---------------------------------
        self.staticInfo = []
        try:
            with open('../data/tpl_static_info.json') as self.staticInfoFile:
                self.staticInfo = json.load(self.staticInfoFile)
        except OSError as e:
            print('static information file not found (events.json). '
                'You should enable the self.trace in the .oil file and '
                'recompile your application.')
            sys.exit(1)

        #---------------------------------
        #Ok, now self.trace JSON file
        #---------------------------------
        self.trace = []
        try:
            with open('../data/self.trace.json')  as self.traceFile:
                self.trace = json.load(self.traceFile)
        except OSError as e:
            print('self.trace file not found (self.trace.json). '
                'You should run your application.')
            sys.exit(1)

        #---------------------------------
        #Now, we add some specific stuff for Trampoline
        #---------------------------------
        # proc (task+isr) names
        self.procNames = []
        for proc in self.staticInfo['task']:
            self.procNames.append(proc['NAME'])
        self.procNames.append('idle') #idle task is the last one.
        # OS constant names (task states, alarm states)
        self.taskStates = ['SUSPENDED','READY','RUNNING','WAITING','AUTOSTART','READY_AND_NEW']
        self.timeObjStates = ['SUSPENDED','READY','RUNNING','WAITING','AUTOSTART','READY_AND_NEW']
        # track the running task (init to idle)
        runningTask = len(self.procNames)-1

    def printTrace(self):
        #---------------------------------
        #Exploit the trace, chronologically
        #---------------------------------
        for elt in self.trace:
            print('[{0: >10}] '.format(elt['ts']), end='')
            if elt['type'] == 'proc':        #proc state udpdate
                i = int(elt['proc_id'])
                st=int(elt['target_state'])
                print('proc {0: <20} change to state {1}'.format(self.procNames[i],self.taskStates[st]))
                if self.taskStates[st]=='RUNNING': #//change to running
                    runningTask = i
            elif elt['type'] == 'timeobj_expire': #alarm expire
                i = int(elt['timeobj_id'])
                to = self.staticInfo['alarm'][i]
                print('time object expired: {0}'.format(to['NAME']))
            elif elt['type'] == 'timeobj':   #alarm state update
                i = int(elt['timeobj_id'])
                print('time object "{0:>11}" change to state {1}'.format(
                    to['NAME'],
                    timeObjStates[int(elt['target_state'])]))
            elif elt['type'] == 'set_event': #send event
                target  = int(elt['target_task_id'])
                evtId   = int(elt['event'])-1
                evtName = self.staticInfo['task'][target]['EVENT'][evtId]['VALUE']
                print('Event {0:>12} (id {1}) sent to task {2}'.format(
                    evtName,
                    int(elt['event']),
                    self.procNames[target]))
            elif elt['type'] == 'reset_event': #reset event
                target  = runningTask
                evtId   = int(elt['event'])-1
                evtName = self.staticInfo['task'][target]['EVENT'][evtId]['VALUE']
                print('task {0:>20} resets event {1:>10} (id {2})'.format(
                    self.procNames[i],
                    evtName,
                    int(elt['event'])))
            else:
                print('unhandled type: {0}'.format(elt['type']))

    def writeTrace(self, filename):


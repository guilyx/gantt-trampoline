#! /usr/bin/env python3
# -*- coding: UTF-8 -*-
import json
import time
import sys
import os


class TraceGenerator():
    def __init__(self, static_info_filename='../data/tpl_static_info.json', trace_filename='../data/trace.json'):

        # ---------------------------------
        # read static information JSON file
        # ---------------------------------
        self.staticInfo = []
        try:
            with open(static_info_filename) as self.staticInfoFile:
                self.staticInfo = json.load(self.staticInfoFile)
        except OSError as e:
            print('static information file not found (events.json). '
                  'You should enable the trace in the .oil file and '
                  'recompile your application.')
            sys.exit(1)

        # ---------------------------------
        # Ok, now self.trace JSON file
        # ---------------------------------
        self.trace = []
        try:
            with open(trace_filename) as self.traceFile:
                self.trace = json.load(self.traceFile)
        except OSError as e:
            print('trace file not found (trace.json). '
                  'You should run your application.')
            sys.exit(1)

        # ---------------------------------
        # Now, we add some specific stuff for Trampoline
        # ---------------------------------
        # proc (task+isr) names
        self.procNames = []
        for proc in self.staticInfo['task']:
            self.procNames.append(proc['NAME'])
        self.procNames.append('idle')  # idle task is the last one.
        # OS constant names (task states, alarm states)
        self.taskStates = ['SUSPENDED', 'READY', 'RUNNING',
                           'WAITING', 'AUTOSTART', 'READY_AND_NEW']
        self.timeObjStates = ['SUSPENDED', 'READY',
                              'RUNNING', 'WAITING', 'AUTOSTART', 'READY_AND_NEW']
        # track the running task (init to idle)
        runningTask = len(self.procNames)-1

    def __getEventName(self, staticInfo, task, target, mask):
        for taskEvt in staticInfo['task'][target]['EVENT']:
            for evt in staticInfo['event']:
                if evt['MASK'] == mask and taskEvt['VALUE'] == evt['NAME']:
                    return evt['NAME']

    def printTrace(self):
        # ---------------------------------
        # Exploit the trace, chronologically
        # ---------------------------------
        for elt in self.trace:
            print('[{0: >10}] '.format(elt['ts']), end='')
            if elt['type'] == 'proc':  # proc state udpdate
                i = int(elt['proc_id'])
                st = int(elt['target_state'])
                print('proc {0: <20} change to state {1}'.format(
                    self.procNames[i], self.taskStates[st]))
                if self.taskStates[st] == 'RUNNING':  # //change to running
                    runningTask = i
            elif elt['type'] == 'timeobj_expire':  # alarm expire
                i = int(elt['timeobj_id'])
                to = self.staticInfo['alarm'][i]
                print('time object expired: {0}'.format(to['NAME']))
            elif elt['type'] == 'timeobj':  # alarm state update
                i = int(elt['timeobj_id'])
                print('time object "{0:>11}" change to state {1}'.format(
                    to['NAME'],
                    self.timeObjStates[int(elt['target_state'])]))
            elif elt['type'] == 'set_event':  # send event
                target = int(elt['target_task_id'])
                evtMask = int(elt['event'])
                evtName = self.__getEventName(self.staticInfo, target, evtMask)
                print('Event {0:>12} (id {1}) sent to task {2}'.format(
                    evtName, int(elt['event']), self.procNames[target]))
            elif elt['type'] == 'reset_event':  # reset event
                target = int(elt['target_task_id'])
                evtMask = int(elt['event'])
                evtName = self.__getEventName(self.staticInfo, target, evtMask)
                print('task {0:>20} (id {1}) resets event {1:>10} (mask {2})'.format(
                    evtName, int(elt['event']), self.procNames[target]))

            else:
                print('unhandled type: {0}'.format(elt['type']))

    def writeTrace(self, filename):
        path = '../data/' + filename
        self.deleteFile(path)

        for elt in self.trace:
            data = {}
            if elt['type'] == 'proc':  # proc state udpdate
                i = int(elt['proc_id'])
                st = int(elt['target_state'])

                data[elt['ts']] = {
                    elt['type']: ('{0}, {1}'.format(
                        self.procNames[i], self.taskStates[st]))
                }
                if self.taskStates[st] == 'RUNNING':  # //change to running
                    runningTask = i
            elif elt['type'] == 'timeobj_expire':  # alarm expire
                i = int(elt['timeobj_id'])
                to = self.staticInfo['alarm'][i]

                data[elt['ts']] = {
                    elt['type']: (
                        'time object expired: {0}'.format(to['NAME']))
                }

            elif elt['type'] == 'timeobj':  # alarm state update
                i = int(elt['timeobj_id'])

                data[elt['ts']] = {
                    elt['type']: ('time object "{0:>11}" change to state {1}'.format(
                        to['NAME'],
                        self.timeObjStates[int(elt['target_state'])]))
                }

            elif elt['type'] == 'set_event':  # send event
                target = int(elt['target_task_id'])
                evtMask = int(elt['event'])
                evtName = self.__getEventName(self.staticInfo, target, evtMask)

                data[elt['ts']] = {
                    elt['type']: ('Event {0:>12} (id {1}) sent to task {2}'.format(
                        evtName,
                        int(elt['event']),
                        self.procNames[target]))
                }

            elif elt['type'] == 'reset_event':  # reset event
                target = int(elt['target_task_id'])
                evtMask = int(elt['event'])
                evtName = self.__getEventName(self.staticInfo, target, evtMask)
                data[elt['ts']] = {
                    elt['type']: ('task {0:>20} resets event {1:>10} (id {2})'.format(
                        self.procNames[i],
                        evtName,
                        int(elt['event'])))
                }

            else:
                data[elt['ts']] = {
                    elt['type']: 'unhandled type'
                }

            # Fills with new data
            with open(path, 'a') as outfile:
                json.dump(data, outfile, indent=4)

    @staticmethod
    def deleteFile(path):
        try:
            os.remove(path)
        except OSError as e:
            pass


if __name__ == "__main__":
    rt = TraceGenerator()
    rt.writeTrace('generatedTrace.json')

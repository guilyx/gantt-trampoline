import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from lib.Tasks import ManualTask, TaskMaster

DURATION = 5

ts = []

ts.append(ManualTask("task1", [(0, DURATION)]))
ts.append(ManualTask("task2", [(DURATION, 0)]))
ts.append(ManualTask("task3", [(DURATION, DURATION)]))
ts.append(ManualTask("task1", [(DURATION*2, DURATION)]))
ts.append(ManualTask("task2", [(DURATION*3, DURATION)]))

tm = TaskMaster()
for t in ts:
    tm.registerTask(t)

tm.plotGantt()
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from lib.Tasks import ManualTask, TaskMaster

DURATION = 0.5
PERIOD_T1 = 2
PERIOD_T2 = 3

ts = []

t1_time = 2
t2_time = 3

ts.append(ManualTask("task1", [(t1_time, DURATION), (t1_time+PERIOD_T1, DURATION), (t1_time + 2*PERIOD_T1, DURATION), (t1_time + 3*PERIOD_T1, DURATION)]))
ts.append(ManualTask("task2", [(t2_time, DURATION), (t2_time+PERIOD_T2, DURATION), (t2_time + 2*PERIOD_T2, DURATION), (t2_time + 3*PERIOD_T2, DURATION)]))

tm = TaskMaster()
for t in ts:
    tm.registerTask(t)

tm.plotGantt()
import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from lib.Tasks import JobScheduler
from lib.Tasks import AutomaticTask
import random

def test_feasible():
    sched = JobScheduler()
    
    t1 = AutomaticTask('t1', 0, 2, 6, 6)
    t2 = AutomaticTask('t2', 0, 2, 8, 8)
    t3 = AutomaticTask('t3', 0, 2, 12, 12)

    ts = [t1, t2, t3]

    for t in ts:
        sched.registerTask(t)
    
    feasible = sched.check_feasibility()

    assert(feasible == True)


def test_rm_schedulable():
    sched = JobScheduler()
    
    t1 = AutomaticTask('t1', 0, 2, 6, 6)
    t2 = AutomaticTask('t2', 0, 2, 8, 8)
    t3 = AutomaticTask('t3', 0, 2, 12, 12)

    ts = [t1, t2, t3]

    for t in ts:
        sched.registerTask(t)
    
    sched.schedRateMonotonic(False)
    assert(sched.rm_schedulable == True)

def test_not_feasible():
    sched = JobScheduler()
    
    t1 = AutomaticTask('t1', 0, 10, 6, 6)
    t2 = AutomaticTask('t2', 0, 18, 8, 8)
    t3 = AutomaticTask('t3', 0, 48, 12, 12)

    ts = [t1, t2, t3]

    for t in ts:
        sched.registerTask(t)
    
    feasible = sched.check_feasibility()
    assert(feasible == False)

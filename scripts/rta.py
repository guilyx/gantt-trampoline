import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from lib.Tasks import AutomaticTask, JobScheduler

t1 = AutomaticTask("t1", 0, 2, 6, 5)
t2 = AutomaticTask("t2", 0, 2, 8, 4)
t3 = AutomaticTask("t3", 0, 4, 12, 8)

js = JobScheduler()
js.registerTask(t1)
js.registerTask(t2)
js.registerTask(t3)

js.check_feasibility()
rt = js.response_time_analysis(t3, "deadline monotonic")
for t in rt:
    print("Response Time for == ", t, " == is : ", rt[t])
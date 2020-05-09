from lib.task import *
import argparse

def main():
    sched = TaskMaster()
    sched.generateGanttFromJson('data/tpl_static_info.json', 'data/trace.json')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Gantt Diagrams from Real-Time process' traces.")
    parser.add_argument('mode', type=int, default=0, help="0 to build from scratch, 1 to use scheduling algorithms, 2 to use processes' trace")
    parser.add_argument('--tpl_path', type=str, default='data/tpl_static_info.json', help="Register the path to the tpl static info json file")
    parser.add_argument('--trace_path', type=str, default='data/trace.json', help="Register the path to the trace json file")
    args = parser.parse_args()
    sched = TaskMaster()
    if args.mode == 2:
        sched.generateGanttFromJson(args.tpl_path, args.trace_path)
        
    elif args.mode == 0:
        t1 = ManualTask('Task 1', [(0, 50)])
        t2 = ManualTask('Task 2', [(50, 20)])
        t3 = ManualTask('Task 3', [(70, 10), (150, 30)])
        idle = ManualTask('Idle', [(180, 100)])
        t4 = ManualTask('Task 4', [(80, 70)])
        sched.registerTask(t1)
        sched.registerTask(t2)
        sched.registerTask(t3)
        sched.registerTask(t4)
        sched.registerTask(idle)
        sched.plotGantt()

    elif args.mode == 1:
        sched = JobScheduler()
    
        t1 = AutomaticTask('t1', 0, 2, 6, 6)
        t2 = AutomaticTask('t2', 0, 2, 8, 8)
        t3 = AutomaticTask('t3', 0, 2, 12, 8)

        ts = [t1, t2, t3]

        for t in ts: 
            sched.registerTask(t) 
        
        sched.schedRateMonotonic()


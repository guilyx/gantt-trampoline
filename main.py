from lib.task import Task, TaskMaster
import argparse

def main():
    sched = TaskMaster()
    sched.generateGanttFromJson('data/tpl_static_info.json', 'data/trace.json')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Gantt Diagrams from Real-Time process' traces.")
    parser.add_argument('use_trace', type=int, default=0, help="0 to build from scratch, 1 to use processes' trace")
    parser.add_argument('--tpl_path', type=str, default='data/tpl_static_info.json', help="Register the path to the tpl static info json file")
    parser.add_argument('--trace_path', type=str, default='data/trace.json', help="Register the path to the trace json file")
    args = parser.parse_args()
    sched = TaskMaster()
    if args.use_trace == True:
        sched.generateGanttFromJson(args.tpl_path, args.trace_path)
    else:
        t1 = Task('Task 1', [(0, 50)])
        t2 = Task('Task 2', [(50, 20)])
        t3 = Task('Task 3', [(70, 10), (150, 30)])
        idle = Task('Idle', [(180, 100)])
        t4 = Task('Task 4', [(80, 70)])
        sched.registerTask(t1)
        sched.registerTask(t2)
        sched.registerTask(t3)
        sched.registerTask(t4)
        sched.registerTask(idle)
        sched.plotGantt()


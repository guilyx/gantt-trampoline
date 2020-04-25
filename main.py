from lib.task import Task, TaskMaster

def main():
    sched = TaskMaster()
    sched.generateGanttFromJson('data/tpl_static_info.json', 'data/trace.json')

if __name__ == "__main__":
    main()
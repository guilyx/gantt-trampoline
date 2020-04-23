from lib.task import Task, TaskMaster

def main():
    sched = TaskMaster()

    server = Task("Server", [(50, 40), (90, 50)])
    task_ = Task("Task1", [(0, 20)])
    task_2 = Task("Task2", [(140, 50)])
    task_3 = Task("Task3", [(20, 30)])

    sched.registerTask(server)
    sched.registerTask(task_3)
    sched.registerTask(task_2)
    sched.registerTask(task_)

    sched.plotGantt()

if __name__ == "__main__":
    main()
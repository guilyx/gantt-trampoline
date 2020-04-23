from lib.plot_gantt import GanttPlot
from lib.task import Task


def main():
    sched = GanttPlot(10, 200)

    server = Task("Server", [(0, 40), (90, 50)])
    task_ = Task("Task1", [(40, 50)])
    task_2 = Task("Task2", [(40, 50)])
    task_3 = Task("Task3", [(40, 50)])

    sched.addTask(server)
    sched.addTask(task_)
    sched.addTask(task_2)
    sched.addTask(task_3)
    
    sched.show()

if __name__ == "__main__":
    main()
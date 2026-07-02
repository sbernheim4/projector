from typing import Any, overload

from app.projection import Leaf

class Task:
    title: str
    done: bool

class TaskView:
    title: Leaf[str]
    done: Leaf[bool]

task_views: TaskView

class Project:
    name: str
    description: str
    task: Task

class ProjectView:
    name: Leaf[str]
    description: Leaf[str]
    task: TaskView

project_views: ProjectView

class ProjectAddTaskTask:
    title: str

class ProjectAddTaskTaskView:
    title: Leaf[str]

projectaddtasktask_views: ProjectAddTaskTaskView

class ProjectAddTask:
    task: ProjectAddTaskTask

class ProjectAddTaskView:
    task: ProjectAddTaskTaskView

projectaddtask_views: ProjectAddTaskView

class ProjectCompleteTaskTask:
    done: bool

class ProjectCompleteTaskTaskView:
    done: Leaf[bool]

projectcompletetasktask_views: ProjectCompleteTaskTaskView

class ProjectCompleteTask:
    task: ProjectCompleteTaskTask

class ProjectCompleteTaskView:
    task: ProjectCompleteTaskTaskView

projectcompletetask_views: ProjectCompleteTaskView

class ProjectCreateTask:
    title: str
    done: bool

class ProjectCreateTaskView:
    title: Leaf[str]
    done: Leaf[bool]

projectcreatetask_views: ProjectCreateTaskView

class ProjectCreate:
    name: str
    description: str
    task: ProjectCreateTask

class ProjectCreateView:
    name: Leaf[str]
    description: Leaf[str]
    task: ProjectCreateTaskView

projectcreate_views: ProjectCreateView

class ProjectUpdateTask:
    title: str
    done: bool

class ProjectUpdateTaskView:
    title: Leaf[str]
    done: Leaf[bool]

projectupdatetask_views: ProjectUpdateTaskView

class ProjectUpdate:
    name: str
    description: str
    task: ProjectUpdateTask

class ProjectUpdateView:
    name: Leaf[str]
    description: Leaf[str]
    task: ProjectUpdateTaskView

projectupdate_views: ProjectUpdateView

@overload
def views_for(model_cls: type[Project]) -> ProjectView: ...
@overload
def views_for(model_cls: type[ProjectAddTask]) -> ProjectAddTaskView: ...
@overload
def views_for(model_cls: type[ProjectCompleteTask]) -> ProjectCompleteTaskView: ...
@overload
def views_for(model_cls: type[ProjectCreate]) -> ProjectCreateView: ...
@overload
def views_for(model_cls: type[ProjectUpdate]) -> ProjectUpdateView: ...
@overload
def views_for(model_cls: type[Task]) -> TaskView: ...
def views_for(model_cls: type[object]) -> Any: ...

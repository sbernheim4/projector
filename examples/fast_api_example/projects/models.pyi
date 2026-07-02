from typing import Any, overload

from app.projection import Leaf

class Project:
    name: str
    description: str
    task: Task

class ProjectView:
    name: Leaf[str]
    description: Leaf[str]
    task: TaskView

project_views: ProjectView

class Task:
    title: str
    done: bool

class TaskView:
    title: Leaf[str]
    done: Leaf[bool]

task_views: TaskView

@overload
def views_for(model_cls: type[Project]) -> ProjectView: ...
@overload
def views_for(model_cls: type[Task]) -> TaskView: ...
def views_for(model_cls: type[object]) -> Any: ...

from dataclasses import dataclass

from app import api, build_entity, renderer, views_for


@dataclass(kw_only=True)
class Task:
    title: str
    done: bool


@dataclass(kw_only=True)
class Project:
    name: str
    description: str
    task: Task


project_views = views_for(Project)

project_entity = build_entity(Project)
ProjectAPI = api(
    project_entity,
    renderer=renderer.Pydantic,
    Create=project_views.name + project_views.description + project_views.task.title + project_views.task.done,
    Update=project_views.name + project_views.description + project_views.task.title + project_views.task.done,
    AddTask=project_views.task.title,
    CompleteTask=project_views.task.done,
)

ProjectCreate = ProjectAPI.CreateModel
ProjectUpdate = ProjectAPI.UpdateModel
ProjectAddTask = ProjectAPI.AddTaskModel
ProjectCompleteTask = ProjectAPI.CompleteTaskModel

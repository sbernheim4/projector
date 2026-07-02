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
    create=project_views.name + project_views.description + project_views.task.title + project_views.task.done,
    update=project_views.name + project_views.description + project_views.task.title + project_views.task.done,
    addTask=project_views.task.title,
    completeTask=project_views.task.done,
)

ProjectCreate = ProjectAPI.create_model
ProjectUpdate = ProjectAPI.update_model
ProjectAddTask = ProjectAPI.addTask_model
ProjectCompleteTask = ProjectAPI.completeTask_model

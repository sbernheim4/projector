from dataclasses import dataclass

from projector import project, renderer, views_for


@dataclass(kw_only=True)
class Task:
    title: str
    done: bool


@dataclass(kw_only=True)
class Project:
    id: int
    name: str
    description: str
    task: Task


project_views = views_for(Project)

ProjectModels = project(
    Project,
    renderer=renderer.Pydantic,
    Create=project_views.name
    + project_views.description
    + project_views.task.title
    + project_views.task.done,
    Read=project_views.id
    + project_views.name
    + project_views.description
    + project_views.task.title
    + project_views.task.done,
    ListItem=project_views.id + project_views.name + project_views.task.title,
    Update=project_views.name
    + project_views.description
    + project_views.task.title
    + project_views.task.done,
    AddTask=project_views.task.title,
    CompleteTask=project_views.task.done,
)

ProjectCreate = ProjectModels.CreateModel
ProjectRead = ProjectModels.ReadModel
ProjectListItem = ProjectModels.ListItemModel
ProjectUpdate = ProjectModels.UpdateModel
ProjectAddTask = ProjectModels.AddTaskModel
ProjectCompleteTask = ProjectModels.CompleteTaskModel

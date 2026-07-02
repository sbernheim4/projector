from dataclasses import dataclass

from app import views_for


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

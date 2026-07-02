CREATE_PROJECT = """
insert into projects (name, description, task_title, task_done)
values (:name, :description, :task_title, :task_done)
"""

LIST_PROJECTS = """
select id, name, description, task_title, task_done
from projects
order by id
"""

GET_PROJECT = """
select id, name, description, task_title, task_done
from projects
where id = :id
"""

UPDATE_PROJECT = """
update projects
set name = :name,
    description = :description,
    task_title = :task_title,
    task_done = :task_done
where id = :id
"""

DELETE_PROJECT = """
delete from projects
where id = :id
"""

ADD_TASK = """
update projects
set task_title = :task_title,
    task_done = 0
where id = :id
"""

COMPLETE_TASK = """
update projects
set task_done = 1
where id = :id
"""

CREATE_USER = """
insert into users (name, email, city, zip)
values (:name, :email, :city, :zip)
"""

LIST_USERS = """
select id, name, email, city, zip
from users
order by id
"""

GET_USER = """
select id, name, email, city, zip
from users
where id = :id
"""

UPDATE_USER = """
update users
set name = :name,
    email = :email,
    city = :city,
    zip = :zip
where id = :id
"""

DELETE_USER = """
delete from users
where id = :id
"""

RENAME_CITY = """
update users
set city = :city
where id = :id
"""


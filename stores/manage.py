from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from single_store import app, db


manager = Manager(app)
migrate = Migrate(app, db, compare_type = True)

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
'''
This will create a folder called migrations with alembic.ini and env.py files and a sub-folder migrations 
which will include your future migrations. It has to be run only once.
-->>python manage.py db init

Generates a new migration in the migrations folder. The file is pre-filled based on the changes detected by 
alembic, edit the description message at the beginning of the file and make any change you want.
-->>python manage.py db migrate

Implements the changes in the migration files in the database and updates the version of the migration in the 
alembic_version table.
-->>python manage.py db upgrade
'''

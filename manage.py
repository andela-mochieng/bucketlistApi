"""Module runs the application, creates, migrates and upgrades the db """
from app import create_app, db
from app.models import User, BucketList, BucketListItem
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand


app = create_app
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    """Add app, database and models to the shell."""
    return dict(app=app, db=db, User=User, BucketList=BucketList,
                BucketListItem=BucketListItem)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()

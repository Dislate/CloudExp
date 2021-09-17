from CloudExp import app, manager
from CloudExp.commands import start_cli

# Init project's commands for basic setting project
app.cli.add_command(start_cli)

if __name__ == "__main__":
    manager.run()
    app.run()

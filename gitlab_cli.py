import click
import gitlab
from decouple import config

'''
Usage: python gitlab_cli.py --title='Your title' --description='Your description'
'''


gl = gitlab.Gitlab.from_config('somewhere', ['/etc/myfile.cfg'])
project = gl.projects.get(config('GITLAB_PROJECT_ID'))


@click.command()
@click.option('--title', prompt='Title', help='Type the title.')
@click.option('--description', prompt='Description', help='Type the description.')
def create_issue(title, description):
    response = project.issues.create(
        {"title": f"{title}",
         "description": f"{description}"})

    click.echo(response.iid)
    click.echo(response.title)


if __name__ == '__main__':
    create_issue()

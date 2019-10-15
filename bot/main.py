import click
import gitlab
import logging

log = logging.getLogger(__name__)

def main():
    cli(auto_envvar_prefix='APP')

@click.command()
@click.option(
    '--project-id', '-p', required=True, type=int,
    help='The numeric id of the GitLab project to work on.')
@click.option(
    '--source-branch', '-s', required=True,
    help='The source branch to be merged into the target branch')
@click.option(
    '--target-branch', '-t', required=True, help='The target branch')
def cli(project_id, source_branch, target_branch):
    logging.basicConfig(level=logging.INFO)

    gl = gitlab.Gitlab.from_config()
    project = gl.projects.get(project_id)
    comparison = project.repository_compare(source_branch, target_branch)
    diff_has_content = len(comparison['diffs']) > 0
    log.info("Branches {} and {} differ: {}".format(
        source_branch, target_branch, diff_has_content))

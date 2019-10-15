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
@click.option('--url', help='The GitLab instance URL.')
@click.option('--private-token', help='A GitLab private access token.')
def cli(project_id, source_branch, target_branch,
    url=None, private_token=None):

    logging.basicConfig(level=logging.INFO)

    if url is not None or private_token is not None:
        gl = gitlab.Gitlab(url, private_token=private_token)
    else:
        log.info("Using python-gitlab config file")
        gl = gitlab.Gitlab.from_config()

    project = gl.projects.get(project_id)
    comparison = project.repository_compare(source_branch, target_branch)
    diff_has_content = len(comparison['diffs']) > 0
    log.info("Branches {} and {} differ: {}".format(
        source_branch, target_branch, diff_has_content))

import logging

import click
import gitlab

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
    """Diff two branches in a given project and output whether their content
    differs.

    In addition to command line flags, you can configure this tool via
    environment variables by using the long-form arguments, making them
    uppercase, prefixing them with `APP_`, and using underscores `_` as
    separators. E.g. `--private-token` becomes `APP_PRIVATE_TOKEN`.
    """

    logging.basicConfig(level=logging.INFO)

    if url is not None or private_token is not None:
        gl = gitlab.Gitlab(url, private_token=private_token)
    else:
        log.info('Using python-gitlab config file')
        gl = gitlab.Gitlab.from_config()

    project = gl.projects.get(project_id)
    comparison = project.repository_compare(source_branch, target_branch)
    diff_has_content = len(comparison['diffs']) > 0
    log.info('Branches {0} and {1} differ: {2}'.format(
        source_branch, target_branch, diff_has_content))

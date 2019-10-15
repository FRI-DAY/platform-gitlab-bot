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
@click.option('--label', 'labels', default=[], multiple=True,
              help='Label to attach to created MRs (multiple allowed).')
@click.option('--url', help='The GitLab instance URL.')
@click.option('--private-token', help='A GitLab private access token.')
def cli(project_id, source_branch, target_branch, labels,
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

    existing_mr = existing_merge_request(project, source_branch, target_branch)
    if existing_mr is not None:
        log.info('{0} -> {1}: Merge request already exists, stopping. '
                 'MR: {2}'.format(
                    source_branch, target_branch, existing_mr.web_url))
        return

    branch_content_differs = does_branch_content_differ(
        project, source_branch, target_branch)
    if not branch_content_differs:
        log.info('{0} -> {1}: Branch contents are the same, stopping.'.format(
                 source_branch, target_branch))
        return

    mr_title = '⛵️ {0} to {1}'.format(source_branch, target_branch)
    created_mr = project.mergerequests.create({
        'source_branch': source_branch,
        'target_branch': target_branch,
        'title': mr_title,
        'labels': labels})

    log.info('{0} -> {1}: Created MR: {2}'.format(
             source_branch, target_branch, created_mr.web_url))


def does_branch_content_differ(project, source, target):
    comparison = project.repository_compare(source, target)
    return len(comparison['diffs']) > 0


def existing_merge_request(project, source, target):
    existing = project.mergerequests.list(
        state='opened', source_branch=source, target_branch=target)

    return existing[0] if existing else None

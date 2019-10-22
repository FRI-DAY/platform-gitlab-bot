import logging

import click
import gitlab

from bot.runner import Runner
from bot.server import Server

log = logging.getLogger(__name__)


def main():
    cli(auto_envvar_prefix='APP')


@click.group()
@click.option('--url', help='The GitLab instance URL.')
@click.option('--private-token', help='A GitLab private access token.')
@click.pass_context
def cli(ctx, url=None, private_token=None):
    """
    A GitLab bot. For now, it compares a source and a target branch and,
    if their contents differ, it creates a merge request from the source to
    the target branch. This is useful for promoting changes from one branch to
    another, e.g. for managing configuration for different infrastructure
    environments.

    Configuration happens via a configuration file in the project's default
    branch, called `gitlab-bot.yml`.

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

    ctx.ensure_object(dict)
    ctx.obj['gitlab'] = gl


@cli.command()
@click.option(
    '--project-id', '-p', required=True, type=int,
    help='The numeric id of the GitLab project to work on.')
@click.pass_context
def once(ctx, project_id):
    """Run the bot tasks once on a specific GitLab project."""
    runner = Runner(ctx.obj['gitlab'])
    runner.run(project_id)


@cli.command()
@click.pass_context
def server(ctx):
    """Run the bot as an HTTP server reacting to webhooks from GitLab."""
    runner = Runner(ctx.obj['gitlab'])
    Server(runner).run()

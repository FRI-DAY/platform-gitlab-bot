import logging

import click
import gitlab
from aiohttp import web

from bot.runner import Runner

log = logging.getLogger(__name__)


def main():
    cli(auto_envvar_prefix='APP')


@click.command()
@click.option('--server/--no-server', '-d', default=False,
              help='Run an HTTP server receiving webhooks')
@click.option(
    '--project-id', '-p', required=True, type=int,
    help='The numeric id of the GitLab project to work on.')
@click.option('--url', help='The GitLab instance URL.')
@click.option('--private-token', help='A GitLab private access token.')
def cli(server, project_id, url=None, private_token=None):
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

    runner = Runner(gl)

    if server:
        run_server(runner, project_id)
    else:
        runner.run(project_id)


def run_server(runner, project_id):
    run_handler = create_run_handler(runner, project_id)

    app = web.Application()
    app.add_routes([web.post('/', run_handler)])
    web.run_app(app)


def create_run_handler(runner, project_id):
    async def handle_run(request):
        runner.run(project_id)
        return web.Response(text='Done.\n')
    return handle_run

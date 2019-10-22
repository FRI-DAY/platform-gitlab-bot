import hmac
import json
import logging

from aiohttp import web
from pydantic import BaseModel

log = logging.getLogger(__name__)


class Server(object):
    MAX_REQUEST_BODY_SIZE = 128 * 1024

    def __init__(self, runner, webhook_auth_token):
        self.runner = runner
        self.webhook_auth_token = webhook_auth_token

    def run(self):
        if self.webhook_auth_token == '':
            raise Exception('webhook_auth_token is empty')

        app = web.Application()
        app.add_routes([web.post('/webhook', self.handle_webhook)])
        web.run_app(app)

    async def handle_webhook(self, request):
        # For some reason, aiohttp's client_max_size isn't effective here.
        request_body = await request.content.read(self.MAX_REQUEST_BODY_SIZE)
        if not request.content.at_eof():
            raise web.HTTPRequestEntityTooLarge(self.MAX_REQUEST_BODY_SIZE,
                                                request.content_length or 0)

        provided_token = request.headers.get('X-Gitlab-Token', '')
        if not hmac.compare_digest(provided_token, self.webhook_auth_token):
            raise web.HTTPUnauthorized()

        try:
            webhook_request = GitLabWebhookRequest(**json.loads(request_body))
        except Exception as e:
            log.info('Invalid request: {0}'.format(e))
            raise web.HTTPBadRequest()

        log.info('Received webhook for project with id {0}'.format(
                 webhook_request.project_id))

        self.runner.run(webhook_request.project_id)
        return web.Response(text='Done.\n')


class GitLabWebhookRequest(BaseModel):
    project_id: int

import logging

import gitlab

from bot.branch_promotion import BranchPromoter
from bot.config import load_from_yaml as load_config_from_yaml

log = logging.getLogger(__name__)


CONFIG_FILENAME = 'gitlab-bot.yml'


class ConfigNotFound(Exception):
    def __init__(self, details):
        self.details = details


class Runner(object):
    def __init__(self, gitlab):
        self.gitlab = gitlab

    def run(self, project_id):
        project = self.gitlab.projects.get(project_id)
        try:
            config = self.load_config(project)
        except ConfigNotFound as e:
            log.warning(e.details)
            return

        promoter = BranchPromoter(project, config.promote_branches)
        promoter.run()

    def load_config(self, project):
        log.info('Processing "{0}" with default branch "{1}"'.format(
                 project.path_with_namespace,
                 project.default_branch))

        try:
            config_file = project.files.get(file_path=CONFIG_FILENAME,
                                            ref=project.default_branch)
        except gitlab.GitlabGetError as e:
            if e.response_code == 404:
                raise ConfigNotFound(
                    '{0}: "{1}" not found in default branch "{2}", stopping.'
                    .format(project.path_with_namespace,
                            CONFIG_FILENAME,
                            project.default_branch))

            raise e

        log.info('{0}: Using "{1}" found in '
                 'default branch "{2}"'.format(
                    project.path_with_namespace, CONFIG_FILENAME,
                    project.default_branch))

        return load_config_from_yaml(config_file.decode())

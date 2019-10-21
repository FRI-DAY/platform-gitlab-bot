import logging

log = logging.getLogger(__name__)


class BranchPromoter(object):
    def __init__(self, project, config):
        self.project = project
        self.config = config

    def run(self):
        for promote_config in self.config:
            self.create_merge_request(promote_config.source,
                                      promote_config.target,
                                      promote_config.labels)

    def create_merge_request(
            self, source_branch, target_branch, labels):

        existing_mr = self.existing_merge_request(
            self.project, source_branch, target_branch)
        if existing_mr is not None:
            log.info('{0} -> {1}: Merge request already exists, stopping. '
                     'MR: {2}'.format(
                        source_branch, target_branch, existing_mr.web_url))
            return

        branch_content_differs = self.does_branch_content_differ(
            self.project, source_branch, target_branch)
        if not branch_content_differs:
            log.info('{0} -> {1}: Branch contents are the same, stopping.'
                     .format(source_branch, target_branch))
            return

        mr_title = '⛵️ {0} to {1}'.format(source_branch, target_branch)
        created_mr = self.project.mergerequests.create({
            'source_branch': source_branch,
            'target_branch': target_branch,
            'title': mr_title,
            'labels': labels})

        log.info('{0} -> {1}: Created MR: {2}'.format(
                 source_branch, target_branch, created_mr.web_url))

    def does_branch_content_differ(self, project, source, target):
        # It's quite unintuitive, but what we want is
        # `git diff target...source`. We want the changes that happened on
        # source since target was branched off source.
        comparison = project.repository_compare(target, source)
        return len(comparison['diffs']) > 0

    def existing_merge_request(self, project, source, target):
        existing = project.mergerequests.list(
            state='opened', source_branch=source, target_branch=target)

        return existing[0] if existing else None

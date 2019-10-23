# GitLab Bot

This is a GitLab bot, which at the moment only promotes changes from a source branch to a target branch by creating a merge request whenever the contents of the two branches differ. It supports GitLab webhooks to automatically check for changes on the project whenever GitLab receives a push.

#### Features

* Support for GitLab webhooks to automatically check for changes on push
* Automatically create merge requests if branch contents differ
* Project-specific configuration via a `gitlab-bot.yml` file
* Attach specified labels to automatically created merge requests

## Project Configuration

Note: Unless already done, please [install the bot server](#Installation) before configuring a project.

1. Create a `gitlab-bot.yml` in the **default branch** of the project you want to enable GitLab Bot for. This is an example:

    ```
    promote_branches:
    - source: exp
      target: sandbox
      labels:
        - Automated
    - source: sandbox
      target: production
      labels:
        - Automated
    ```

    - `source` and `target` refer to the source and target branch
    - `labels` refers to GitLab labels attached to the create merger requests.

2. Set up a **GitLab webhook integration** for the project.
    * **URL**: `https://<gitlab-bot-host>/webhook`
    * **Secret Token:** As configured for the bot
    * **Trigger**: Only 'Push Events'
    * **Enable SSL verification**: Yes

3. Add the GitLab bot user to the project.
    * **Role:** Developer

## Installation

### GitLab User

Create a GitLab user with the following settings:

* **Access Level:** Regular
* **External:** Yes (no need to give this user more access than necessary)
* **URL:** Add a link to this project repository to allow users to understand the bot (optional).

**Log in as this user** (unless you can't due to SSO), otherwise you must be a GitLab admin and **impersonate** it.

Go to the user's **Settings**, **Access Tokens** and create a new personal access token with the following setting:

* **Scopes:** `api`

You might also want to disable all email notifications for the user under *Settings*, *Notifications*.

### Bot Server

For a server deploment, GitLab bot needs the following environment variables set:

* `APP_URL` - The GitLab instance URL
* `APP_PRIVATE_TOKEN` - A private token to authenticate against GitLab as GitLab user.
* `APP_SERVER_WEBHOOK_AUTH_TOKEN` - A random value that needs to be shared with GitLab, for authentication (generate e.g. using `openssl rand -hex 20`). The value set here must be put into the *Secret Token* field in GitLab, as shown above.

#### Deployment

Deployment happens automatically via GitLab CI on Kubernetes (via kustomize). See [`.gitlab-ci.yml`](.gitlab-ci.yml) and [kubernetes/](kubernetes/) for details.

For recreating the secret containing the environment variables above, you can use the following command:

```bash
kubectl create secret generic gitlab-bot \
    --from-literal=APP_URL=https://gitlab.example.com \
    --from-literal=APP_SERVER_WEBHOOK_AUTH_TOKEN='randomly-generated-string' \
    --from-literal=APP_PRIVATE_TOKEN=='token-from-gitlab'
```

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from common.utils import github_request


class Repository(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    webhook_id = models.PositiveIntegerField(null=True)

    class Meta:
        verbose_name = 'Repositório'
        verbose_name_plural = 'Repositórios'

    def __str__(self):
        return self.name

    def has_webhook(self):
        return self.webhook_id is not None

    def add_webhook(self, token, webhook_url):
        if not self.has_webhook():
            repo_name = self.name
            webhook_data = {'config': {'url': webhook_url, 'content_type': 'json'}}
            # repo.name already contains {user_name}/{project_name}
            endpoint = f'repos/{repo_name}/hooks'
            req = github_request(endpoint, 'post', token, webhook_data)
            if req.status_code == 201:
                webhook = req.json()
                self.webhook_id = webhook['id']
                self.save()

    @staticmethod
    def repository_exists(owner_name, project_name, credentials):
        endpoint = f'repos/{owner_name}/{project_name}'
        token = credentials.extra_data['access_token']
        req = github_request(endpoint, 'get', token, {})
        if req.status_code == 200:
            return True
        return False


class Commit(models.Model):
    code = models.CharField(max_length=255, unique=True)
    url = models.URLField(max_length=255, default='')
    message = models.CharField(max_length=255)
    date = models.DateTimeField(default=timezone.now)
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.code

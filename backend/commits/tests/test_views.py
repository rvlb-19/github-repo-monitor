from unittest import mock
from django.shortcuts import reverse
from rest_framework import status
from common.tests.test_base import BaseTestCase

from commits.models import Repository, Commit


class ViewsFetchBaseTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        first_repo = Repository.objects.create(name='foo-user/first-repo', owner=self.foo_user)
        second_repo = Repository.objects.create(name='foo-user/second-repo', owner=self.foo_user)
        not_foo_repo = Repository.objects.create(name='bar-user/not-foo-repo', owner=self.bar_user)

        self.first_repo = first_repo
        self.second_repo = second_repo
        self.not_foo_repo = not_foo_repo


class FetchRepositoriesTestCase(ViewsFetchBaseTestCase):
    endpoint = reverse('Repository-list')

    def test_response_only_has_user_repositories(self):
        client = self.client
        client.force_authenticate(user=self.foo_user)
        response = client.get(self.endpoint)
        data = response.data
        self.assertEqual(data['count'], 2, 'Retorna apenas os repositórios de foo-user')


class FetchCommitsTestCase(ViewsFetchBaseTestCase):
    endpoint = reverse('Commit-list')

    def setUp(self):
        super().setUp()

        Commit.objects.create(
            code='468427924',
            url='http://github.com/foo-user/first-repo/468427924',
            message='All your bases are belong to us',
            date='1995-02-10 13:46:00-03:00',
            repository=self.first_repo,
        )

        Commit.objects.create(
            code='4739844',
            url='http://github.com/foo-user/first-repo/4739844',
            message='The cake is a lie',
            date='1995-02-10 13:46:00-03:00',
            repository=self.first_repo,
        )

        Commit.objects.create(
            code='804353500',
            url='http://github.com/foo-user/first-repo/804353500',
            message='It is dangerous to go alone',
            date='1995-02-10 13:46:00-03:00',
            repository=self.first_repo,
        )

        Commit.objects.create(
            code='742867934',
            url='http://github.com/foo-user/second-repo/742867934',
            message='You are a wizard, Harry',
            date='1995-02-10 13:46:00-03:00',
            repository=self.second_repo,
        )

        Commit.objects.create(
            code='132442424',
            url='http://github.com/foo-user/second-repo/132442424',
            message='Hey Jude',
            date='1995-02-10 13:46:00-03:00',
            repository=self.second_repo,
        )

        Commit.objects.create(
            code='642742480',
            url='http://github.com/bar-user/not-foo-repo/642742480',
            message='Não é a mamãe',
            date='1995-02-10 13:46:00-03:00',
            repository=self.not_foo_repo,
        )

    def test_response_only_has_user_commits(self):
        client = self.client
        client.force_authenticate(user=self.foo_user)
        response = client.get(self.endpoint)
        data = response.data
        self.assertEqual(data['count'], 5, 'Deveria retornar apenas os commits de foo-user')

    def test_response_only_has_repository_commits(self):
        client = self.client
        client.force_authenticate(user=self.foo_user)

        response = client.get(self.endpoint, {'repository': self.first_repo.pk})
        data = response.data
        self.assertEqual(data['count'], 3, 'Deveria retornar apenas os commits de first_repo')

        response = client.get(self.endpoint, {'repository': self.second_repo.pk})
        data = response.data
        self.assertEqual(data['count'], 2, 'Deveria retornar apenas os commits de second_repo')


class CreateRepositoriesTestCase(BaseTestCase):
    endpoint = reverse('Repository-list')

    @mock.patch('common.utils.requests.get')
    def test_create_repository(self, mock_github):
        # Mocks the responses of the GitHub requests
        mock_github.return_value.status_code = status.HTTP_200_OK

        client = self.client
        client.force_authenticate(user=self.foo_user)
        response = client.post(self.endpoint, {'name': 'foo-user/test-repo'})
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            'Um repositório deveria ter sido criado'
        )

    @mock.patch('common.utils.requests.get')
    def test_create_repository_when_it_already_exists(self, mock_github):
        # Mocks the response of the GitHub request
        mock_github.return_value.status_code = status.HTTP_200_OK
        Repository.objects.create(name='foo-user/test-repo', owner=self.foo_user)

        client = self.client
        client.force_authenticate(user=self.foo_user)
        response = client.post(self.endpoint, {'name': 'foo-user/test-repo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class BulkInsertCommitsTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        repo = Repository.objects.create(name='foo-user/test-repo', owner=self.foo_user)
        self.repo = repo
        self.endpoint = reverse('Repository-bulk-insert-commits', kwargs={'pk': repo.pk})

    @mock.patch('common.utils.requests.get')
    def test_bulk_insert_commits(self, mock_github):
        # Mocks the response of the GitHub request
        mock_github.return_value.status_code = status.HTTP_200_OK
        mock_github.return_value.json.return_value = [
            {
                'sha': '749353593',
                'html_url': 'https://www.foo.com/749353593',
                'commit': {
                    'message': 'Hello World',
                    'author': {
                        'date': '2019-02-10 00:00:00Z'
                    }
                }
            },
            {
                'sha': '31389494',
                'html_url': 'https://www.foo.com/31389494',
                'commit': {
                    'message': 'Bye World',
                    'author': {
                        'date': '2019-02-15 00:00:00Z'
                    }
                }
            }
        ]

        client = self.client
        client.force_authenticate(user=self.foo_user)
        client.post(self.endpoint, {'days': 30})

        commits = Commit.objects.filter(repository=self.repo)
        self.assertEqual(len(commits), 2)

    @mock.patch('common.utils.requests.get')
    def test_bulk_insert_commits_github_fail(self, mock_github):
        # Mocks the response of the GitHub request
        mock_github.return_value.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        client = self.client
        client.force_authenticate(user=self.foo_user)
        client.post(self.endpoint, {'days': 30})

        commits = Commit.objects.filter(repository=self.repo)
        self.assertEqual(len(commits), 0)

    def test_bulk_insert_commits_without_days(self):
        client = self.client
        client.force_authenticate(user=self.foo_user)
        response = client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class WebhookTestCase(BaseTestCase):
    endpoint = reverse('Repository-github-repo-webhook')

    def setUp(self):
        super().setUp()
        test_repo = Repository.objects.create(name='foo-user/test-repo', owner=self.foo_user)
        self.test_repo = test_repo

    def test_webhook_invalid_request_no_header(self):
        client = self.client
        response = client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_webhook_invalid_request_invalid_header(self):
        client = self.client
        client.credentials(HTTP_X_GITHUB_EVENT='pong')
        response = client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_webhook_ping(self):
        client = self.client
        client.credentials(HTTP_X_GITHUB_EVENT='ping')
        response = client.post(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_webhook_push_invalid_body(self):
        client = self.client
        client.credentials(HTTP_X_GITHUB_EVENT='push')
        response = client.post(self.endpoint, {'repository': {}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_webhook_push_no_repository(self):
        client = self.client
        client.credentials(HTTP_X_GITHUB_EVENT='push')
        data = {
            'repository': {
                'full_name': 'bar-user/foo-repo'
            },
            'commits': [],
        }
        response = client.post(self.endpoint, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_webhook_push(self):
        client = self.client
        client.credentials(HTTP_X_GITHUB_EVENT='push')
        data = {
            'repository': {
                'full_name': 'foo-user/test-repo'
            },
            'commits': [
                {
                    'id': '387393',
                    'url': 'https://www.foo.com/387393',
                    'timestamp': '2019-02-10 00:00:00Z',
                    'message': 'Hello World'
                },
                {
                    'id': '759358035',
                    'url': 'https://www.foo.com/759358035',
                    'timestamp': '2019-02-20 00:00:00Z',
                    'message': 'Bye World'
                }
            ],
        }
        response = client.post(self.endpoint, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        commits = Commit.objects.filter(repository=self.test_repo)
        self.assertEqual(len(commits), 2)

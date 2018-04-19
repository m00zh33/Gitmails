import re
import requests
from src.helpers.helpers import Helpers

class GithubCollector(object):
    def __new__(self, args):
        self.args = args
        self.repositories = []
        self.helper = Helpers()

        if self.args.username:
            github_url = "https://api.github.com/users/{}/repos".format(self.args.username)
        if self.args.organization:
            github_url = "https://api.github.com/orgs/{}/repos".format(self.args.organization)
        last_page = self.get_last_page(self, github_url)
        if last_page:
            for i in range(1, (last_page + 1)):
                repos = self.get_repositories(self, github_url + "?page=" + str(i))
                if repos:
                    self.repositories.append(repos)
        return self.helper.flatten(self.repositories)

    def get_last_page(self, url):
        try:
            r = requests.head(url)
            last_url = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2})).+?(?=>)', r.headers['Link'])[-1]
            return int(last_url.split('=')[-1])
        except Exception as e:
            print(e)
            return 1

    def get_repositories(self, url):
        repositories = []
        try:
            result = requests.get(url)
            if result.status_code == 403:
                print("gitmails: Github: API rate limit exceeded")
                return False
            for repository in result.json():
                if 'fork' in repository  and 'clone_url' in repository:
                    if not (repository['fork'] and not self.args.include_forks):
                        repositories.append(repository['clone_url'])
            return repositories
        except Exception as e:
            print(e)
            print("gitmails: Could not collect github repositories")
            return False

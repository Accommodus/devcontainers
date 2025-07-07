import os
import subprocess
from dotenv import load_dotenv
from python_on_whales import docker


class ManageDev():
    def __init__(self,
                 registry="ghcr.io",
                 platforms=["linux/amd64", "linux/arm64"],
                 user=None,
                 token=None,
                 repo=None,
                 api_url=None
                 ):

        load_dotenv()

        if user == None:
            user = os.getenv("GITHUB_ACTOR",
                              "Accommodus")

        if token == None:
            token = os.getenv("GITHUB_TOKEN")

        if repo == None:
            repo = os.getenv("GITHUB_REPOSITORY",
                             "Accommodus/devcontainers")

        if api_url == None:
            api_url = os.getenv("GITHUB_API_URL", "https://api.github.com")

        self.registry = registry
        self.platforms = platforms

        self.user = user
        self.token = token
        self.repo = repo
        self.api_url = api_url

    def login(self):
        docker.login(server=self.registry, username=self.user, password=self.token)


    def prebuild(self, workspace_folder, config, extend=None):
        self.login()

        prebuilt_name = f"{self.registry}/{self.repo}".lower()
        if extend != None:
            prebuilt_name += f"/{extend}".lower()

        latest = f"{prebuilt_name}:latest"
        cache = f"{prebuilt_name}:cache"
        platforms = ",".join(self.platforms)

        cmd = [
            "devcontainer", "build",
            "--workspace-folder", workspace_folder,
            "--config", config,
            "--push", "true",
            "--image-name", latest,
            "--cache-from", cache,
            "--cache-to", cache,
            "--platform", platforms
        ]

        out = subprocess.run(cmd, check=True, text=True)
        print(out)
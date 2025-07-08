import os
import subprocess
import commentjson
from dotenv import load_dotenv
from python_on_whales import docker
from pathlib import Path


class BaseManage:
    def _set_from_env(self,
                      name: str,
                      value,
                      env_var: str,
                      fallback=None
                      ):
        """
        Sets self.<name> to `value` if not None,
        else to os.getenv(env_var, fallback).
        """
        if value is not None:
            setattr(self, name, value)
        else:
            setattr(self, name, os.getenv(env_var, fallback))


class ManageDev(BaseManage):
    def __init__(self,
                 registry: str = "ghcr.io",
                 platforms: list[str] = ["linux/amd64", "linux/arm64"],
                 user: str | None = None,
                 token: str | None = None,
                 repo: str | None = None,
                 api_url: str | None = None
                 ) -> None:

        load_dotenv()

        self._set_from_env('user', user, 'GITHUB_ACTOR')
        self._set_from_env('token', token, 'GITHUB_TOKEN')
        self._set_from_env('repo', repo, 'GITHUB_REPOSITORY',
                           'Accommodus/devcontainers')
        self._set_from_env('api_url', api_url,
                           'GITHUB_API_URL', 'https://api.github.com')

        self.registry = registry
        self.platforms = platforms

    def login(self) -> None:
        docker.login(server=self.registry,
                     username=self.user, password=self.token)

    def prebuild(self,
                 workspace_folder: Path,
                 config: str | None = None,
                 extend: str | None = None
                 ) -> None:

        self.login()

        prebuilt = f"{self.registry}/{self.repo}".lower()
        if extend:
            prebuilt += f"/{extend}".lower()

        latest = f"{prebuilt}:latest"
        cache = f"{prebuilt}:cache"
        platforms = ",".join(self.platforms)

        cmd = [
            "devcontainer", "build",
            "--workspace-folder", str(workspace_folder),
            "--push", "true",
            "--image-name", latest,
            "--cache-from", cache,
            "--cache-to", cache,
            "--platform", platforms
        ]
        if config:
            cmd.extend(["--config", str(config)])

        out = subprocess.run(cmd, check=True, text=True)
        print(out)


class ManageTemplate(BaseManage):
    def __init__(self,
                 license_rel: str,
                 publisher: str | None = None,
                 base_url: str | None = None,
                 ) -> None:

        self._set_from_env('publisher', publisher, 'PUBLISHER')
        self._set_from_env('base_url', base_url, 'REPO_URL')

        self.license_rel = license_rel

    @staticmethod
    def bump_semver(base_version: str, diff: str | int) -> str:
        base_parts = [int(x) for x in base_version.split(".")]
        while len(base_parts) < 3:
            base_parts.append(0)

        if isinstance(diff, int):
            diff_parts = [0, 0, diff]
        else:
            diff_parts = [int(x) for x in diff.split(".")]
            while len(diff_parts) < 3:
                diff_parts.append(0)

        length = max(len(base_parts), len(diff_parts))
        base_parts += [0] * (length - len(base_parts))
        diff_parts += [0] * (length - len(diff_parts))

        new_parts = [b + d for b, d in zip(base_parts, diff_parts)]
        major, minor, patch = new_parts[:3]
        return f"{major}.{minor}.{patch}"

    def complete_template(self,
                          config_path: Path,
                          id: str,
                          version_change: str | int = 0
                          ) -> None:

        with config_path.open("r", encoding="utf-8") as f:
            cfg = commentjson.load(f)

        new_vers = self.bump_semver(cfg["version"], version_change)
        cfg["version"] = new_vers
        cfg["id"] = id

        with config_path.open("w", encoding="utf-8") as f:
            commentjson.dump(cfg, f, indent=4)
            f.write("\n")


def build_all(devcontainers_path="src"):
    man = ManageDev()
    temp = ManageTemplate("Accommodus")

    base = Path(devcontainers_path)
    for subdir in base.iterdir():
        workspace = subdir / ".devcontainer"
        man.prebuild(workspace_folder=workspace,
                     extend=subdir.name)


if __name__ == "__main__":
    build_all()

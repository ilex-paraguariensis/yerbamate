from git import Repo
import os
import ipdb


def parse_url_from_git():

    max_depth = 3

    root_search = os.getcwd()
    nodes = []
    repo = None
    for i in range(max_depth):
        try:
            repo = Repo(root_search)
            break
        except:
            nodes.append(root_search.split("/")[-1])
            # ipdb.set_trace()
            root_search = os.path.join(root_search, "..")
            root_search = os.path.abspath(root_search)

    if repo:
        parsed_url = __parse_repo(repo)

        nodes = nodes[::-1]
        parsed_url = parsed_url + "/".join(nodes) if len(nodes) > 0 else parsed_url
        return parsed_url

    return None


def __parse_repo(repo):
    url = repo.remotes[0].url

    # transform url to https
    if url.startswith("git@"):
        # url = url.replace("git@", "https:/")
        # change git@github.com:oalee/deep-vision.git to https://github.com/oalee/deep-vision
        url = url.replace("git@", "https:/").replace(":", "/").replace("//", "://")

    # remove .git
    if url.endswith(".git"):
        url = url[:-4]

    branch = repo.active_branch.name
    url = f"{url}/tree/{branch}/"
    # ipdb.set_trace()
    return url

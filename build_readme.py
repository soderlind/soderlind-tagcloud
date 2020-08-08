from python_graphql_client import GraphqlClient
import feedparser
import tweepy
import time
import httpx
import json
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()
client = GraphqlClient(endpoint="https://api.github.com/graphql")


TOKEN = os.environ.get("SODERLIND_TOKEN", "")


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(
        marker, chunk, marker)
    return r.sub(chunk, content)


def make_query(after_cursor=None):
    return """
query {
  viewer {
    repositories(first: 100, orderBy: {field:PUSHED_AT, direction:DESC}, privacy: PUBLIC, isFork: false,after:AFTER) {
      pageInfo {hasNextPage, endCursor}
      nodes {
        name
        description
        pushedAt
        url
        forkCount
      }
    }
  }
}
""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )


def fetch_plugins(oauth_token):
    repos = []
    plugins = []
    repo_names = set()
    has_next_page = True
    after_cursor = None

    while has_next_page:
        data = client.execute(
            query=make_query(after_cursor),
            headers={"Authorization": "Bearer {}".format(oauth_token)},
        )
        print()
        print(json.dumps(data, indent=4))
        print()
        for repo in data["data"]["viewer"]["repositories"]["nodes"]:
            if repo["releases"]["totalCount"] and repo["name"] not in repo_names:
                repos.append(repo)
                repo_names.add(repo["name"])
                plugins.append(
                    {
                        "repo": repo["name"],
                        "url": repo["url"],
                        "description": repo["description"],
                        "pushed_at": repo["pushedAt"],
                        "fork_count": repo["forkCount"],

                    }
                )
        has_next_page = data["data"]["viewer"]["repositories"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["data"]["viewer"]["repositories"]["pageInfo"]["endCursor"]
    return plugins


if __name__ == "__main__":
    readme = root / "README.md"
    # project_releases = root / "releases.md"
    releases = fetch_plugins(TOKEN)
    releases.sort(key=lambda r: r["pushed_at"], reverse=True)
    md = "\n".join(
        [
            "* [{description}]({url}) ({fork_count})".format(**release)
            for release in releases[:8]
        ]
    )
    readme_contents = readme.open().read()
    rewritten = replace_chunk(readme_contents, "recent_releases", md)

    readme.open("w").write(rewritten)

# # Write out full project-releases.md file
# project_releases_md = "\n".join(
#     [
#         (
#             "* **[{repo}]({repo_url})**: [{release}]({url}) - {published_day}\n"
#             "<br>{description}"
#         ).format(**release)
#         for release in releases
#     ]
# )
# project_releases_content = project_releases.open().read()
# project_releases_content = replace_chunk(
#     project_releases_content, "recent_releases", project_releases_md
# )
# project_releases_content = replace_chunk(
#     project_releases_content, "release_count", str(len(releases)), inline=True
# )
# project_releases.open("w").write(project_releases_content)

# tils = fetch_tils()
# tils_md = "\n".join(
#     [
#         "* [{title}]({url}) - {created_at}".format(
#             title=til["title"],
#             url=til["url"],
#             created_at=til["created_utc"].split("T")[0],
#         )
#         for til in tils
#     ]
# )
# rewritten = replace_chunk(rewritten, "tils", tils_md)

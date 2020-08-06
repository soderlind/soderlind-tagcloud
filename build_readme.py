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
TWITTER_CONSUMER_KEY = os.environ.get("TWITTER_CONSUMER_KEY", "")
TWITTER_CONSUMER_SECRET = os.environ.get("TWITTER_CONSUMER_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET", "")


def replace_chunk(content, marker, chunk, inline=False):
    r = re.compile(
        r"<!\-\- {} starts \-\->.*<!\-\- {} ends \-\->".format(marker, marker),
        re.DOTALL,
    )
    if not inline:
        chunk = "\n{}\n".format(chunk)
    chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
    return r.sub(chunk, content)


def make_query(after_cursor=None):
    return """
query {
  viewer {
    repositories(first: 100, privacy: PUBLIC, after:AFTER) {
      pageInfo {
        hasNextPage
        endCursor
      }
      nodes {
        name
        description
        url
        releases(last:1) {
          totalCount
          nodes {
            name
            publishedAt
            url
          }
        }
      }
    }
  }
}
""".replace(
        "AFTER", '"{}"'.format(after_cursor) if after_cursor else "null"
    )


def fetch_releases(oauth_token):
    repos = []
    releases = []
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
                releases.append(
                    {
                        "repo": repo["name"],
                        "repo_url": repo["url"],
                        "description": repo["description"],
                        "release": repo["releases"]["nodes"][0]["name"]
                        .replace(repo["name"], "")
                        .strip(),
                        "published_at": repo["releases"]["nodes"][0]["publishedAt"],
                        "published_day": repo["releases"]["nodes"][0][
                            "publishedAt"
                        ].split("T")[0],
                        "url": repo["releases"]["nodes"][0]["url"],
                    }
                )
        has_next_page = data["data"]["viewer"]["repositories"]["pageInfo"][
            "hasNextPage"
        ]
        after_cursor = data["data"]["viewer"]["repositories"]["pageInfo"]["endCursor"]
    return releases


# def fetch_tils():
#     sql = "select title, url, created_utc from til order by created_utc desc limit 5"
#     return httpx.get(
#         "https://til.simonwillison.net/til.json",
#         params={"sql": sql, "_shape": "array",},
#     ).json()
def fetch_tweets():
	auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
	auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
	api = tweepy.API(auth)
	return [
		{
            "title": entry["title"],
            "url": entry["entities"]["expanded_url"].split("#")[0],
            "published": time.strftime('%d.%m.%Y',entry["created_at"]),
		}
		for entry in api.user_timeline()
	]

def fetch_read():
    entries = feedparser.parse("https://getpocket.com/users/soderlind/feed/all")["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": time.strftime('%d.%m.%Y',entry["updated_parsed"]),
        }
        for entry in entries
    ]

def fetch_blog_entries():
    entries = feedparser.parse("https://soderlind.no/feed.xml")["entries"]
    return [
        {
            "title": entry["title"],
            "url": entry["link"].split("#")[0],
            "published": time.strftime('%d.%m.%Y',entry["updated_parsed"]),
        }
        for entry in entries
    ]


if __name__ == "__main__":
    readme = root / "README.md"
    project_releases = root / "releases.md"
    releases = fetch_releases(TOKEN)
    releases.sort(key=lambda r: r["published_at"], reverse=True)
    # md = "\n".join(
    #     [
    #         "* [{repo} {release}]({url}) - {published_day}".format(**release)
    #         for release in releases[:8]
    #     ]
    # )
    # readme_contents = readme.open().read()
    # rewritten = replace_chunk(readme_contents, "recent_releases", md)

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

    entries = fetch_tweets()[:5]
    tweet_md = "\n".join(
        ["* [{title}]({url}) - {published}".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "recent_releases", tweet_md)

    entries = fetch_read()[:5]
    read_md = "\n".join(
        ["* [{title}]({url}) - {published}".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "read", read_md)

    entries = fetch_blog_entries()[:5]
    entries_md = "\n".join(
        ["* [{title}]({url}) - {published}".format(**entry) for entry in entries]
    )
    rewritten = replace_chunk(rewritten, "blog", entries_md)

    readme.open("w").write(rewritten)
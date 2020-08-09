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
	plugins = []
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
		i = 0
		# for i, repo in enumerate(data["data"]["viewer"]["repositories"]["nodes"]):
		for repo in data["data"]["viewer"]["repositories"]["nodes"]:
			plugin_url = repo["url"] + "/blob/master/" + repo["name"] + ".php"
			if len(str(repo["description"])) > 4 and httpx.get(plugin_url).status_code == 200:
				plugins.append(
					{
						"repo": repo["name"],
						"url": repo["url"],
						"font_format": "**" if i % 2 == 0 else "*",
						"description": repo["description"].strip(),
						"pushed_at": repo["pushedAt"],
						"fork_count": repo["forkCount"],
					}
				)
				i = i+1
		has_next_page = data["data"]["viewer"]["repositories"]["pageInfo"][
			"hasNextPage"
		]
		after_cursor = data["data"]["viewer"]["repositories"]["pageInfo"]["endCursor"]
	return plugins


if __name__ == "__main__":
	readme = root / "README.md"
	plugins = fetch_plugins(TOKEN)
	plugins.sort(key=lambda r: r["pushed_at"], reverse=True)
	md = "\n".join(
		[
			"[{font_format}{description}{font_format}]({url}) &nbsp;&nbsp;&nbsp;".format(
				**plugin)
			for plugin in plugins[:20]
		]
	)
	readme_contents = readme.open().read()
	rewritten = replace_chunk(readme_contents, "plugins", md)

	readme.open("w").write(rewritten)

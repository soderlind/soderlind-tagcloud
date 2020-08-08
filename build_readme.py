from python_graphql_client import GraphqlClient
import feedparser
import tweepy
import time
import httpx
import requests
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


	headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36'}

	while has_next_page:
		data = client.execute(
			query=make_query(after_cursor),
			headers={"Authorization": "Bearer {}".format(oauth_token)},
		)
		print()
		print(json.dumps(data, indent=4))
		print()
		for repo in data["data"]["viewer"]["repositories"]["nodes"]:
			plugin_url = repo["url"] + "/" + repo["name"] + ".php"
			# if repo["description"] != "None" and requests.get(plugin_url, headers=headers).status_code == 200:
			# if "".__ne__(repo["description"]):
			if len(str(repo["description"])) > 4 and requests.get(plugin_url, headers=headers).status_code == 200:
				plugins.append(
					{
						"repo": repo["name"],
						"url": repo["url"],
						"plugin_url": plugin_url,
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
	# project_plugins = root / "plugins.md"
	plugins = fetch_plugins(TOKEN)
	plugins.sort(key=lambda r: r["pushed_at"], reverse=True)
	md = "\n".join(
		[
			"[{description}]({url}) ({fork_count}) | ".format(**plugin)
			for plugin in plugins
		]
	)
	readme_contents = readme.open().read()
	rewritten = replace_chunk(readme_contents, "plugins", md)

	readme.open("w").write(rewritten)

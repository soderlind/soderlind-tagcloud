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
			if repo["description"] != "None" & requests.get(plugin_url, headers=headers).status_code == 200:
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
	# project_plugins = root / "plugins.md"
	plugins = fetch_plugins(TOKEN)
	plugins.sort(key=lambda r: r["pushed_at"], reverse=True)
	md = "\n".join(
		[
			"* [{description}]({url}) ({fork_count})".format(**release)
			for release in plugins
		]
	)
	readme_contents = readme.open().read()
	rewritten = replace_chunk(readme_contents, "plugins", md)

	readme.open("w").write(rewritten)

# # Write out full project-plugins.md file
# project_plugins_md = "\n".join(
#	 [
#		 (
#			 "* **[{repo}]({repo_url})**: [{release}]({url}) - {published_day}\n"
#			 "<br>{description}"
#		 ).format(**release)
#		 for release in plugins
#	 ]
# )
# project_plugins_content = project_plugins.open().read()
# project_plugins_content = replace_chunk(
#	 project_plugins_content, "recent_plugins", project_plugins_md
# )
# project_plugins_content = replace_chunk(
#	 project_plugins_content, "release_count", str(len(plugins)), inline=True
# )
# project_plugins.open("w").write(project_plugins_content)

# tils = fetch_tils()
# tils_md = "\n".join(
#	 [
#		 "* [{title}]({url}) - {created_at}".format(
#			 title=til["title"],
#			 url=til["url"],
#			 created_at=til["created_utc"].split("T")[0],
#		 )
#		 for til in tils
#	 ]
# )
# rewritten = replace_chunk(rewritten, "tils", tils_md)

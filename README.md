# list-links-in-issue-pr
List links in GitHub Issue and Pull Requests

### Requirements
see requirements.txt

### Usage
python list.py -o <organization> -r <repo> -t <github_personal_token>

### Parameters
- API_ENDPOINT (GitHub REST API endpoint)
- URL_PATTERN (URL pattern to be searched in issue/pr body)
Both values are defined in settings.py

### Output
File name: {github_org}.{github_repo}.{now}.txt <br>
Output format: <pull/issue>,id,link_url,html_url <br>
pull request = pull <br>
issue = issue <br>
#!/usr/bin/env python3
# -*- coding: utf_8 -*-
"""list.py"""
import csv
import datetime
import getopt
import re
import sys
import requests
from requests.exceptions import RequestException
import settings

USAGE_TEXT = "Usage: list.py -o <organization> -r <repo> -t <github_personal_token>"
OUTPUT_TEXT = "Output: <pull/issue>,id,link_url,html_url"

endpoints = {
    "ISSUES": "{api_endpoint}/repos/{github_org}/{github_repo}/issues?{parameter}",
    "ISSUECOMMENTS": "{api_endpoint}/repos/{github_org}/{github_repo}/issues/comments?{parameter}",
}
results = []


def get_data(endpoint, github_token):
    """Function get data"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {github_token}",
        }
        response = requests.get(endpoint, headers=headers)
        data = response.json()
        if response.status_code != 200:
            print(response.json())
            return None
        while "next" in response.links.keys():
            response = requests.get(response.links["next"]["url"], headers=headers)
            data.extend(response.json())
        return data

    except RequestException as err:
        print(err)
    return None


def get_values(item):
    """Function get values from result"""
    result_type = ""
    result_id = ""
    html_url = ""
    if "id" in item:
        result_id = item["id"]
    if "html_url" in item:
        html_url = item["html_url"]
        result_type = html_url.split("/")[5]
    return result_type, result_id, html_url


def check_body(item):
    """Function check body"""
    counter_hit = 0
    body = item["body"]
    if body is None:
        return counter_hit

    for url in re.findall(settings.URL_PATTERN, body, flags=0):
        idx = url.find(")")
        result_type, result_id, html_url = get_values(item)
        results.append([result_type, result_id, url[:idx], html_url])
        counter_hit = counter_hit + 1
    return counter_hit


def get_links(endpoint_type, github_org, github_repo, github_token):
    """Function start get links"""
    counter_all = 0
    counter_hit = 0
    parameter = "state=all&per_page=100"
    endpoint = endpoints[endpoint_type].format(
        api_endpoint=settings.API_ENDPOINT,
        github_org=github_org,
        github_repo=github_repo,
        parameter=parameter
    )
    data = get_data(endpoint, github_token)
    if data is None:
        return
    for item in data:
        counter_all = counter_all + 1
        link_in_body = check_body(item)
        counter_hit = counter_hit + link_in_body

    print(f"{endpoint_type}: {counter_hit} / {counter_all}")


def main():
    """Function main"""
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "o:r:t:h", ["organization=", "repo=", "token=", "help"]
        )
        print(args)
        for opt, arg in opts:
            if opt in ("-o", "--organization"):
                github_org = arg
            elif opt in ("-r", "--repo"):
                github_repo = arg
            elif opt in ("-t", "--token"):
                github_token = arg
            elif opt in ("-h", "--help"):
                print(USAGE_TEXT)
                print(OUTPUT_TEXT)
                sys.exit(2)

        get_links("ISSUES", github_org, github_repo, github_token)
        get_links("ISSUECOMMENTS", github_org, github_repo, github_token)

        now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{github_org}.{github_repo}.{now}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(results)

    except getopt.GetoptError as err:
        print(err)
        print(USAGE_TEXT)
        sys.exit(1)


if __name__ == "__main__":
    main()

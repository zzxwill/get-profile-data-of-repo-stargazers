"""
Script to get GitHub profile data of all Stargazers of a given GitHub repository
by Max Woolf (@minimaxir)
"""


import json
import csv
import time
import requests


def call_github_get_api(url, headers=None):
    response = requests.get(url=url, headers=headers)
    data = json.loads(response.text)
    return data


def retrieve_user_followers(user_name, access_token):
    query_url = "https://api.github.com/users/%s/followers?access_token=%s" % (user_name, access_token)
    data = call_github_get_api(query_url)

    follower_list = list()

    for follower in data:
        name = follower.get('login')
        follower_info = retrieve_user_profile(name)

        follower_list.append(follower_info)
    print(len(follower_list))


def retrieve_user_profile(user_name, access_token):
    user_info_url = "https://api.github.com/users/%s?access_token=%s" % (user_name, access_token)
    follower_info = call_github_get_api(user_info_url, None)

    return {
        'name': follower_info.get('login'),
        'id': follower_info.get('id'),
        'company': follower_info.get('company'),
        'location': follower_info.get('location')
    }


def retrieve_stargazers(file_name_prefix, repo, access_token):
    """
    This block of code creates a list of tuples in the form of (username, star_time)
    for the Statgazers, which will laterbe used to extract full GitHub profile data
    :param repo:
    :param access_token:
    :return:
    """

    page_number = 0
    list_stars = []
    stars_remaining = True

    f = open('%s.json' % file_name_prefix, 'w')
    f.write('[')

    while stars_remaining:
        try:
            print('page_number: %s' % page_number)
            query_url = "https://api.github.com/repos/%s/stargazers?page=%s&access_token=%s" % (repo, page_number,
                                                                                                access_token)
            headers = {'Accept': 'application/vnd.github.v3.star+json'}
            data = call_github_get_api(query_url, headers)

            for user in data:
                user_name = user['user']['login']

                user_info = {
                    'name': user_name,
                    'starred_at': user['starred_at']
                }

                list_stars.append(user_info)

                f.write(json.dumps(user_info))
                f.write(',\n')

            if len(data) < 25:
                stars_remaining = False

            page_number += 1
        except TypeError as type_error:
            data_message = data.get('message')
            if 'pagination is limited for this resource' in data_message:
                f.write(']')
                f.close()
                print(data_message)
            print(type_error)
        except Exception as e:
            print(e)


def write_data_in_csv(file_name_prefix):
    f = open('%s.json' % file_name_prefix)
    data_list = json.loads(f.read())

    stars = open('%s.csv' % file_name_prefix, 'w')
    fields = ["user_id", "user_name", "starred_at", "company", "location"]
    stars_writer = csv.writer(stars)
    stars_writer.writerow(fields)

    for user in data_list:
        user_name = user['name']
        user_info = retrieve_user_profile(user_name, developer_access_token)

        stars_writer.writerow([user_info.get('id'), user_name, user['starred_at'], user_info.get('company'),
                               user_info.get('location')])


if __name__ == '__main__':
    developer_access_token = '<Your Input>'
    repo = "996icu/996.ICU"

    process_started_time = time.strftime('%Y%m%d-%H%M%S', time.localtime())
    file_name_prefix = '%s_stargazers_%s' % (repo.split('/')[1], process_started_time)

    retrieve_stargazers(file_name_prefix, repo, developer_access_token)
    write_data_in_csv(file_name_prefix)

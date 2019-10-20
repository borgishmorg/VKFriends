import requests
import time

access_token = '36ac316d36ac316d36ac316d6136c12c67336ac36ac316d6b224d8a421245ecbb27a204'
v = '5.52'

friends_get = 'https://api.vk.com/method/friends.get'
users_get = 'https://api.vk.com/method/users.get'

my_tokens = [
    'a7289a14a7289a14a7289a14c1a745c7e1aa728a7289a14fa8878b91e72d76c1c0ff3ce',
    '36ac316d36ac316d36ac316d6136c12c67336ac36ac316d6b224d8a421245ecbb27a204',
    '10f86b3a10f86b3a10f86b3a88109536cd110f810f86b3a4d5889ced9fb7a49feba5810',
    '1956c0661956c0661956c06610193b9d9e119561956c06644f623635791b178a9d3f677',
    '2bf6be692bf6be692bf6be69cd2b9be39022bf62bf6be6976565d39f2a6a47c5de70f19',
    '2574f7752574f7752574f775032519aa8f225742574f77578d4142af54d86c6af3a67ef',
    '409e0e36409e0e36409e0e36c440f353ca4409e409e0e361d3eeda969726c79df4490dd',
    'e7fd8f75e7fd8f75e7fd8f7503e790d288ee7fde7fd8f75ba5d6b62587cb009e837cc60',
    '9826db3c9826db3c9826db3c06984b86c2998269826db3cc5863f06b4f6b89a4e51caa7',
    '1a9a41c21a9a41c21a9a41c25f1af71fc011a9a1a9a41c2473aa541ace47e8f4d5dd5c8',
    'da3ff98dda3ff98dda3ff98da1da52a789dda3fda3ff98d879f1c5296cc24a6c61066d0',
    '9aa4d95c9aa4d95c9aa4d95c9b9ac9875999aa49aa4d95cc7043caa7d2eab8d47f87531',
    'ad79a599ad79a599ad79a59953ad14fb9faad79ad79a599f0d9439a9bece77f1cf1f115'
]


class Token:

    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0

    def get(self):
        # self.idx = (self.idx + 1) % len(self.tokens)
        return self.tokens[self.idx]


token = Token(my_tokens)


def get_user_photo(user_id):
    """
        Return 200x200 px photo  of user with <user_id> id.
    """
    params = {
        'v': v,
        'user_id': user_id,
        'fields': 'photo_200'
    }
    time0 = time.clock()
    response_json = requests.get(users_get, params=dict(**params, access_token=token.get())).json()
    time1 = time.clock()
    print('response time', time1-time0)
    if 'error' in response_json:
        print(response_json)
        return ''
    print(response_json['response'])
    try:
        return response_json['response'][0]['photo_200']
    except KeyError:
        return 'http://cartravels.com/images/nophoto.jpg'


def get_user_fullname(user_id):
    """
        Return full photo photo  of user with <user_id> id.
    """
    params = {
        'v': v,
        'user_id': user_id
    }
    time0 = time.clock()
    response_json = requests.get(users_get, params=dict(**params, access_token=token.get())).json()
    time1 = time.clock()
    print('response time', time1-time0)
    if 'error' in response_json:
        print(response_json)
        return 'NULL'
    print(response_json['response'])
    try:
        return response_json['response'][0]['first_name'] + ' ' + response_json['response'][0]['last_name']
    except KeyError:
        return 'NULL'


def get_friend_ids_list(user_id):
    """
        Return list of friend ids of user with <user_id> id.
    """
    params = {
        'v': v,
        'user_id': user_id,
        'count': 10000
    }
    time0 = time.clock()
    response_json = requests.get(friends_get, params=dict(**params, access_token=token.get())).json()
    time1 = time.clock()
    print('response time', time1-time0)
    if 'error' in response_json:
        print(response_json)
        return []
    return response_json['response']['items']


def get_friends_path(user1, user2, req_limit=1800):
    left_set = set()
    right_set = set()

    left_queue = [user1]
    right_queue = [user2]

    left_parents = dict()
    right_parents = dict()

    key_user = 0
    path_found = False

    req_count = 0

    while left_queue or right_queue:
        req_count += 1
        if req_count > req_limit:
            raise RuntimeError("Requests limit error (count>{})".format(req_limit))
        print('Right queue len:', len(right_queue))
        if right_queue:
            user = right_queue.pop(0)
            friends = get_friend_ids_list(user)
            for friend in friends:
                if friend not in right_set:
                    right_set.add(friend)
                    right_parents[friend] = user
                    right_queue.append(friend)
                if friend in left_set:
                    key_user = friend
                    path_found = True
                    break
        if path_found:
            break

        print('Left queue len:', len(left_queue))
        req_count += 1
        if req_count > req_limit:
            raise RuntimeError("Requests limit error(count>{})".format(req_limit))
        if left_queue:
            user = left_queue.pop(0)
            friends = get_friend_ids_list(user)
            for friend in friends:
                if friend not in left_set:
                    left_set.add(friend)
                    left_parents[friend] = user
                    left_queue.append(friend)
                if friend in right_set:
                    key_user = friend
                    path_found = True
                    break
        if path_found:
            break

    path = []
    if path_found:
        path.append(key_user)
        user = key_user
        while user in left_parents:
            user = left_parents[user]
            path.append(user)
        path = path[::-1]
        user = key_user
        while user in right_parents:
            user = right_parents[user]
            path.append(user)

    return path

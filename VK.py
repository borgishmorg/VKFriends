import requests
import time
import threading

v = '5.52'

friends_get = 'https://api.vk.com/method/friends.get'
users_get = 'https://api.vk.com/method/users.get'

# write real tokens in my_token
my_tokens = [
    'TOKEN_EXAMPLE',
    'TOKEN_EXAMPLE1'
]


class Token:

    def __init__(self, tokens):
        self.tokens = tokens
        self.idx = 0
        self.lock = threading.Lock()

    def get(self):
        # self.idx = (self.idx + 1) % len(self.tokens)
        return self.tokens[self.idx]


token = Token(my_tokens)


def get_user_id(user):
    """
        Return id  of user with <user> ids/url.
        Or throw exception.
    """
    user_ids = str(user).split('/')[-1]
    params = {
        'v': v,
        'user_ids': user_ids
    }
    time0 = time.clock()
    response_json = requests.get(users_get, params=dict(**params, access_token=token.get())).json()
    time1 = time.clock()
    print('response time', time1-time0)
    if 'error' in response_json:
        print(response_json)
        raise RuntimeError("User {} isn't valid".format(user_ids))
    try:
        return response_json['response'][0]['id']
    except KeyError:
        raise RuntimeError("User {} isn't valid".format(user_ids))


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
    # print('response time', time1-time0)
    if 'error' in response_json:
        print(response_json)
        return []
    return response_json['response']['items']


class FriendGraph:
    def __init__(self, user1, user2, req_limit=10000):
        self.left_set = {user1}
        self.right_set = {user2}
        self.left_queue = [user1]
        self.right_queue = [user2]
        self.left_parents = dict()
        self.right_parents = dict()
        self.key_user = 0
        self.path_found = False
        self.req_count = 0
        self.req_limit = req_limit
        self.left_mutex = threading.Lock()
        self.right_mutex = threading.Lock()
        self.req_count_mutex = threading.Lock()

    def request_left_user(self):
        with self.left_mutex:
            if self.left_queue:
                with self.req_count_mutex:
                    self.req_count += 1
                    if self.req_count > self.req_limit:
                        raise RuntimeError("Requests limit error(count>{})".format(self.req_limit))
                return self.left_queue.pop(0)
            else:
                return -1

    def request_right_user(self):
        with self.right_mutex:
            if self.right_queue:
                with self.req_count_mutex:
                    self.req_count += 1
                    if self.req_count > self.req_limit:
                        raise RuntimeError("Requests limit error(count>{})".format(self.req_limit))
                return self.right_queue.pop(0)
            else:
                return -1


def left_compute(fg):
    while True:
        time.sleep(0.1)

        if fg.path_found:
            return
        try:
            user = fg.request_left_user()
        except RuntimeError as err:
            print(str(err))
            return
        if user == -1:
            continue

        friends = get_friend_ids_list(user)
        for friend in friends:
            with fg.left_mutex:
                if friend not in fg.left_set:
                    fg.left_set.add(friend)
                    fg.left_parents[friend] = user
                    fg.left_queue.append(friend)
            with fg.right_mutex:
                if friend in fg.right_set:
                    fg.key_user = friend
                    fg.path_found = True
                    return


def right_compute(fg):
    while True:
        time.sleep(0.1)

        if fg.path_found:
            return
        try:
            user = fg.request_right_user()
        except RuntimeError as err:
            print(str(err))
            return
        if user == -1:
            continue

        friends = get_friend_ids_list(user)
        for friend in friends:
            with fg.right_mutex:
                if friend not in fg.right_set:
                    fg.right_set.add(friend)
                    fg.right_parents[friend] = user
                    fg.right_queue.append(friend)
            with fg.left_mutex:
                if friend in fg.left_set:
                    fg.key_user = friend
                    fg.path_found = True
                    return


def get_friends_path(user1, user2):
    fg = FriendGraph(user1, user2)

    left_computes = [threading.Thread(target=left_compute, args=(fg,)) for _ in range(50)]
    right_computes = [threading.Thread(target=right_compute, args=(fg,)) for _ in range(50)]

    time0 = time.clock()
    for compute in left_computes:
        compute.start()
    for compute in right_computes:
        compute.start()

    for compute in left_computes:
        try: compute.join()
        except: pass
    for compute in right_computes:
        try: compute.join()
        except: pass
    time1 = time.clock()

    path = []
    if fg.path_found:
        path.append(fg.key_user)
        user = fg.key_user
        while user in fg.left_parents:
            user = fg.left_parents[user]
            path.append(user)
        path = path[::-1]
        user = fg.key_user
        while user in fg.right_parents:
            user = fg.right_parents[user]
            path.append(user)
    print('='*100)
    print('compute time', time1 - time0, 'sec')
    print('compute time per request', (time1 - time0)/fg.req_count, 'sec')
    print('request count', fg.req_count)
    return path

import atlastk as atlas
import VK

body = """
<body>
    <p style="text-align:center">Пользователь 1:<input id="user1" size="30" type="url" /></p>  
    <p style="text-align:center">Пользователь 2:<input id="user2" size="30" type="url" /></p>  
    <p style="text-align:center"><input data-xdh-onevent="compute" type="button" value="Найти путь" /></p>
</body>
"""

compute_body = """
<body>
    <p style="text-align:center">Ищем друзей</p>
</body>
"""

err_body = """
<body>
    <p style="text-align:center">{error}</p>
</body>
"""


def get_res_layout(path):
    res_body = '<body>'
    for user in path:
        res_body += '<p style="text-align:center"><img alt="" src="{}" style="height:200px; width:200px" /></p>'.format(VK.get_user_photo(user))
        res_body += '<p style="text-align:center"><a href="https://vk.com/id{}">{}</a></p>'.format(user, VK.get_user_fullname(user))
    res_body += '</body>'
    return res_body


def ac_connect(dom, id):
    dom.setLayout("", body)


def compute(dom, id):

    try:
        user1 = VK.get_user_id(dom.getContent('user1'))
        user2 = VK.get_user_id(dom.getContent('user2'))
    except RuntimeError as err:
        dom.alert(str(err))
        return

    if not VK.get_friend_ids_list(user1):
        dom.alert("{} don't have any friends :(".format(VK.get_user_fullname(user1)))
        return
    if not VK.get_friend_ids_list(user2):
        dom.alert("{} don't have any friends :(".format(VK.get_user_fullname(user2)))
        return

    dom.setLayout("", compute_body)
    try:
        path = VK.get_friends_path(user1, user2)
        print(' https://vk.com/id'.join(['', *map(str, path)]))
        dom.setLayout("", get_res_layout(path))
    except RuntimeError as err:
        dom.setLayout("", err_body.format(error=err))


callbacks = {
    "": ac_connect,
    "compute": compute,
}

atlas.launch(callbacks)

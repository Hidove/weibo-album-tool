import json
import os
import random
import re
import time

import requests

from common import print_error, print_info, print_success

if __name__ != '__main__':
    exit()
# 新浪用户的uid
UID_LIST = [
    1809054937,
]
# 你的新浪账号cookie
COOKIE = ''
# 链接格式可用变量{pic_id}
PIC_FORMAT = 'https://tva1.sinaimg.cn/large/{pic_id}.jpg'
# 是否启用aria2
ARIA2_ENABLE = False
# aria2文件保存路径
ARIA2_PATH = '/www/wwwroot/download.com/file/'
# aria2 token
ARIA2_TOKEN = ''
# aria2 jsonrpc地址
ARIA2_JSONRPC = 'http://xxx.com:6800/jsonrpc'

headers = {
    'cookie': COOKIE
}

def get_albums(uid):
    page = 1
    count = 100
    temp_url = 'https://photo.weibo.com/albums/get_all?uid={uid}&page={page}&count={count}&__rnd={time}'
    url = temp_url.format(
        uid=uid,
        count=count,
        page=page,
        time=time.time(),
    )
    requests_get = requests.get(url, headers=headers)
    try:
        return requests_get.json()['data']['album_list']
    except Exception as e:
        print_error('登录信息无效，请更新！')
        raise Exception(e)


def save_album(pic_list, username, album):
    filepath = os.getcwd() + '/pic_list/{username}/{caption}.txt'.format(
        username=username,
        caption=album['caption'],
    )
    path_dirname = os.path.dirname(filepath)
    if not os.path.exists(path_dirname):
        os.makedirs(path_dirname)
    content = '\n'.join(pic_list)
    with open(filepath, 'w')as f:
        f.write(content)
        f.flush()


def notice_aria2(pic_list, username, caption):
    if len(pic_list) <= 0:
        return
    path = ARIA2_PATH.rstrip('/') + '/{username}/{caption}/'.format(username=username, caption=caption)
    for pic in pic_list:
        data = {
            "jsonrpc": "2.0",
            "method": "aria2.addUri",
            "id": "lixiaoen",
            "params": [
                "token:%s" % ARIA2_TOKEN,
                [
                    pic
                ]
                ,
                {
                    "dir": path
                }
            ]
        }
        requests.post(ARIA2_JSONRPC, data=json.dumps(data))
    print_success('发送下载任务带aria2服务器成功')


def get_album_pic(uid, album, username):
    global photo_list
    print_info('开始获取相册【{album_id}】'.format(album_id=album['album_id']))
    page = 1
    count = 100
    pic_list = []

    while True:
        print_info('正在获取第{page}页'.format(page=page))
        temp_url = 'https://photo.weibo.com/photos/get_all?uid={uid}&album_id={album_id}&count={count}&page={page}&type={type}&__rnd={time}'
        url = temp_url.format(
            uid=uid,
            album_id=album['album_id'],
            count=count,
            page=page,
            type=album['type'],
            time=time.time(),
        )
        requests_get = requests.get(url, headers=headers)
        try:
            photo_list = requests_get.json()['data']['photo_list']
        except Exception as e:
            print_error('登录信息无效，请更新！')
            raise Exception(e)
        if len(photo_list) <= 0:
            break
        for photo in photo_list:
            pic_url = (PIC_FORMAT).format(pic_id=photo['pic_pid'])
            pic_list.append(pic_url)
        print_success('第{page}页获取完毕，共{count}条'.format(page=page, count=len(photo_list)))
        page += 1

    print_success('相册【{album_id}】获取完毕'.format(album_id=album['album_id']))
    # 保存
    save_album(pic_list, username, album)
    # 通知aria2
    if ARIA2_ENABLE:
        notice_aria2(pic_list, username, album['caption'])


def get_username(uid):
    try:
        requests_get = requests.get('https://photo.weibo.com/%s/albums?rd=1' % uid, headers=headers)
    except:
        return get_username(uid)
    try:
        get_text = requests_get.text
        username = re.findall(r"<title>(.+?)的专辑\s-\s微相册<\/title>", get_text)[0]
        return username
    except Exception as e:
        print_error('登录信息无效，请更新！')
        raise Exception(e)


for uid in UID_LIST:
    username = get_username(uid)
    print_info('正在获取用户【{uid}】的相册'.format(uid=uid))
    album_list = get_albums(uid)
    print_success('获取用户【{uid}】的相册成功'.format(uid=uid))
    for album in album_list:
        get_album_pic(uid, album, username)

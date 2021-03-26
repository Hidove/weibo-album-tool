import os
import time

import requests

if __name__ != '__main__':
    exit()
# 新浪用户的uid
uid = 1947117325
# 相册id
album_id_list = [
    189229,
    3558779514364152,
]
# 你的新浪账号cookie
cookie = 'cookie'
# 链接格式可用变量{pic_id}
pic_format = 'https://tva1.sinaimg.cn/large/{pic_id}.jpg'

headers = {
    'cookie': cookie
}

def save_album(pic_list, album_id):
    filepath = os.getcwd() + '/pic_list/album_{album_id}.txt'.format(album_id=album_id)
    dirname = os.path.dirname(filepath)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    content = '\n'.join(pic_list)
    with open(filepath, 'w')as f:
        f.write(content)
        f.flush()


def get_album_pic(album_id):
    global photo_list
    print('开始获取相册【{album_id}】'.format(album_id=album_id))
    page = 1
    count = 100
    pic_list = []

    while True:
        print('正在获取第{page}页'.format(page=page))
        temp_url = 'https://photo.weibo.com/photos/get_all?uid={uid}&album_id={album_id}&count={count}&page={page}&type=3&__rnd={time}'
        url = temp_url.format(
            uid=uid,
            album_id=album_id,
            count=count,
            page=page,
            time=time.time(),
        )
        requests_get = requests.get(url, headers=headers)
        try:
            photo_list = requests_get.json()['data']['photo_list']
        except:
            print('登录信息无效，请更新！')
            exit()
        if len(photo_list) <= 0:
            break
        for photo in photo_list:
            pic_url = (pic_format).format(pic_id=photo['pic_pid'])
            pic_list.append(pic_url)
        print('第{page}页获取完毕，共{count}条'.format(page=page, count=len(photo_list)))
        page += 1

    print('相册【{album_id}】获取完毕'.format(album_id=album_id))
    save_album(pic_list, album_id)


for album_id in album_id_list:
    get_album_pic(album_id)

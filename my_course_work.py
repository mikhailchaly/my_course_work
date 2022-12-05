import datetime
import time
import json
import requests
import random
from tqdm import tqdm
from pprint import pprint

list_like_date_url_photo = []
dict_photo = {}
name_date_list = []
list_info_photos = []


class VkUser():
    token_vk = input('Введите токен vk\n')
    #with open('my_token_vk.txt', 'r') as file:
        #token_vk = file.read().strip()
    url = 'https://api.vk.com/method/'


    def __init__(self, token_vk, version):
        self.params = {
            'access_token': token_vk,
            'v': version}

    def get_photos(self):
        group_photos_get = self.url + 'photos.get'
        photos_get_params = {
            'owner_id': '9419101',
            'album_id': 'profile',
            'extended': '1'}
        result = requests.get(group_photos_get, params={**self.params, **photos_get_params})
        #pprint(result.json())

        for element in result.json()["response"]["items"]:
            likes = element["likes"]["count"]
            date = datetime.datetime.fromtimestamp(element["date"]).strftime("%Y_%m_%d_%H_%M_%S")
            if likes not in name_date_list:
                name = f"{likes}"
                name_date_list.append(likes)
            else:
                name = f"{likes}_{date}"
                name_date_list.append(likes)
            for elem in element.get('sizes'):
                if elem.get("type") == "w":
                    url_photo = elem["url"]
                    dict_photo = {"name": name, "url": url_photo}
            list_like_date_url_photo.append(dict_photo)


        # Сохраним данные по сохранненым фотографиям на yandex_disk - в файл .json
        for element in result.json()["response"]["items"]:
            for elem in element.get('sizes'):
                if elem.get("type") != "w":
                    elem.clear()
            list_info_photos.append(element)
        with open("photos_in_yandex_disk.json", "w") as file:
            json.dump(list_info_photos, file, ensure_ascii=False, indent=2)


class Yandex():
    print()
    token_yandex = input('Введите токен yandex_disk\n(id пользователя vk введите в метод get_photos)\n')
    #with open('my_token_yandex.txt', 'r') as file:
        #token_yandex = file.read().strip()
    base_host = 'https://cloud-api.yandex.net'

    def __init__(self, token):
        self.token = Yandex.token_yandex

    def get_headers(self):
        return {
            'Content-Type': "application/json",
            'Authorization': f'OAuth {self.token_yandex}'
        }

    def _get_upload_link(self, path):
        uri = '/v1/disk/resources/upload/'
        request_url = self.base_host + uri
        params = {'path': path, 'overwrite': True}
        response = requests.get(request_url, headers=self.get_headers(), params=params)
        return response.json()["href"]

    def add_directory(self, path):
        uri = '/v1/disk/resources/'
        request_url = self.base_host + uri
        params = {'path': path}
        response = requests.put(request_url, headers=self.get_headers(), params=params)
        return response.json()

    def upload_to_disk(self, local_path, yandex_path):
        upload_url = self._get_upload_link(yandex_path)
        response = requests.put(upload_url, data = open(local_path, 'rb'), headers=self.get_headers())


    def upload_from_internet(self):
        uri = '/v1/disk/resources/upload/'
        request_url = self.base_host + uri

        #сохраним фото на яндекс диск с использованием прогресс-бар для отслеживания процесса программы
        print()
        print("резервное копирование фотографий....")
        for element in tqdm(list_like_date_url_photo, colour='green', ncols=100):
            time.sleep(random.uniform(0.2, 1))
            params = {'url': element['url'], 'path': f'photo_archive_vk/{element["name"]}'}
            response = requests.post(request_url, params=params, headers=self.get_headers())
        print("копирование успешно завершено")
        #pprint(list_like_date_url_photo)


vk_client = VkUser(VkUser.token_vk, "5.131")
vk_client.get_photos()

ya = Yandex(Yandex.token_yandex)
ya.add_directory('photo_archive_vk')
ya.upload_to_disk('requirements.txt', '/photo_archive_vk/requiremеnts.txt')
ya.upload_from_internet()








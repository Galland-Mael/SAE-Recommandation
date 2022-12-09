from urllib.request import urlopen, Request
import json
# add async await
import asyncio
# add thread
import threading


url = "https://qghub.cloud/assets/yelp_business.json"

req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})


# class to read json from url in stream
class StreamJson:
    def __init__(self, url):
        # with fake user agent
        self.stream = urlopen(url)
        self.decoder = json.JSONDecoder()

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            try:
                return self.decoder.raw_decode(self.stream.readline().decode())[0]
            except ValueError:
                continue

# def split_string(string):
#     # Split the string based on space delimiter
#     list_string = string.split(',')
#
#     return list_string
#
# verif=0
# for obj in StreamJson(req):
#     check=False
#     verif += 1
#     categories = obj.get('categories')
#     city = obj.get('city')
#     liste = split_string(categories)
#     size = len(liste)
#     if city.lower() == "indianapolis" and categories is not None:
#         for i in range(size):
#             if i != 0:  # test pour suppression de l'espace devant la chaine
#                 alias = liste[i][1:]
#                 liste[i] = alias
#             else:
#                 alias = liste[i]
#             if alias.lower() == "restaurants":
#                 check = True
#
#         if check == True:
#             liste.remove('Restaurants')
#             try:
#                 liste.remove('Food')
#             except:
#                 print('no food')
#             print(type(liste))
#             size = len(liste)
#             for j in range(size):
#                 if j != 0:  # test pour suppression de l'espace devant la chaine
#                     print(liste[j] + ' ' + str(j))
#     verif += 1
#     if verif==400:
#         exit()
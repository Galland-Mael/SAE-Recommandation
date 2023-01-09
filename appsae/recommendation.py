from surprise import KNNBasic
from surprise import Dataset
from surprise import Reader
from django.conf import settings

from collections import defaultdict
from operator import itemgetter
import heapq

import os
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "appsae.settings")

import django
django.setup()


def load_dataset():
    file = str(settings.BASE_DIR) + '/' + "ratingsmovies.csv"
    reader = Reader(line_format='user item rating timestamp', sep=',', skip_lines=1)
    ratings_dataset = Dataset.load_from_file(file, reader=reader)

    # Lookup a movie's name with it's Movielens ID as key
    restaurantID_to_name = {}
    file = str(settings.BASE_DIR) + '/' + "movies.csv"
    with open(file, newline='', encoding='ISO-8859-1') as csvfile:
            restaurant_reader = csv.reader(csvfile)
            next(restaurant_reader)
            for row in restaurant_reader:
                restaurantID = int(row[0])
                restaurant_name = row[1]
                restaurantID_to_name[restaurantID] = restaurant_name
    # Return both the dataset and lookup dict in tuple
    return (ratings_dataset, restaurantID_to_name)


def getRestaurantName(RestaurantID,restaurantID_to_name):
  if int(RestaurantID) in restaurantID_to_name:
    return restaurantID_to_name[int(RestaurantID)]
  else:
      return ""



def finalRecommendation():
    dataset, restaurantID_to_name = load_dataset()

    # Build a full Surprise training set from dataset
    trainset = dataset.build_full_trainset()

    similarity_matrix = KNNBasic(sim_options={
            'name': 'cosine',
            'user_based': False
            })\
            .fit(trainset)\
            .compute_similarities()

    test_subject = '12'

    k = 5

    test_subject_iid = trainset.to_inner_uid(test_subject)
    test_subject_ratings = trainset.ur[test_subject_iid]
    k_neighbors = heapq.nlargest(k, test_subject_ratings, key=lambda t: t[1])

    candidates = defaultdict(float)

    for itemID, rating in k_neighbors:
        try:
          similaritities = similarity_matrix[itemID]
          for innerID, score in enumerate(similaritities):
              candidates[innerID] += score * (rating / 5.0)
        except:
          continue

    visited = {}
    for itemID, rating in trainset.ur[test_subject_iid]:
      visited[itemID] = 1
      recommendations = []

      position = 0
      for itemID, rating_sum in sorted(candidates.items(), key=itemgetter(1), reverse=True):
          if not itemID in visited:
              recommendations.append(getRestaurantName(trainset.to_raw_iid(itemID),restaurantID_to_name))
              position += 1
              if (position > 10): break  # We only want top 10

      for rec in recommendations:
          print("Restaurant: ", rec)


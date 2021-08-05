#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
artist-recommender.py: 
	Recommends various artists based on a user's Spotify listening history.
Creates a playlist of songs from said artists.
"""

__author__ = "Aidan Fadool"
__copyright__ = "Copyright 2021, Shaky Dev Projects"
__credits__ = ["Aidan Fadool"]

__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Aidan Fadool"
__email__ = "fadooljo@msu.edu"
__status__ = "Production"

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from credentials import client_id, client_secret
import pprint
import math
import time

# Recommendation weights
w_top_artist = 0.8 	# Higher weight = lower recommending power with each descending 'top artist'
w_rec_artist = 0.3  # Higher weight = lower recommending power with each descending 'recommended artist'
top_artist_depth = 20 # How many of your top artists are taken into consideration
time_range = 'medium_term' # How far back in time your music taste is accounted for
						   # Options: short_term, medium_term, long_term

# Establish authorization arguments
redirect_uri = 'https://example.com/callback'
scope = 'user-library-read user-top-read playlist-modify-public'

pp = pprint.PrettyPrinter(depth=8) # Establishing pretty print

# Connect to spotify API (first build has to be in terminal)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri,
                                               scope=scope))

# Fetch the user's top listened artists
top_artists = sp.current_user_top_artists(limit=top_artist_depth, offset=0, time_range=time_range)
top_artist_ids = [x['id'] for x in top_artists['items']]

# Create a list of similar artists
new_artist_rankings = {} # 'key': artist_id, 'item': recommending power

# Parse the list of top listened artists
for i in range(len(top_artist_ids)):
	weight_1 = (len(top_artist_ids) - i*w_top_artist) / (len(top_artist_ids)) # Artist recommendations hold
															   # less weight as the list goes on
	# Create a list of similar artists
	similar_artists = sp.artist_related_artists(top_artist_ids[i])
	# pp.pprint(similar_artists)
	similar_artist_ids = [x['id'] for x in similar_artists['artists']]

	# Parse the list of top recommended artists
	for i in range(len(similar_artist_ids)):
		weight_2 = (len(similar_artist_ids) - i*w_rec_artist) / (len(similar_artist_ids)) # Artist recommendations hold
															   		 # less weight as the list goes on
		# Check if artists has been recommended already
		if ((similar_artist_ids[i]) in new_artist_rankings):
			new_artist_rankings[similar_artist_ids[i]] += weight_1 * weight_2;
		else:
			# Add the artist to the list of recommended artists
			new_artist_rankings[similar_artist_ids[i]] = weight_1 * weight_2;

	print("%s artists found for you so far..." % len(new_artist_rankings))

# Create a list of ids from results
new_artist_ids = list(new_artist_rankings.keys())
new_artist_values = list(new_artist_rankings.values())

# Break up the artist ids into batches for requesting
num_ids = len(new_artist_ids)
batch_size = 15 # Number of artist ids per request (sp.artists() has a limit on artist requests)

# Create an empty nested list (each nested list is one batch)
new_artist_ids_batches = [[] for _ in range(math.ceil(num_ids / batch_size))]

for i in range(num_ids):
	# Append current id to batched list
	new_artist_ids_batches[math.floor(i / batch_size)].append(new_artist_ids[i])
						  # calculates which nested list the next id should be
						  # added to to obey batch sizes

new_artist_names = [] # Empty list of names

# Iterate through list of batches 
for batch in new_artist_ids_batches:
	artist_info = sp.artists(batch)
	# Parse the info for names
	for artist in artist_info['artists']:
		new_artist_names.append(artist['name'])

	print("Requesting artist names...%0.2f%%" % (len(new_artist_names) / (batch_size*len(new_artist_ids_batches))*100))
print("Artist names found!")

# Create a new dict for named artists
named_artists = {}
for i in range(len(new_artist_names)):
	named_artists[new_artist_names[i]] = new_artist_values[i]

# Sort the named artists by their recommending power
print("Sorting artists...")
sort_named_rankings = sorted(named_artists.items(), key=lambda x: x[1], reverse=True)

pp.pprint(sort_named_rankings)

# TODO: Generate a playlist of songs from new artists


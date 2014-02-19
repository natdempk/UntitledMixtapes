import pylast
import random
import threading
import Queue
import time
from pyechonest import config as echoconfig
from pyechonest import artist, song
import config
import math

echoconfig.ECHO_NEST_API_KEY = config.ECHO_NEST_API_KEY

class echoArtistThread(threading.Thread):
    def __init__(self, queue, artist_list, song_max):
        threading.Thread.__init__(self)
        self.queue = queue
        self.artist_list = artist_list
        self.song_max = song_max-4

    def run(self):
        try:
            a = self.queue.get()
            ar = artist.Artist(a)
            l = ar.get_songs(results=5)
            self.artist_list.append({'artist':ar,'songs':l})
        finally:
            self.queue.task_done()
            return


def get_artist_num(song_max):
	if song_max == 12:
		return 10
	elif song_max == 14:
		return 8
	else:
		return 13

def do_everything(artist_name="Anamanaguchi", song_name="Endless Fantasy", song_max=8, diversity=0):

    start_time = time.time()
    similar_artist_num = get_artist_num(song_max)
    if diversity:
        similar_artist_num /= 2

    song_max -= 2

    # connect to last.fm
    network = pylast.LastFMNetwork(api_key = config.LAST_FM_API_KEY, 
                                   api_secret = config.LAST_FM_API_SECRET,
                                   username= config.LAST_FM_USERNAME,
                                   password_hash = config.LAST_FM_PASSWORD_HASH)

    artistgrab = network.get_artist(artist_name) # get artist name from last.fm
    similar = artistgrab.get_similar()[0:similar_artist_num] # get similar artists

    similar_artists = []
    # get a specified number of similar artists
    [similar_artists.append(similar[i][0].get_name()) for i in range(len(similar)) if not '&' in similar[i][0].get_name()]

    similar_artist_num = len(similar_artists)

    if diversity: # get more kinda similar artists to mix in
        k_artistgrab = network.get_artist(similar_artists[0]) # doubt we need this line
        k_similar = k_artistgrab.get_similar()
        last = len(k_similar)
        k_similar_artists = []
        index = 0
        while len(k_similar_artists) < len(similar_artists):
            if index < last:
                if not k_similar[index][0].get_name() in similar_artists and k_similar[index][0].get_name() != artist_name:
                    k_similar_artists.append(k_similar[index][0].get_name())
                index += 1
            else:
                break

        k_similar_artist_num = len(k_similar_artists)
    # audio summary bucket gets detailed track info, spotify-ww gets some spotify info
    # and tracks gets track-specific spotify info
    buckets = ['audio_summary', 'id:spotify-WW', 'tracks'] # setup buckets for requests
    # get user entered song from echonest
    the_song = song.search(title=song_name, artist=artist_name, buckets=buckets)[0]
    the_song_info = the_song.audio_summary

    sim_songs = [] # similar songs
    k_sim_songs = [] # kinda similar songs

    a_queue = Queue.Queue()
    a_list = []

    # add similar artists to queue
    for a in similar_artists:
        a_queue.put(a)

    # get echonest artists + songs
    for i in range(similar_artist_num):
        t = echoArtistThread(a_queue, a_list, song_max)
        t.setDaemon(True)
        t.start()

    a_queue.join() # wait for all threads to finish
    # add found soungs to list
    [sim_songs.extend(a['songs'][0:6]) for a in a_list if a['songs']]

    if diversity: # make a second queue and look up second set of artists
        # TODO: make this part of first queue by setting artist types
        k_queue = Queue.Queue()
        k_list = []
        for a in k_similar_artists:
            k_queue.put(a)

        for i in range(k_similar_artist_num):
            t = echoArtistThread(k_queue, k_list, song_max)
            t.setDaemon(True)
            t.start()

        k_queue.join()
        # if we found songs add them to our song list
        [k_sim_songs.extend(a['songs'][0:6]) for a in k_list if a]

    the_artist = artist.Artist(artist_name) # get user's artist
    artist_songs = the_artist.get_songs()[:10] # get artist songs
    artist_songs_ids = [s.id for s in artist_songs] # get ids for artist songs
    artist_songs = song.profile(artist_songs_ids, buckets=buckets) # get spotify IDs and info
    # sort songs by energy similarity
    the_songs = sorted(artist_songs, key=lambda k: abs(the_song_info[u'energy']-k.audio_summary[u'energy']))

    # TODO(natdempk): have zack explain what this does to me
    seen = set()
    seen_add = seen.add
    the_songs = [ x for x in the_songs if x not in seen and not seen_add(x)]

    n = 1
    tflag = True

    # filter to only songs that have spotify IDs
    the_songs = [s for s in the_songs if 'tracks' in s.cache]

    #first_song_id = the_songs[0].cache['tracks'][0]['foreign_id'] # set first
    #last_song_id  = the_songs[1].cache['tracks'][0]['foreign_id'] # and last songs

    while tflag == True:
        tflag = False
        try:
            first_song_id = the_songs[n].cache['tracks'][0]['foreign_id']
        except:
            tflag = True
            n += 1


    try:
        last_song_id = the_song.cache['tracks'][0]['foreign_id']
    except:
        n += 1
        tflag = True
        while tflag == True:
            tflag = False
            try:
                last_song_id = the_songs[n].cache['tracks'][0]['foreign_id']
            except:
                tflag = True
                n += 1

    seen = set()
    seen_add = seen.add
    sim_songs = [ x for x in sim_songs if x not in seen and not seen_add(x)]

    sim_songs_info = []

    i = 0
    while i < len(sim_songs):
        sim_songs_info += song.profile(map(lambda k: sim_songs[k].id, range(i, min(i+9, len(sim_songs)-1))), buckets=buckets)
        i += 9


    # filter to songs with similar energy
    sim_songs_info = filter(lambda k: k.audio_summary[u'energy'] < the_song_info[u'energy']+.3 and
    				      k.audio_summary[u'energy'] > the_song_info[u'energy']-.3, sim_songs_info)
    
    # sort songs by tempo
    sim_songs_info = sorted(sim_songs_info, key=lambda k: k.audio_summary[u'tempo'])

    # divide into slower and faster songs
    slow_songs = sorted(sim_songs_info[:len(sim_songs)/2],
                        key=lambda k: k.audio_summary[u'duration'])
    fast_songs = sorted(sim_songs_info[len(sim_songs)/2:],
                        key=lambda k: k.audio_summary[u'duration'])
    
    # do the same for diversity songs
    if diversity:
        k_seen = set()
        k_seen_add = k_seen.add
        k_sim_songs = [x for x in k_sim_songs if x not in seen and not k_seen_add(x)]

        k_sim_songs_info = []

        i = 0
        while i < len(k_sim_songs):
            k_sim_songs_info += song.profile(map(lambda k: k_sim_songs[k].id, range(i, min(i+9, len(k_sim_songs)-1))), buckets=buckets)
            i += 9

        # filter to songs with similar energy
        k_sim_songs_info = filter(lambda k: k.audio_summary[u'energy'] < the_song_info[u'energy']+.3 and
                              k.audio_summary[u'energy'] > the_song_info[u'energy']-.3, k_sim_songs_info)

        # sort songs by tempo
        k_sim_songs_info = sorted(k_sim_songs_info, key=lambda k: k.audio_summary[u'tempo'])

        # divide into slower and faster songs
        k_slow_songs = sorted(k_sim_songs_info[:len(k_sim_songs_info)/2],
                            key=lambda k: k.audio_summary[u'duration'])
        k_fast_songs = sorted(k_sim_songs_info[len(k_sim_songs_info)/2:],
                            key=lambda k: k.audio_summary[u'duration'])


    total_info = []
    counter = 0


    if diversity: # select songs from 4 lists
        lists = [fast_songs, slow_songs, k_fast_songs, k_slow_songs]
        for i in range(song_max):
            cur_list = lists[i%4]
            flag = True
            while flag == True:
                flag = False
                info = cur_list[random.randint(0, len(cur_list)-1)]
                for j in range(len(total_info)):
                    try:
                        if info.artist_name == total_info[j].artist_name:
                            counter += 1
                            if counter < 100:
                                flag = True
                    except:
                        counter += 1
                        if counter < 100:
                            flag = True
            total_info.append(info)
    else: # select songs from just two lists
        # TODO make a conditional that sets lists and merge these two pieces of code
        for i in range(song_max/2):
            flag = True
            while flag == True:
                flag = False
                info = fast_songs[random.randint(0, len(fast_songs)-1)]
                for j in range(len(total_info)):
                    if info.artist_name == total_info[j].artist_name:
                        counter += 1
                        if counter < 100:
                            flag = True
            total_info.append(info)
            flag = True
            while flag == True:
                flag = False
                info = slow_songs[random.randint(0, len(slow_songs)-1)]
                for j in range(len(total_info)):
                    if info.artist_name == total_info[j].artist_name:
                        counter += 1
                        if counter < 100:
                            flag = True
            total_info.append(info)

    total_res = []
    total_res.append(first_song_id) 
    final_ids = [t.id for t in total_info]

    print total_info

    for t in total_info:
        try:
            if 'tracks' in s.cache:
                total_res.append(t.cache['tracks'][0]['foreign_id'])
        except:
            pass

    total_res.append(last_song_id)

    seen = set()
    seen_add = seen.add
    total_res = [ x for x in total_res if x not in seen and not seen_add(x)]

    return total_res

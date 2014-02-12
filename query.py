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
    def __init__(self, queue, artist_list):
        threading.Thread.__init__(self)
        self.queue = queue
        self.artist_list = artist_list

    def run(self):
        while True:
            try:
                a = self.queue.get()
                ar = artist.Artist(a)
                l = ar.get_songs()
                self.artist_list.append({'artist':ar,'songs':l})
            finally:
                self.queue.task_done()

class echoThread(threading.Thread):
    def __init__(self, queue, songs_list):
        threading.Thread.__init__(self)
        self.queue = queue
        self.songs_list = songs_list

    def run(self):
        while True:
            try:
                s = self.queue.get() # get artist from queue
                self.songs_list += song.profile(s, buckets=['audio_summary'])
            finally:
                self.queue.task_done()

            #the_artist = artist.Artist(a)
            #songs = the_artist.get_songs()[:num_songs]
            #artist_list.append({'artist':})


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
        k_artistgrab = network.get_artist(similar_artists[0])
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

        #[k_similar_artists.append(k_similar[i][0].get_name()) for i in range(len(similar))]
        k_similar_artist_num = len(k_similar_artists)

    #for i in range(similar_artist_num):    print time.time() - start_time

    #    if i < len(similar):
    #        similar_artists.append(similar[i][0].get_name())
    #    else:
    #        similar_artist_num = len(similar_artists)
    #        break

    the_song = song.search(title=song_name, artist=artist_name)[0] # get requested song
    the_song_info = the_song.get_audio_summary() # get echonest song info

    sim_songs = []
    k_sim_songs = []

    a_queue = Queue.Queue()
    a_list = []

    for a in similar_artists:
        a_queue.put(a)

    for i in range(similar_artist_num):
        t = echoArtistThread(a_queue, a_list)
        t.setDaemon(True)
        t.start()

    a_queue.join()

    for a in a_list:
        l = a['songs']
        if l:
            sim_songs = sim_songs + l[0:song_max]

    if diversity:
        k_queue = Queue.Queue()
        k_list = []
        for a in k_similar_artists:
            k_queue.put(a)

        for i in range(k_similar_artist_num):
            t = echoArtistThread(k_queue, k_list)
            t.setDaemon(True)
            t.start()

        k_queue.join()

        for a in k_list:
            l = a['songs']
            if l:
                k_sim_songs = k_sim_songs + l[0:song_max]

    the_artist = artist.Artist(artist_name)
    the_songs = sorted(the_artist.get_songs()[:10], key=lambda k: the_song_info[u'energy']-k.get_audio_summary()[u'energy'])
    seen = set()
    seen_add = seen.add
    the_songs = [ x for x in the_songs if x not in seen and not seen_add(x)]

    n = 1
    tflag = True

    while tflag == True:
        tflag = False
        try:
            first_id = the_songs[n].get_tracks("spotify-WW")[0][u'foreign_id']
        except:
            tflag = True
            n += 1


    #when we found info about the first song but its not on spotify
    try:
        new_first_track_id = the_song.get_tracks("spotify-WW")[0][u'foreign_id']
    except:
        n += 1
        tflag = True
        while tflag == True:
            tflag = False
            try:
                new_first_track_id = the_songs[n].get_tracks("spotify-WW")[0][u'foreign_id']
            except:
                tflag = True
                n += 1

    seen = set()
    seen_add = seen.add
    sim_songs = [ x for x in sim_songs if x not in seen and not seen_add(x)]

    sim_songs_info = []

    queue = Queue.Queue()

    i = 0
    while i < len(sim_songs): # add songs to queue
        queue.put(map(lambda k: sim_songs[k].id, range(i, min(i+9, len(sim_songs)-1))))
        i += 9
    
    for r in range(int(math.ceil(len(sim_songs)/9))): # create threads
       t = echoThread(queue, sim_songs_info)
       t.setDaemon(True)
       t.start()
    
    queue.join() # wait for queue to be processed

    #for i in range(len(sim_songs)): # create song handles
    #    sim_songs_info[i]['song_handle'] = sim_songs[i]


    # filter to songs with similar energy
    sim_songs_info = filter(lambda k: k.audio_summary[u'energy'] < the_song_info[u'energy']+.2 and
    				      k.audio_summary[u'energy'] > the_song_info[u'energy']-.2, sim_songs_info)

    # sort songs by tempo
    sim_songs_info = sorted(sim_songs_info, key=lambda k: k.audio_summary[u'tempo'])

    # divide into slower and faster songs
    slow_songs = sorted(sim_songs_info[:len(sim_songs_info)/2],
                        key=lambda k: k.audio_summary[u'duration'])
    fast_songs = sorted(sim_songs_info[len(sim_songs_info)/2:],
                        key=lambda k: k.audio_summary[u'duration'])

    # do the same for
    if diversity:
        k_seen = set()
        k_seen_add = k_seen.add
        k_sim_songs = [x for x in k_sim_songs if x not in seen and not k_seen_add(x)]

        k_sim_songs_info = []

        queue = Queue.Queue()

        i = 0
        while i < len(k_sim_songs): # add songs to queue
            queue.put(map(lambda k: k_sim_songs[k].id, range(i, min(i+9, len(k_sim_songs)-1))))
            i += 9
    
        for r in range(int(math.ceil(len(k_sim_songs)/9))): # create threads
            t = echoThread(queue, k_sim_songs_info)
            t.setDaemon(True)
            t.start()
    
        queue.join() # wait for queue to be processed

        #for i in range(len(sim_songs)): # create song handles
        #    k_sim_songs_info[i]['song_handle'] = k_sim_songs[i]

        '''for i in range(len(k_sim_songs)):
            k_sim_songs_info.append(k_sim_songs[i].get_audio_summary())
            k_sim_songs_info[i]['song_handle'] = k_sim_songs[i]'''

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


    if diversity:
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
    else:
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

    #total_res = [[first_song.title, artist_name]]

    #for i in range(len(total_info)):
    #	try:
    #        total_res.append([total_info[i]['song_handle'].title,
    #                      total_info[i]['song_handle'].artist_name])
    #    except:
    #    	pass

    #total_res.append([second_song.title, artist_name])

    total_res = []

    total_res.append(new_first_track_id)


    for i in range(len(total_info)):
    	try:
        	total_res.append(total_info[i].get_tracks("spotify-WW")[0][u'foreign_id'])
        except:
            print total_info[i].title + " not found"
            pass

    total_res.append(first_id)

    seen = set()
    seen_add = seen.add
    total_res = [ x for x in total_res if x not in seen and not seen_add(x)]

    return total_res

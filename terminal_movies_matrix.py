"""
Watch movies in your terminal with this handy video-to-ascii converter.

Note that characters are actually mirrored in the matrix.

Play movie like so:
>>>python3 terminal_movies_matrix.py path/to/movie
"""
import argparse
import curses
import random
import time
import cv2
from ffpyplayer.player import MediaPlayer

class CodeRain:
    row = 0
    timer = 12 #Seconds to fall to bottom

    def __init__(self):
        self.column = random.random()
        self.started = time.time()

    def update(self):
        now = time.time() - self.started
        self.row = now / self.timer

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to movie")
args = parser.parse_args()
path = args.path

ascii_map = dict(enumerate(' .ｰ*:+ﾆﾍｺ7ﾘﾒﾊ1ﾜｴｽﾑﾇｵｻ2ｾZI54ｶ08'))
scale = 255/len(ascii_map) + .05  # Add a small amount to prevent key errors

def main(screen):
    init_curses(screen)

    movie = cv2.VideoCapture(path)
    audio = MediaPlayer(path)
    rain = []
    running = read_flag = True

    while read_flag and running:
        audio.get_frame()
        read_flag, frame = movie.read()

        height, width = screen.getmaxyx()

        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(grayscale, (width, height))

        for row_num, row in enumerate(resized):
            screen.addstr(row_num, 0,
                          ''.join(ascii_map[int(color/scale)] for color in row[:-1]))

        # code rain updates
        if random.random() < .01:
            rain.append(CodeRain())

        for drop in rain:
            row = int(drop.row * height)
            screen.chgat(row, int(drop.column * width), 1,
                         curses.color_pair(2) | curses.A_BOLD)
            for i in range(max(0, row - 4), row):
                screen.chgat(i, int(drop.column * width), 1,
                             curses.color_pair(2))
            drop.update()

        screen.refresh()

        #Delete rain at the bottom of screen
        rain = [drop for drop in rain if drop.row < 1]

        # Sync audio and video
        audio_time = audio.get_pts() * 1000
        movie_sleep = (movie.get(cv2.CAP_PROP_POS_MSEC) - audio_time)/1000
        if movie_sleep > 0:
            time.sleep(movie_sleep)
        else:
            while audio_time - movie.get(cv2.CAP_PROP_POS_MSEC) > 1:
                movie.read()

        running = screen.getch() != ord('q')

    audio.close_player()
    movie.release()

def init_curses(screen):
    curses.noecho()
    curses.cbreak()
    screen.nodelay(1)
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    screen.attron(curses.color_pair(1))
    screen.clear()

if __name__ == '__main__':
    curses.wrapper(main)

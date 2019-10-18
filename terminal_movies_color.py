"""
Watch movies in your terminal with this handy video-to-ascii converter.

Play movie like so:
>>>python3 terminal_movies.py path/to/movie
"""
import argparse
import curses
import cv2
from ffpyplayer.player import MediaPlayer


parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to movie")
args = parser.parse_args()
path = args.path

values = [0, 95, 135, 175, 215, 255]
color_map = {}
for color in range(256):
    color_map[color] = min(values,key=lambda value:abs(value-color))
values = {value:i for i,value in enumerate(values)}


def main(screen):
    init_curses(screen)

    movie = cv2.VideoCapture(path)
    audio = MediaPlayer(path)
    running = read_flag = True

    while read_flag and running:
        audio.get_frame()
        read_flag, frame = movie.read()

        resized = cv2.resize(frame, screen.getmaxyx()[::-1])

        for row_num, row in enumerate(resized):
            for column, color in enumerate(row[:-1]):
                pair = sum(6**i * values[color_map[value]]
                           for i, value in enumerate(reversed(color))) + 17
                screen.addstr(row_num, column," ", curses.color_pair(pair))
        screen.refresh()

        # This loop syncs video with audio.  Without it the video may lag behind.
        audio_time = audio.get_pts() * 1000
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
    curses.start_color()
    curses.use_default_colors()
    for i in range(curses.COLORS):
        curses.init_pair(i + 1, -1, i)
    screen.clear()

if __name__ == '__main__':
    curses.wrapper(main)

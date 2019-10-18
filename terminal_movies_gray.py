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

scale = 255/26 + .05


def main(screen):
    init_curses(screen)

    movie = cv2.VideoCapture(path)
    audio = MediaPlayer(path)
    running = read_flag = True

    while read_flag and running:
        audio.get_frame()
        read_flag, frame = movie.read()

        grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(grayscale, screen.getmaxyx()[::-1])

        for row_num, row in enumerate(resized):
            for column, color in enumerate(row[:-1]):
                screen.addstr(row_num, column," ", curses.color_pair(int(color/scale + 1)))
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
    curses.init_pair(1, -1, 16)
    for i in range(232, 256):
        curses.init_pair(i-230, -1, i)
    curses.init_pair(26, -1, 15)
    screen.clear()

if __name__ == '__main__':
    curses.wrapper(main)

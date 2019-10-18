"""
Watch movies in your terminal with this handy video-to-ascii converter.

Note that characters are actually mirrored in the matrix, but besides that we should have
most of the characters found in the matrix "code-rain".

Play movie like so:
>>>python3 terminal_movies_ascii.py path/to/movie
"""
import argparse
import curses
import time
import cv2
from ffpyplayer.player import MediaPlayer


parser = argparse.ArgumentParser()
parser.add_argument("path", help="path to movie")
args = parser.parse_args()
path = args.path

ascii_map = dict(enumerate(' ._ｰ*:ﾝ+=<>ﾆﾍﾐｼｺ7ﾃｯﾘﾒﾅｱﾗﾊｹﾏ1ｸﾜｴｽｳｷﾑﾇﾈﾓｵｻﾎ2ｾﾀZ3I54ｶ908'))
scale = 255/len(ascii_map) + .05  # Add a small amount to prevent key errors

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
            screen.addstr(row_num, 0,
                          ''.join(ascii_map[int(color/scale)] for color in row[:-1]))
        screen.refresh()

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
    screen.attron(curses.color_pair(1))
    screen.clear()

if __name__ == '__main__':
    curses.wrapper(main)

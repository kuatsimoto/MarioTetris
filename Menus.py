import pyglet
from pyglet.window import key
import numpy as np


class Main_Menu:
    def __init__(self, width, height, *args, **kwargs):
        self.window_width = width
        self.window_height = height
        self.title = pyglet.text.Label('Tetris', font_size=48, bold=False, x=self.window_width // 2,
                                       y=self.window_height // 1.3, font_name='Impact')
        self.button_label = pyglet.text.Label('Play', font_size=32, bold=False, x=self.window_width // 2 + 32,
                                         y=self.title.y - 48 * 2, font_name='Impact')
        self.button_box = pyglet.shapes.BorderedRectangle(x=self.button_label.x - 32 / 4, y=self.button_label.y - 32 / 4,
                                                     width=32 * 2.8, height=32 + 32 / 2,
                                                     color=(0, 0, 0), border_color=(255, 255, 255))
        self.exit_label = pyglet.text.Label('Quit', font_size=32, bold=False, x=self.window_width // 2 + 32,
                                              y=self.title.y - 48 * 3.5, font_name='Impact')
        self.exit_box = pyglet.shapes.BorderedRectangle(x=self.exit_label.x - 32 / 4,
                                                          y=self.exit_label.y - 32 / 4,
                                                          width=32 * 2.8, height=32 + 32 / 2,
                                                          color=(0, 0, 0), border_color=(255, 255, 255))
        self.game_start = False

    def play_button(self):

        self.button_box.draw()
        self.button_label.draw()
        self.exit_box.draw()
        self.exit_label.draw()


    def draw(self):
        self.title.draw()
        self.play_button()

    def update(self):
        self.on_mouse_press()


class GameOver:
    def __init__(self, width, height, *args, **kwargs):
        self.window_width = width
        self.window_height = height
        self.final_score = 0
        self.high_score = 0
        self.title = pyglet.text.Label('Game Over', font_size=48, bold=False, x=self.window_width // 2 - 32*4,
                                       y=self.window_height // 1.3, font_name='Impact')
        self.button_label = pyglet.text.Label('Retry', font_size=32, bold=False, x=self.window_width // 2 - 32,
                                         y=self.title.y - 48 * 2, font_name='Impact')
        self.button_box = pyglet.shapes.BorderedRectangle(x=self.button_label.x - 32 / 4, y=self.button_label.y - 32 / 4,
                                                     width=32 * 3.5, height=32 + 32 / 2,
                                                     color=(0, 0, 0), border_color=(255, 255, 255))
        self.back_label = pyglet.text.Label('Back', font_size=32, bold=False, x=self.window_width // 2 - 32,
                                              y=self.title.y - 48 * 4, font_name='Impact')
        self.back_box = pyglet.shapes.BorderedRectangle(x=self.back_label.x - 32 / 4,
                                                          y=self.back_label.y - 32 / 4,
                                                          width=32 * 3.5, height=32 + 32 / 2,
                                                          color=(0, 0, 0), border_color=(255, 255, 255))
        self.high_score_label = pyglet.text.Label('High Score:  {}'.format(self.high_score), font_size=32, bold=False, x=self.window_width // 2 - 32*6,
                                              y=self.title.y - 48 * 5.5, font_name='Impact')

        self.game_over = False


    def buttons(self):

        self.button_box.draw()
        self.button_label.draw()
        self.back_box.draw()
        self.back_label.draw()
        self.high_score_label = pyglet.text.Label('High Score:  {}'.format(self.high_score), font_size=32, bold=False,
                                                  x=self.window_width // 2 - 32 * 4.5,
                                                  y=self.title.y - 48 * 6, font_name='Impact').draw()
        pyglet.text.Label('Your Score:  {}'.format(self.final_score), font_size=32, bold=False,
                          x=self.window_width // 2 - 32 * 4.5,
                          y=self.title.y - 48 * 7, font_name='Impact').draw()


    def draw(self):
        self.title.draw()
        self.buttons()


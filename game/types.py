"""Core type definitions for the Pacman game.

Pure data types and enums. MUST NOT import pygame.
"""
from enum import Enum


class Action(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    NOOP = 4


class Status(Enum):
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"

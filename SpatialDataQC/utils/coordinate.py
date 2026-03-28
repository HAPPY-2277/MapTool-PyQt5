from typing import Tuple, Optional


def screen_to_world(
    screen_x: float,
    screen_y: float,
    offset_x: float,
    offset_y: float,
    scale: float
) -> Tuple[float, float]:
    world_x = (screen_x - offset_x) / scale
    world_y = (screen_y - offset_y) / scale
    return world_x, world_y


def world_to_screen(
    world_x: float,
    world_y: float,
    offset_x: float,
    offset_y: float,
    scale: float
) -> Tuple[float, float]:
    screen_x = world_x * scale + offset_x
    screen_y = world_y * scale + offset_y
    return screen_x, screen_y


def normalize_coordinates(
    x: float,
    y: float,
    extent: Tuple[float, float, float, float]
) -> Tuple[float, float]:
    x_min, y_min, x_max, y_max = extent
    x_range = x_max - x_min if x_max != x_min else 1
    y_range = y_max - y_min if y_max != y_min else 1
    
    norm_x = (x - x_min) / x_range
    norm_y = (y - y_min) / y_range
    
    return norm_x, norm_y


def denormalize_coordinates(
    norm_x: float,
    norm_y: float,
    extent: Tuple[float, float, float, float]
) -> Tuple[float, float]:
    x_min, y_min, x_max, y_max = extent
    x_range = x_max - x_min if x_max != x_min else 1
    y_range = y_max - y_min if y_max != y_min else 1
    
    x = norm_x * x_range + x_min
    y = norm_y * y_range + y_min
    
    return x, y


def is_point_in_extent(
    x: float,
    y: float,
    extent: Tuple[float, float, float, float]
) -> bool:
    x_min, y_min, x_max, y_max = extent
    return x_min <= x <= x_max and y_min <= y <= y_max


def calculate_distance(
    x1: float,
    y1: float,
    x2: float,
    y2: float
) -> float:
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

# -*- coding: utf-8 -*-


def get_frame_border_color(rarity):
    border_rarity_colors = {
        "common": (177, 177, 177),
        "uncommon": (135, 227, 57),
        "rare": (55, 209, 255),
        "epic": (233, 94, 255),
        "legendary": (233, 141, 75)
    }

    return border_rarity_colors[rarity]


def get_frame_center_color(rarity):
    center_rarity_colors = {
        "common": (190, 190, 190),
        "uncommon": (105, 187, 30),
        "rare": (44, 193, 255),
        "epic": (195, 89, 255),
        "legendary": (234, 141, 35)
    }

    return center_rarity_colors[rarity]


def get_frame_corner_color(rarity):
    corner_rarity_colors = {
        "common": (100, 100, 100),
        "uncommon": (23, 81, 23),
        "rare": (20, 57, 119),
        "epic": (75, 36, 131),
        "legendary": (120, 55, 29)
    }

    return corner_rarity_colors[rarity]

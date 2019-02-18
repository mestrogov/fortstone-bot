# -*- coding: utf-8 -*-


def parse_as_boolean(arg):
    if str(arg).lower() in ["true", "1"]:
        return True
    else:
        return False

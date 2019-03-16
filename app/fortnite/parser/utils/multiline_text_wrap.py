# -*- coding: utf-8 -*_


def wrap(text, font, max_width):
    if font.getsize(text)[0] <= max_width:
        return text
    else:
        words = text.split(" ")
        line = ""
        result = ""
        for word in words:
            if font.getsize(line + word)[0] < max_width:
                line = line + word + " "
            else:
                result = result + line + word + " \n"
                line = ""
        if not result.endswith(line):
            result = result + line

        return result

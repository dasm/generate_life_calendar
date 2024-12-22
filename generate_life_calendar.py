#!/usr/bin/env python3
import argparse
import datetime
import math
import os

import cairo

# A1 standard international paper size
DOC_WIDTH = 1683  # 594mm / 23 3/8 inches
DOC_HEIGHT = 2383  # 841mm / 33 1/8 inches

DOC_NAME = "life_calendar.pdf"

KEY_NEWYEAR_DESC = "First week of the new year"
KEY_BIRTHDAY_DESC = "Week of your birthday"

FONT = "Brocha"
BIGFONT_SIZE = 40
SMALLFONT_SIZE = 16
TINYFONT_SIZE = 14

MAX_TITLE_SIZE = 30
DEFAULT_TITLE = "LIFE CALENDAR"

Y_MARGIN = 144
BOX_MARGIN = 6

MIN_AGE = 80
MAX_AGE = 100

BOX_LINE_WIDTH = 3
NUM_COLUMNS = 52

BIRTHDAY_COLOUR = (0.5, 0.5, 0.5)
NEWYEAR_COLOUR = (0.8, 0.8, 0.8)
DARKENED_COLOUR_DELTA = (-0.4, -0.4, -0.4)


def draw_canvas(ctx):
    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(0, 0, DOC_WIDTH, DOC_HEIGHT)
    ctx.fill()


def draw_title(ctx, title):
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_font_size(BIGFONT_SIZE)
    w, h = text_size(ctx, title)
    ctx.move_to((DOC_WIDTH / 2) - (w / 2), (Y_MARGIN / 2) - (h / 2))
    ctx.show_text(title)


def draw_subtitle(ctx, subtitle):
    if not subtitle:
        return

    ctx.set_source_rgb(0.7, 0.7, 0.7)
    ctx.set_font_size(SMALLFONT_SIZE)
    w, h = text_size(ctx, subtitle)
    ctx.move_to((DOC_WIDTH / 2) - (w / 2), (Y_MARGIN / 2) - (h / 2) + 15)
    ctx.show_text(subtitle)


def draw_sidebar(ctx, sidebar, margin):
    if not sidebar:
        return

    ctx.set_source_rgb(0.7, 0.7, 0.7)
    ctx.set_font_size(SMALLFONT_SIZE)
    w, _h = text_size(ctx, sidebar)
    ctx.move_to((DOC_WIDTH - margin) + 20, Y_MARGIN + w + 100)
    ctx.rotate(-90 * math.pi / 180)
    ctx.show_text(sidebar)


def draw_square(ctx, pos_x, pos_y, box_size, fillcolour=(1, 1, 1)):
    """
    Draws a square at pos_x,pos_y
    """
    ctx.set_line_width(BOX_LINE_WIDTH)
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(pos_x, pos_y)

    ctx.rectangle(pos_x, pos_y, box_size, box_size)
    ctx.stroke_preserve()

    ctx.set_source_rgb(*fillcolour)
    ctx.fill()


def text_size(ctx, text):
    _, _, width, height, _, _ = ctx.text_extents(text)
    return width, height


def back_up_to_monday(date):
    return date - datetime.timedelta(date.weekday())


def is_future(now, date):
    return now < date


def is_current_week(now, month, day):
    end = now + datetime.timedelta(weeks=1)
    ret = []

    for year in [now.year, now.year + 1]:
        try:
            date = datetime.datetime(year, month, day)
        except ValueError as e:
            if (month == 2) and (day == 29):
                # Handle edge case for birthday being on leap year day
                date = datetime.datetime(year, month, day - 1)
            else:
                raise e

        ret.append(now <= date < end)

    return True in ret


def get_darkened_fill(fill):
    return tuple(map(sum, zip(fill, DARKENED_COLOUR_DELTA)))


def draw_row(ctx, pos_y, birthdate, date, box_size, x_margin, darken_until_date):
    """
    Draws a row of 52 squares, starting at pos_y
    """

    pos_x = x_margin

    for _ in range(NUM_COLUMNS):
        fill = (1, 1, 1)

        if is_current_week(date, birthdate.month, birthdate.day):
            fill = BIRTHDAY_COLOUR
        elif is_current_week(date, 1, 1):
            fill = NEWYEAR_COLOUR

        if darken_until_date and is_future(date, darken_until_date):
            fill = get_darkened_fill(fill)

        draw_square(ctx, pos_x, pos_y, box_size, fillcolour=fill)
        pos_x += box_size + BOX_MARGIN
        date += datetime.timedelta(weeks=1)


def draw_legend(ctx, pos_x, pos_y, box_size):
    for desc, colour in (
        (KEY_NEWYEAR_DESC, NEWYEAR_COLOUR),
        (KEY_BIRTHDAY_DESC, BIRTHDAY_COLOUR),
    ):
        draw_square(ctx, pos_x, pos_y, box_size, fillcolour=colour)
        pos_x += box_size + (box_size / 2)

        ctx.set_source_rgb(0, 0, 0)
        w, h = text_size(ctx, desc)
        ctx.move_to(pos_x, pos_y + (box_size / 2) + (h / 2))
        ctx.show_text(desc)

        pos_x += w + (box_size * 2)


def draw_grid(ctx, birthdate, num_rows, darken_until_date):
    """
    Draws the whole grid of 52x(num_rows) squares
    """
    # Draw the key for box colours
    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    box_size = ((DOC_HEIGHT - (Y_MARGIN + 36)) / num_rows) - BOX_MARGIN
    x_margin = (DOC_WIDTH - ((box_size + BOX_MARGIN) * NUM_COLUMNS)) / 2

    pos_x = x_margin / 4
    pos_y = pos_x

    # Draw legend
    draw_legend(ctx, pos_x, pos_y, box_size)

    # draw week numbers above top row
    monday = back_up_to_monday(birthdate)

    pos_x = x_margin
    pos_y = Y_MARGIN
    for idx in range(1, NUM_COLUMNS + 1):
        w, h = text_size(ctx, str(idx))
        ctx.move_to(pos_x + (box_size / 2) - (w / 2), pos_y - box_size)
        if idx % 4 == 0:
            ctx.show_text(str(idx))
        pos_x += box_size + BOX_MARGIN

    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_ITALIC, cairo.FONT_WEIGHT_NORMAL)

    for idx in range(1, num_rows + 1):
        # Generate string for current date
        ctx.set_source_rgb(0, 0, 0)
        _ = monday.strftime("%d %b, %Y")
        w, h = text_size(ctx, str(idx))

        # Draw it in front of the current row
        ctx.move_to(x_margin - w - box_size, pos_y + ((box_size / 2) + (h / 2)))
        if idx % 5 == 0:
            ctx.show_text(str(idx))

        # Draw the current row
        draw_row(ctx, pos_y, birthdate, monday, box_size, x_margin, darken_until_date)

        # Increment y position and current date by 1 row/year
        pos_y += box_size + BOX_MARGIN
        monday += datetime.timedelta(weeks=52)

    return x_margin


def gen_calendar(
    birthdate,
    title,
    age,
    filename,
    darken_until_date,
    sidebar,
    subtitle,
):
    # Fill background with white
    surface = cairo.PDFSurface(filename, DOC_WIDTH, DOC_HEIGHT)
    ctx = cairo.Context(surface)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

    draw_canvas(ctx)
    draw_title(ctx, title)
    draw_subtitle(ctx, subtitle)

    x_margin = draw_grid(ctx, birthdate, age, darken_until_date)
    draw_sidebar(ctx, sidebar, x_margin)

    ctx.show_page()


def generate_parser():
    parser = argparse.ArgumentParser(
        description='\nGenerate a personalized "Life '
        ' Calendar", inspired by the calendar with the same name from the '
        "waitbutwhy.com store"
    )
    parser.add_argument(
        "date",
        type=datetime.datetime.fromisoformat,
        help="starting date; your birthday, in ISO format",
    )
    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        dest="filename",
        help="output filename",
        default=DOC_NAME,
    )

    def title_len(title):
        if len(title) > MAX_TITLE_SIZE:
            raise argparse.ArgumentTypeError(
                "Title can't be longer than %d characters" % MAX_TITLE_SIZE
            )
        return title

    parser.add_argument(
        "-t",
        "--title",
        type=title_len,
        dest="title",
        help='Calendar title text (default is "%s")' % DEFAULT_TITLE,
        default=DEFAULT_TITLE,
    )

    parser.add_argument(
        "-s",
        "--sidebar-text",
        type=str,
        dest="sidebar",
        help="Text to show along the right side of grid (default is no sidebar text)",
    )

    parser.add_argument(
        "-b",
        "--subtitle-text",
        type=str,
        dest="subtitle",
        help="Text to show under the calendar title (default is no subtitle text)",
    )

    parser.add_argument(
        "-a",
        "--age",
        type=int,
        dest="age",
        choices=range(MIN_AGE, MAX_AGE + 1),
        metavar="[%s-%s]" % (MIN_AGE, MAX_AGE),
        help=("Number of rows to generate, representing years of life"),
        default=90,
    )

    parser.add_argument(
        "-d",
        "--darken-until",
        type=datetime.datetime.fromisoformat,
        dest="darken_until_date",
        default=datetime.datetime.today(),
        help="Darken until date. " "(defaults to today if argument is not given)",
    )

    return parser


def main():
    parser = generate_parser()
    args = parser.parse_args()
    doc_name = "%s.pdf" % (os.path.splitext(args.filename)[0])

    gen_calendar(
        args.date,
        args.title,
        args.age,
        doc_name,
        args.darken_until_date,
        sidebar=args.sidebar,
        subtitle=args.subtitle,
    )
    print("Created %s" % doc_name)


if __name__ == "__main__":
    main()

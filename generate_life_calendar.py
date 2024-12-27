#!/usr/bin/env python3
import argparse
import datetime
import math

import cairo

# A1 standard international paper size
DOC_WIDTH = 1683  # 594mm / 23 3/8 inches
DOC_HEIGHT = 2383  # 841mm / 33 1/8 inches

OUTPUT_FILE = "life_calendar.pdf"

KEY_BIRTHDAY_DESC = "Birthday"

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
NUM_OF_WEEKS = 52

BIRTHDAY_COLOR = (0.5, 0.5, 0.5)
DARKENED_COLOR_DELTA = (-0.4, -0.4, -0.4)


def get_text_size(ctx, text):
    _, _, width, height, _, _ = ctx.text_extents(text)
    return width, height


def get_weeks(year):
    return datetime.date(year, 12, 28).isocalendar().week


def get_monday(date):
    return date - datetime.timedelta(date.weekday())


def shaded_fill(fill):
    return tuple(map(sum, zip(fill, DARKENED_COLOR_DELTA)))


def draw_canvas(ctx):
    ctx.set_source_rgb(1, 1, 1)
    ctx.rectangle(0, 0, DOC_WIDTH, DOC_HEIGHT)
    ctx.fill()


def draw_title(ctx, title):
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_font_size(BIGFONT_SIZE)
    w, h = get_text_size(ctx, title)
    ctx.move_to((DOC_WIDTH / 2) - (w / 2), (Y_MARGIN / 2) - (h / 2))
    ctx.show_text(title)


def draw_subtitle(ctx, subtitle):
    if not subtitle:
        return

    ctx.set_source_rgb(0.7, 0.7, 0.7)
    ctx.set_font_size(SMALLFONT_SIZE)
    w, h = get_text_size(ctx, subtitle)
    ctx.move_to((DOC_WIDTH / 2) - (w / 2), (Y_MARGIN / 2) - (h / 2) + 15)
    ctx.show_text(subtitle)


def draw_sidebar(ctx, sidebar, pos_x):
    if not sidebar:
        return

    ctx.save()

    ctx.set_source_rgb(0.7, 0.7, 0.7)
    ctx.set_font_size(SMALLFONT_SIZE)
    w, _h = get_text_size(ctx, sidebar)
    ctx.move_to((DOC_WIDTH - pos_x) + 20, Y_MARGIN + w + 100)
    ctx.rotate(-90 * math.pi / 180)
    ctx.show_text(sidebar)

    ctx.restore()


def draw_box(ctx, pos_x, pos_y, box_size, fillcolor=(1, 1, 1)):
    """
    Draws a square at pos_x,pos_y
    """
    ctx.set_line_width(BOX_LINE_WIDTH)
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(pos_x, pos_y)

    ctx.rectangle(pos_x, pos_y, box_size, box_size)
    ctx.stroke_preserve()

    # Add color
    ctx.set_source_rgb(*fillcolor)
    ctx.fill()


def draw_legend(ctx, box_size, pos_x, pos_y):
    x_margin = pos_x

    for desc, color in (
        (KEY_BIRTHDAY_DESC, BIRTHDAY_COLOR),
    ):
        draw_box(ctx, x_margin, pos_y, box_size, fillcolor=color)
        pos_x = x_margin + box_size + (box_size / 2)

        ctx.set_source_rgb(0, 0, 0)
        w, h = get_text_size(ctx, desc)
        ctx.move_to(pos_x, pos_y + (box_size / 2) + (h / 2))
        ctx.show_text(desc)

        pos_y += box_size + BOX_MARGIN


def draw_week_numbers(ctx, box_size, pos_x):
    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    for idx in range(1, NUM_OF_WEEKS + 1):
        w, h = get_text_size(ctx, str(idx))
        ctx.move_to(pos_x + (box_size / 2) - (w / 2), Y_MARGIN - box_size)
        if idx % 4 == 0:
            ctx.show_text(str(idx))
            pos_x += BOX_MARGIN
        pos_x += box_size + BOX_MARGIN


def draw_year_numbers(ctx, box_size, pos_x, pos_y, life_expectancy):
    ctx.set_font_size(TINYFONT_SIZE)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    for year in range(life_expectancy):
        ctx.set_source_rgb(0, 0, 0)
        w, h = get_text_size(ctx, str(year))

        # Draw it in front of the current row
        ctx.move_to(pos_x - w - box_size, pos_y + ((box_size / 2) + (h / 2)))
        ctx.show_text(str(year))
        pos_y += box_size + BOX_MARGIN


def draw_row(ctx, box_size, pos_x, pos_y, birthdate, shade_until_date, first_row=False):
    """
    Draws a row of 52 squares, starting at pos_y
    """
    date = datetime.date(birthdate.year, 1, 1)
    for week in range(1, get_weeks(birthdate.year) + 1):
        fill = (1, 1, 1)
        _year, birthday_week, _weekday = birthdate.isocalendar()

        if week == birthday_week:
            fill = BIRTHDAY_COLOR

        if date < shade_until_date:
            fill = shaded_fill(fill)

        if (first_row and (week >= birthdate.isocalendar().week)) or (not first_row):
            draw_box(ctx, pos_x, pos_y, box_size, fillcolor=fill)

        if week % 4 == 0:
            pos_x += BOX_MARGIN
        pos_x += box_size + BOX_MARGIN
        date += datetime.timedelta(weeks=1)


def draw_grid(
    ctx, box_size, pos_x, pos_y, life_expectancy, shade_until_date, birthdate
):
    """
    Draws the whole grid of 52x(life_expectancy) squares
    """
    # Draw the key for box colors
    birthdate_year = birthdate.year
    for idx, year in enumerate(
        range(birthdate_year + 1, birthdate_year + 1 + life_expectancy)
    ):
        birthdate = datetime.date(year, birthdate.month, birthdate.day)
        draw_row(ctx, box_size, pos_x, pos_y, birthdate, shade_until_date, idx == 0)
        pos_y += box_size + BOX_MARGIN


def gen_calendar(
    birthdate,
    title,
    life_expectancy,
    shade_until_date,
    sidebar,
    subtitle,
):
    # Fill background with white
    surface = cairo.PDFSurface(OUTPUT_FILE, DOC_WIDTH, DOC_HEIGHT)
    ctx = cairo.Context(surface)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)

    box_size = ((DOC_HEIGHT - (Y_MARGIN + 36)) / life_expectancy) - BOX_MARGIN
    pos_x = (
        DOC_WIDTH
        - ((box_size + BOX_MARGIN) * NUM_OF_WEEKS)
        - (BOX_MARGIN * NUM_OF_WEEKS / 4)
    ) / 2

    draw_canvas(ctx)
    draw_title(ctx, title)
    draw_subtitle(ctx, subtitle)

    draw_legend(ctx, box_size, pos_x, pos_x / 4)

    draw_week_numbers(ctx, box_size, pos_x)
    draw_year_numbers(ctx, box_size, pos_x, Y_MARGIN, life_expectancy)
    draw_grid(
        ctx, box_size, pos_x, Y_MARGIN, life_expectancy, shade_until_date, birthdate
    )

    draw_sidebar(ctx, sidebar, pos_x)

    ctx.show_page()


def generate_parser():
    parser = argparse.ArgumentParser(
        description='\nGenerate a personalized "Life '
        ' Calendar", inspired by the calendar with the same name from the '
        "waitbutwhy.com store"
    )
    parser.add_argument(
        "date",
        type=datetime.date.fromisoformat,
        help="starting date; your birthday, in ISO format",
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
        type=datetime.date.fromisoformat,
        dest="shade_until_date",
        default=datetime.date.today(),
        help="Darken until date. " "(defaults to today if argument is not given)",
    )

    return parser


def main():
    parser = generate_parser()
    args = parser.parse_args()

    gen_calendar(
        args.date,
        args.title,
        args.age,
        args.shade_until_date,
        args.sidebar,
        subtitle=(args.subtitle or str(args.date)),
    )


if __name__ == "__main__":
    main()

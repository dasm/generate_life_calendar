import argparse
import calendar
import datetime
import math

import cairo

OUTPUT_FILE = "goal.pdf"
WIDTH = HEIGHT = 3
PIXEL_SCALE = 1000

CIRCLE_X = WIDTH / 2
CIRCLE_Y = HEIGHT / 2

LINE_LENGTH = 0.6
LINE_WIDTH = 0.01

MONTHS = dict(zip(range(1, 13), calendar.month_name[1:]))
START_ANGLE = 270

BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (1, 1, 1)


def draw_background(ctx):
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.set_source_rgb(*WHITE_COLOR)  # white color
    ctx.fill()


def draw_boxes(ctx, date, month):
    cal = calendar.Calendar()
    weeks = cal.monthdatescalendar(date.year, month)
    weeks = [[day if day.month == month else 0 for day in week] for week in weeks]

    ctx.save()
    # NOTE: Separate from the hard line
    ctx.translate(0, 0.02)

    for week in weeks:
        draw_days(ctx, date, week)
        # NOTE: Divide a circle by 12 months * 6 weeks
        ctx.rotate(2 * math.pi / (12 * 6))
        # NOTE: Separate line of boxes, correct x axis
        ctx.translate(0.002, 0.06)

    ctx.restore()


def draw_days(ctx, date, days):
    ctx.save()
    # NOTE: Rescale box
    ctx.scale(0.05, 0.05)

    for day in days:
        border = BLACK_COLOR
        background = WHITE_COLOR
        if day == 0:
            # NOTE: Draw "white/empty" box
            border = WHITE_COLOR
        elif day < date:
            background = BLACK_COLOR
        draw_roundrect(ctx, border, background)
        ctx.translate(1.2, 0)

    ctx.restore()


def draw_roundrect(ctx, border=BLACK_COLOR, background=WHITE_COLOR):
    ctx.set_line_width(LINE_WIDTH * 5)
    ctx.set_source_rgb(*border)

    x = y = 0
    width = height = 1
    r = 0.2
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.arc(x + width - r, y + r, r, 3 * math.pi / 2, 0)
    ctx.arc(x + width - r, y + height - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + height - r, r, math.pi / 2, math.pi)
    ctx.close_path()
    ctx.stroke_preserve()

    ctx.set_source_rgb(*background)
    ctx.fill()


def draw_line(ctx):
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(0, 0)
    ctx.line_to(LINE_LENGTH, 0)
    ctx.set_line_width(LINE_WIDTH)
    ctx.stroke()


def draw_circle(ctx, date):
    ctx.translate(HEIGHT / 2, WIDTH / 2)
    # NOTE: Rotate back by 90* to start from top
    ctx.rotate(START_ANGLE * math.pi / 180)

    for idx, month in MONTHS.items():
        radians = 2 * math.pi * (idx - 1) / 12

        ctx.save()

        # NOTE: Rotate by x/12th (no of months)
        ctx.rotate(radians)

        # NOTE: Move (0, 0) to pos (0.75, 0) considering new angle
        ctx.translate(0.75, 0)
        draw_line(ctx)
        draw_boxes(ctx, date, idx)

        draw_month_names(ctx, month, radians)
        ctx.restore()


def draw_month_names(ctx, month, radians):
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_font_size(0.05)
    ctx.select_font_face("Brocha", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)

    _, _, width, height, _, _ = ctx.text_extents(month)

    # NOTE: Move to expected location
    ctx.translate(0.55, 0.15)
    # NOTE: Rotate back to 'normal' angle
    ctx.rotate((math.pi / 2) - radians)
    # NOTE: Translate based on center of a word
    ctx.translate(-width / 2, height / 2)
    ctx.move_to(0, 0)
    ctx.show_text(month)


def main(date):
    surface = cairo.PDFSurface(OUTPUT_FILE, WIDTH * PIXEL_SCALE, HEIGHT * PIXEL_SCALE)
    ctx = cairo.Context(surface)
    ctx.scale(PIXEL_SCALE, PIXEL_SCALE)

    draw_background(ctx)
    draw_circle(ctx, date)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d", "--date", type=datetime.date.fromisoformat, default=datetime.date.today()
    )
    parser.add_argument("-s", "--sunday", action="store_true", default=False)
    args = parser.parse_args()
    if args.sunday:
        calendar.setfirstweekday(calendar.SUNDAY)
    main(args.date)

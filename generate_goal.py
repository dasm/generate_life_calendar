import argparse
import calendar
import math

import cairo

WIDTH = HEIGHT = 3
PIXEL_SCALE = 1000

CIRCLE_X = WIDTH / 2
CIRCLE_Y = HEIGHT / 2

LINE_LENGTH = 0.6
LINE_WIDTH = 0.01


def draw_background(ctx):
    ctx.rectangle(0, 0, WIDTH, HEIGHT)
    ctx.set_source_rgb(1, 1, 1)  # white color
    ctx.fill()


def draw_boxes(ctx, year, month):
    weeks = calendar.monthcalendar(year, month)
    # angle = 2 * math.pi / 12 / len(weeks)

    ctx.save()
    # NOTE: Separate from the hard line
    ctx.translate(0, 0.02)

    for week in weeks:
        draw_days(ctx, week)
        # NOTE: Divide a circle by 12 months * 6 weeks
        ctx.rotate(2 * math.pi / (12 * 6))
        # NOTE: Separate line of boxes, correct x axis
        ctx.translate(0.002, 0.06)

    ctx.restore()


def draw_days(ctx, days):
    ctx.save()
    # NOTE: Rescale box
    ctx.scale(0.05, 0.05)
    for day in days:
        color = (0, 0, 0)
        if day == 0:
            # NOTE: Draw "white/empty" box
            color = (1, 1, 1)
        draw_roundrect(ctx, color)
        ctx.translate(1.2, 0)

    ctx.restore()


def draw_roundrect(ctx, color=(0, 0, 0)):
    ctx.set_line_width(LINE_WIDTH * 5)
    ctx.set_source_rgb(*color)

    x = y = 0
    width = height = 1
    r = 0.2
    ctx.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    ctx.arc(x + width - r, y + r, r, 3 * math.pi / 2, 0)
    ctx.arc(x + width - r, y + height - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + height - r, r, math.pi / 2, math.pi)
    ctx.close_path()
    ctx.stroke()


def draw_line(ctx):
    ctx.set_source_rgb(0, 0, 0)
    ctx.move_to(0, 0)
    ctx.line_to(LINE_LENGTH, 0)
    ctx.set_line_width(LINE_WIDTH)
    ctx.stroke()


def draw_circle(ctx, year):
    ctx.translate(HEIGHT / 2, WIDTH / 2)
    for month in range(1, 13):
        ctx.save()

        # NOTE: Rotate by 1/12th (a month)
        ctx.rotate(2 * math.pi * month / 12)

        # NOTE: Move (0, 0) to pos (0.75, 0) considering new angle
        ctx.translate(0.75, 0)

        draw_line(ctx)
        draw_boxes(ctx, year, month)
        ctx.restore()


def main(year):
    surface = cairo.ImageSurface(
        cairo.FORMAT_RGB24, WIDTH * PIXEL_SCALE, HEIGHT * PIXEL_SCALE
    )
    ctx = cairo.Context(surface)
    ctx.scale(PIXEL_SCALE, PIXEL_SCALE)

    draw_background(ctx)
    draw_circle(ctx, year)
    surface.write_to_png("rectangle.png")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("year", type=int)
    args = parser.parse_args()
    main(args.year)

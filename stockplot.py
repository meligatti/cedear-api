import matplotlib.pyplot as plt
import numpy as np
from datetime import date, datetime

def draw_line(x_coord, y_coord, plot_color):
    plt.plot(x_coord, y_coord, plot_color)
    # plt.show()

def draw_markers(x_coord, y_coord, day_extr):
    marker_width = 0.2
    day_start = day_extr[0]
    day_end = day_extr[1]
    # Ver color
    if day_start <= day_end:
        plot_color = 'g'
    else:
        plot_color = 'r'

    line_x_coord = [x_coord - marker_width, x_coord]
    line_y_coord = [day_start, day_start]
    draw_line(line_x_coord, line_y_coord, plot_color)

    line_x_coord = [x_coord, x_coord + marker_width]
    line_y_coord = [day_end, day_end]
    draw_line(line_x_coord, line_y_coord, plot_color)
    draw_line([x_coord, x_coord], y_coord, plot_color)
    # plt.show()

def ohlc_plot(opening, maximum, minimum, closing, dates):
    if len(opening) == len(closing) == len(minimum) == len(maximum):
        #TODO: Maybe I can fill the list element by element using the for-loop
        for i in range(len(opening)):
            x_coord = i + 1
            y_coord = [minimum[i], maximum[i]]
            day_extremes = [opening[i], closing[i]]
            draw_markers(x_coord, y_coord, day_extremes)
        fig = plt.gcf()
        ax = plt.gca()
        ax.set_xticks([i + 1 for i in range(len(opening))])
        ax.set_xticklabels(dates, rotation = 45)
        fig.autofmt_xdate()
        plt.show()
    else:
        print('Check list lengths')

def draw_amount_exchanged(amount, dates):
    if len(amount) == len(dates):
        # h, edges = np.histogram(np.asarray(amount, dtype = 'float'),
        #                         [datetime(date.year, date.month, date.day) for date in dates])
        # fig, ax = plt.subplots()
        # ax.stairs(h, edges)
        # ax.set_title("Amount exchanged")

        # plt.hist(amount, bins = len(dates))
        # plt.show()
        fig = plt.gcf()
        ax = plt.subplot(111)
        ax.bar(dates, amount, width = 1)
        # ax.set_xticks([i + 1 for i in range(len(amount))])
        ax.xaxis_date()
        fig.autofmt_xdate()
        plt.show()

# def draw_stock_plots(opening, maximum, minimum, closing, amount, stock_name, dates):
#     amount_of_draws = 2
#     # TODO: Hay un argumento que se llama share x axis o algo así
#     fig, (ohlc_ax, amount_ax) = plt.subplots(amount_of_draws)
#     fig.suptitle(stock_name)


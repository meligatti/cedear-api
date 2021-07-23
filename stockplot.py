import matplotlib.pyplot as plt
import textparsing as tp


# Auxiliary functions to make the OHLC plot. This kind of plot summarizes the most important information about a stock
# value in a daily basis. For each day, there is a vertical line that represents the extreme values (maximum and
# minimum) and two horizontal lines marking the opening and closing price.

def draw_line(x_coord, y_coord, plot_color):
    plt.plot(x_coord, y_coord, plot_color)

# This function generates all the coordinates to plot each daily symbol. Its color depends on which extreme price is
# bigger than the other one.
def draw_markers(x_coord, y_coord, day_extr):
    marker_width = 0.2
    day_start = day_extr[0]
    day_end = day_extr[1]
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


# Function to configure the vertical axis of the amount exchanged plot. The number of ticks (marks) can be edited.
def format_y_axis(values_list):
    tick_number = 5
    # Add an extra margin for vertical axis maximum tick
    list_max = float(max(values_list)) * 1.05
    tick_list = [list_max * i / tick_number for i in range(tick_number + 1)]
    if list_max / 1000 < 1000:
        tick_labels = ['{:.1f}K'.format(i / 1000) for i in tick_list]
    else:
        tick_labels = ['{:.1f}M'.format(i / 1000000) for i in tick_list]
    plt.yticks(tick_list, tick_labels)



def set_labels(title, x_label, y_label):
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)


def ohlc_plot(opening, maximum, minimum, closing, dates, stock_list, sel_stock, ohlc_ax = None, ohlc_fig = None):
    if len(opening) == len(closing) == len(minimum) == len(maximum):
        stock_currency = get_stock_currency(stock_list, sel_stock)
        for i in range(len(opening)):
            x_coord = i + 1
            y_coord = [minimum[i], maximum[i]]
            day_extremes = [opening[i], closing[i]]
            draw_markers(x_coord, y_coord, day_extremes)
        if ohlc_ax == None:
            ohlc_ax = plt.gca()
            ohlc_fig = plt.gcf()
        fixed_stock_name = tp.revert_stock_name_fix(sel_stock)
        set_labels(fixed_stock_name.upper() + ' stock price', 'Date', stock_currency)
        ohlc_ax.set_xticks([i + 1 for i in range(len(opening))])
        ohlc_ax.set_xticklabels(dates, rotation = 45)
        ohlc_ax.xaxis_date()
        ohlc_fig.autofmt_xdate()
        plt.show()
    else:
        print('Check list lengths')

def draw_amount_exchanged(amount, dates, stock_list, sel_stock, amount_ax = None, amount_fig = None):
    if len(amount) == len(dates):
        stock_currency = get_stock_currency(stock_list, sel_stock)
        if amount_ax == None:
            amount_ax = plt.subplot(111)
            amount_fig = plt.gcf()
        marker_days = 1
        amount_ax.bar(dates, amount, align = 'center', width = marker_days)
        fixed_stock_name = tp.revert_stock_name_fix(sel_stock)
        set_labels(fixed_stock_name.upper() + ' amount exchanged', 'Date', stock_currency)
        format_y_axis(amount)
        amount_ax.xaxis_date()
        amount_fig.autofmt_xdate()
        plt.tight_layout()
        plt.show()
    else:
        print('Check list lengths')


# Function that returns a string with the stock currency used on the plots vertical axes. There are many companies that
# have several stocks. The main stock is in ARS and the other ones are in USD. The names of the last ones are composed
# by the original stock name with ARS currency and a C or a D in the end.
# There are some cases that do not comply with the above rule. They are considered and listed as exceptions.

def get_stock_currency(stock_list, selected_stock):
    last_stock_char = selected_stock[-1]
    if last_stock_char == 'c' or last_stock_char == 'd':
        stock_index = stock_list.index(selected_stock)
        if stock_index == 0:
            stock_currency = 'ARS'
        elif stock_index == 1:
            if tp.is_base_stock_name(stock_list[0], selected_stock[:-1]):
                stock_currency = 'USD'
            else:
                stock_currency = 'ARS'
        else:
            if tp.is_usd_stock_exception(selected_stock):
                stock_currency = 'USD'
            elif tp.is_ars_stock_exception(selected_stock):
                stock_currency = 'ARS'
                print('It is ARS exception')
            elif tp.is_base_stock_name(stock_list[stock_index - 2], selected_stock[:-1]) or \
                 tp.is_base_stock_name(stock_list[stock_index - 1], selected_stock[:-1]):
                stock_currency = 'USD'
            else:
                stock_currency = 'ARS'
    elif selected_stock == 'mod_stk':
        stock_currency = 'USD'
    else:
        stock_currency = 'ARS'
    return stock_currency


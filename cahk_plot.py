import numpy as np
import matplotlib.pyplot as plt
import statistics

from astropy.io import ascii
import sys
import os.path
from datetime import datetime

import bandpass
import tools
import plot

def main():

    # Gets name of csv file with times and s-values
    if (len(sys.argv) != 2):
        print("usage error: missing filename")
        return
    filename = sys.argv[1]

    # Read in data from file
    data = ascii.read(filename)
    s_values = list(data["svalue"])
    s_err = list(data["svalue_err"])
    tel = list(data["tel"])

    # Convert times into JD units
    times = [tools.utc_to_jd(datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')) for time in data["time"]]

    # Create lists of all observations of the star.
    # Keep the two instruments separate.
    times_h, s_values_h, s_err_h = [], [], []
    times_a, s_values_a, s_err_a = [], [], []
    for n in range(len(s_values)):
        if (tools.is_value(s_values[n])):
            if (tel[n] == "hires_j"):
                times_h.append(times[n])
                s_values_h.append(s_values[n])
                s_err_h.append(s_err[n])
            if (tel[n] == "apf"):
                times_a.append(times[n])
                s_values_a.append(s_values[n])
                s_err_a.append(s_err[n])

    # Remove data points that are likely errors
    times_h, s_values_h = tools.remove_outliers(times_h, s_values_h)
    times_a, s_values_a = tools.remove_outliers(times_a, s_values_a)

    # Sort data points by time
    tools.bubble_sort(times_h, s_values_h)
    tools.bubble_sort(times_a, s_values_a)

    # Combine points that are under 1 hour apart
    times_h, s_values_h = tools.combine_close_times(times_h, s_values_h)
    times_a, s_values_a = tools.combine_close_times(times_a, s_values_a)

    # Save unfiltered data for comparison
    unfiltered_times = times_h + times_a
    unfiltered_s_values = [s - tools.average_list(s_values_h) for s in s_values_h] \
                        + [s - tools.average_list(s_values_a) for s in s_values_a]

    # Apply filter before combining data. Applying the filter will remove long-term
    # trends that may have affected the two sets separately.
    times_h, s_values_h = bandpass.band_pass_filter(times_h, s_values_h, 1/100, 1/4)
    times_a, s_values_a = bandpass.band_pass_filter(times_a, s_values_a, 1/100, 1/4)

    # Combine the sets from the two instruments.
    times = times_h + times_a
    s_values = s_values_h + s_values_a

    # Sort data points by time... again
    tools.bubble_sort(times, s_values)

    # Makes periodogram model and finds best period
    ls, periods, power, best_period, FAP = plot.periodogram(times, s_values)

    # Scores the best_period
    peak_found = tools.find_peak(ls, power, periods, FAP)
    score = tools.get_score(peak_found, FAP)

    # Finds and prints the astrophysical variance of the period
    # to_print = plot.find_variance(times, s_values, best_period, FAP)

    # Make plot
    alpha = 0.01
    fig, axs = plot.plot(times, s_values, unfiltered_times, unfiltered_s_values, periods, power, ls, best_period, alpha)

    axs[0].set(title='Filtered s-values',
               ylabel='Rel. s-values')

    starname = 'hd{0}'.format(filename.split('/')[-1].split('.')[0])
    # if to_print:
    #     to_print = starname + ',' + to_print
    #     print(to_print)
    fig.suptitle(starname)
    fig.set_size_inches(9, 6)
    plt.show()
    # fig.savefig(os.path.dirname(__file__) + "/../periodograms/cahk/{0}.png".format(starname), dpi=300)

    # Record best period in a file
    # file = open(os.path.dirname(__file__) + "/../cahk_periods_catalog.txt", "a")
    # file.write("{0},{1},{2},{3}\n".format(starname, str(best_period), str(FAP), score))
    # file.close()

if (__name__ == '__main__'):
    main()

import numpy as np
import matplotlib.pyplot as plt
import pandas

from datetime import datetime
import os.path
import sys

import bandpass
import tools
import plot

def main():

    # Gets name of csv file with times and h-alpha values
    if (len(sys.argv) != 2):
        print("usage error: missing filename")
        return
    filename = sys.argv[1]

    file = pandas.read_csv(filename)
    times = list(file["time"])
    tel = list(file['tel'])
    Ha = list(file["Ha"])

    # Create lists of all observations of the star.
    # Keep the two instruments separate.
    star_times_a, star_times_h = [], []
    star_Ha_a, star_Ha_h = [], []
    for i in range(len(Ha)):
        if (tel[i] == 'hires_j'):
            star_times_h.append(times[i])
            star_Ha_h.append(Ha[i])
        else:
            star_times_a.append(times[i])
            star_Ha_a.append(Ha[i])

    # Remove data points that are obviously errors
    star_times_a, star_Ha_a = tools.remove_outliers(star_times_a, star_Ha_a)
    star_times_h, star_Ha_h = tools.remove_outliers(star_times_h, star_Ha_h)

    # Sort data points by time
    tools.bubble_sort(star_times_h, star_Ha_h)
    tools.bubble_sort(star_times_a, star_Ha_a)

    # Combine points that are under 1 hour apart
    star_times_a, star_Ha_a = tools.combine_close_times(star_times_a, star_Ha_a)
    star_times_h, star_Ha_h = tools.combine_close_times(star_times_h, star_Ha_h)

    # Save unfiltered data for comparison
    unfiltered_times = star_times_a + star_times_h
    unfiltered_Ha = [Ha - tools.average_list(star_Ha_a) for Ha in star_Ha_a] \
                  + [Ha - tools.average_list(star_Ha_h) for Ha in star_Ha_h]

    # Apply filter before combining data. Applying the filter will remove long-term
    # trends that may have affected the two sets separately.
    star_times_a, star_Ha_a = bandpass.band_pass_filter(star_times_a, star_Ha_a, 1/100, 1/4)
    star_times_h, star_Ha_h = bandpass.band_pass_filter(star_times_h, star_Ha_h, 1/100, 1/4)

    # Combine the sets from the two instruments.
    star_times = star_times_a + star_times_h
    star_Ha = star_Ha_a + star_Ha_h

    # Sort data points by time... again
    tools.bubble_sort(star_times, star_Ha)

    # Makes periodogram model and finds best period
    ls, periods, power, best_period, FAP = plot.periodogram(star_times, star_Ha)

    # Scores the best_period
    peak_found = tools.find_peak(ls, power, periods, FAP)
    score = tools.get_score(peak_found, FAP)

    # Finds and prints the astrophysical variance of the period
    # to_print = plot.find_variance(star_times, star_Ha, best_period, FAP)

    # # Make historgram of powers
    # fig, ax = plt.subplots(1, 1, tight_layout=True)
    # ax.hist(spower, bins=100, log=True)
    # plt.show()

    # Make plot
    fig, axs = plot.plot(star_times, star_Ha, unfiltered_times, unfiltered_Ha, periods, power, ls, best_period, 0.01)

    axs[0].set(title='Filtered H-alpha values',
               ylabel='Rel. H-alpha values')

    star = filename.split('/')[-1].split('.')[0]
    starname = 'hd{0}'.format(star)
    # if to_print:
    #     to_print = starname + ',' + to_print
    #     print(to_print)
    fig.suptitle(starname)
    fig.set_size_inches(9, 6)
    plt.show()
    # fig.savefig(os.path.dirname(__file__) + "/../periodograms/halpha/{0}.png".format(starname), dpi=500)

    # Record best period in a file
    # file = open(os.path.dirname(__file__) + "/../halpha_periods_catalog.txt", "a")
    # file.write("hd{0},{1},{2},{3}\n".format(star, str(best_period), str(FAP), score))
    # file.close()

if (__name__ == '__main__'):
    main()

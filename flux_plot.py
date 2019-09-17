import numpy as np
import matplotlib.pyplot as plt
import pandas
import statistics

import sys
import os
from datetime import datetime

import bandpass
import tools
import plot

def main():

    # Gets the path to the directory containing the flux data
    if (len(sys.argv) != 2):
        print("usage error: missing filename")
        return
    path = sys.argv[1]

    # Read in data from file
    file = pandas.read_csv(path + 'fluxes.csv', sep=' ')
    times = list(file["time"] + 2400000)
    fluxes = list(file["flux"])

    # Sort data points by time
    tools.bubble_sort(times, fluxes)

    # Combine points that are under 1 hour apart
    times, fluxes = tools.combine_close_times(times, fluxes)

    # Remove data points that are obviously errors
    times, fluxes = tools.remove_outliers(times, fluxes)

    # Save unfiltered data for comparison
    unfiltered_times = times
    unfiltered_fluxes = fluxes

    # Apply band-pass filter.
    times, fluxes = bandpass.band_pass_filter(times, fluxes, 1/70, 1/4)

    # Makes periodogram model and finds best period
    ls, periods, power, best_period, FAP = plot.periodogram(times, fluxes)

    # Scores the best_period
    peak_found = tools.find_peak(ls, power, periods, FAP)
    score = tools.get_score(peak_found, FAP, mode='strict')

    # Finds and prints the astrophysical variance of the period
    ngroups = round((max(times) - min(times)) / 365)

    # Makes plot
    alpha = 0.001
    fig, axs = plot.plot(times, fluxes, unfiltered_times, unfiltered_fluxes, periods, power, ls, best_period, alpha)

    axs[0].set(title='Filtered Flux',
               ylabel='Rel. Flux')

    if (path[-1] == '/'):
        path = path[:-1]
    starname = path.split('/')[-1]
    fig.suptitle(starname)
    fig.set_size_inches(9, 6)

    plt.show()
    # fig.savefig(os.path.dirname(__file__) + "/../periodograms/photometry/{0}.png".format(starname), dpi=300)

    to_print = plot.find_variance(times, fluxes, best_period, FAP, ngroups=ngroups)
    if to_print:
        to_print = starname + ',' + to_print
        print(to_print)

    # Record best period in a file
    # file = open(os.path.dirname(__file__) + "/../flux_periods_catalog.txt", "a")
    # file.write("{0},{1},{2},{3}\n".format(starname, str(best_period), str(FAP), score))
    # file.close()

if (__name__ == '__main__'):
    main()

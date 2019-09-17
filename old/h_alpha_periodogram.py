import numpy as np
import matplotlib.pyplot as plt
import pandas

from astropy.timeseries import LombScargle
from datetime import datetime

import bandpass
from tools import *

def main():
    megafile = pandas.read_csv("../halpha.csv")
    ids = list(megafile["observation_id"])
    times = list(megafile["time"])
    starnames = list(megafile["star"])
    Ha = list(megafile["Ha"])
    C1 = list(megafile["C1"])

    # Convert times from UTC into float
    times = [utc_to_jd(datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')) for time in times]

    # Create list of all star names
    starlist = []
    for starname in starnames:
        if starname not in starlist:
            starlist.append(starname)

    #145675, 201092, 221354
    for star in (217107,):
        print(star)

        # Create lists of all observations of the star.
        # Keep the two instruments separate.
        star_times_a, star_times_h = [], []
        star_Ha_a, star_Ha_h = [], []
        for i in range(len(Ha)):
            if (starnames[i] == star):
                if (ids[i][1] == 'j'):
                    star_times_h.append(times[i])
                    star_Ha_h.append(Ha[i])
                else:
                    star_times_a.append(times[i])
                    star_Ha_a.append(Ha[i])

        # # # # # # # # # # # # # # # #
        # Data Processing Begins Here #
        # # # # # # # # # # # # # # # #

        # Remove data points that are obviously errors
        star_times_a, star_Ha_a = remove_outliers(star_times_a, star_Ha_a)
        star_times_h, star_Ha_h = remove_outliers(star_times_h, star_Ha_h)

        # Apply filter before combining data. Applying the filter will remove long-term
        # trends that may have affected the two sets separately.
        star_times_a, star_Ha_a = bandpass.band_pass_filter(star_times_a, star_Ha_a, 1/100, 1/4)
        star_times_h, star_Ha_h = bandpass.band_pass_filter(star_times_h, star_Ha_h, 1/100, 1/4)

        # Combine the sets from the two instruments.
        star_times = star_times_a + star_times_h
        star_Ha = star_Ha_a + star_Ha_h

        # Create Lomb-Scargle Periodogram model
        ls = LombScargle(star_times, star_Ha)
        baseline = max(star_times) - min(star_times)
        frequency, power = ls.autopower(minimum_frequency=1/baseline, maximum_frequency=1/2)
        periods = 1 / frequency

        # Find the best period within a reasonable range
        best_power = 0
        best_period = 1
        for i, p in enumerate(power):
            if (periods[i] > 4 and periods[i] < 80):
                if (p > best_power):
                    best_power = p
                    best_period = periods[i]

        # # # # # # # # # # # # # # #
        # Data Processing Ends Here #
        # # # # # # # # # # # # # # #

        FAP = ls.false_alarm_probability(best_power)
        alpha = 0.001

        # Record best period in a file
        # if (FAP < 1):
        #     file = open("/Users/Ilya/Desktop/SURF/halpha_periods_catalog.txt", "a")
        #     file.write("hd{0}\t{1}\t{2}\n".format(star, str(best_period), str(FAP)))
        #     file.close()

        # Make plot
        fig, axs = plt.subplots(3, 1, sharex=False)

        # Plot filtered data
        axs[0].plot(star_times, star_Ha, 'k.')
        axs[0].set(title="hd{0}".format(star))

        # Plot periodogram
        axs[1].plot(periods, power, 'k-')
        axs[1].set(xlim=(min(periods), max(periods)),
                   ylim=min(power),
                   xlabel='Period (JD)',
                   ylabel='Lomb-Scargle Power',
                   xscale='log')

        # Plot phased data
        phased_t = [time % float(best_period) for time in star_times]
        axs[2].plot(phased_t, star_Ha, 'k.')

        # Plot best-fit model on top of phased data
        n = 300
        model_t = [i / n * float(best_period) for i in range(n)]
        y_fit = ls.model(model_t, 1/best_period)
        axs[2].plot(model_t, y_fit, 'b.')

        # Add line to periodogram representing FAP = alpha
        n = 100
        x_values = [1.3**i for i in range(n)] + [1.11]
        y_values_alpha = [ls.false_alarm_level(alpha) for i in range(n + 1)]
        axs[1].plot(x_values, y_values_alpha, 'b_')
        axs[1].legend(["{0} FAP".format(alpha)], loc="upper right", frameon=False, handlelength=0)

        # Plot aliases, harmonics and sampling periods on the periodogram as vertical lines.
        f_sampling = [1/1, 1/29.5, 1/365]
        aliases, harmonics = find_aliases(1 / best_period, [-2, -1, 1, 2], f_sampling)
        for alias in aliases:
            axs[1].axvline(alias, c="grey")
        for harmonic in harmonics:
            axs[1].axvline(harmonic, c="blue")
        for f in f_sampling:
            axs[1].axvline(1/f, c="green")

        plt.show()

if (__name__ == '__main__'):
    main()

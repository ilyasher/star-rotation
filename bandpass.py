import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from astropy.io import ascii
from astropy.timeseries import LombScargle
import os
import sys
from datetime import datetime
from dateutil import tz
import statistics
from scipy import signal
from random import random
import math

from tools import *

def moving_average_filter(t, y, m, min_n):
    """
    Arguments:
    t - time array
    y - value array
    m - kernel length

    Returns filtered value array
    """

    new_t = []
    new_y = []

    for i, value in enumerate(y):
        sum = 0
        time_at_value = t[i]
        n = 0
        for j, time in enumerate(t):
            if (abs(time - time_at_value) <= m / 2):
                sum += y[j];
                n += 1
        if (n >= min_n):
            sum /= n
            new_t.append(time_at_value)
            new_y.append(sum)

    return new_t, new_y

def low_pass_filter(t, y, f_max):
    return moving_average_filter(t, y, 1/f_max, 1)

def high_pass_filter(t, y, f_min):
    low_pass_t, low_pass_y = moving_average_filter(t, y, 1/f_min, 3)
    return low_pass_t, [y[t.index(time)] - low_pass_y[low_pass_t.index(time)] for time in low_pass_t]

def band_pass_filter(t, y, f_min, f_max):
    t, y = high_pass_filter(t, y, f_min)
    return low_pass_filter(t, y, f_max)

def find_best_period(t, y, FAP=False, return_model=False):
    baseline = max(t) - min(t)
    ls = LombScargle(t, y)
    frequency, power = ls.autopower(minimum_frequency=1/baseline, maximum_frequency=1/2)
    periods = 1 / frequency
    best_power = power.max()
    best_period = periods[list(power).index(best_power)]
    if (FAP):
        FAP = ls.false_alarm_probability(best_power)
        if (return_model):
            return (best_period, FAP, ls)
        else:
            return (best_period, FAP)
    else:
        if (return_model):
            return (best_period, ls)
        else:
            return best_period

def main():

    # generate sparse, uneven times from 0-5000 days

    filename = "rv/110897.csv"

    # Read in data from file
    data = ascii.read(filename)
    s_values = list(data["svalue"])
    s_err = list(data["svalue_err"])
    tel = list(data["tel"])

    # Convert times into JD units
    times = [utc_to_jd(datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')) for time in data["time"]]

    # Create lists of all observations of the star.
    # Keep the two instruments separate.
    times_h, times_a = [], []
    for i in range(len(s_values)):
        if (is_value(s_values[i])):
            if (tel[i] == "hires_j"):
                times_h.append(times[i])
            if (tel[i] == "apf"):
                times_a.append(times[i])

    t = []
    sig = []
    for times, sigma in ((times_a, 0.2), (times_h, 0.1)):
        for time in times:

            value = 0

            # add long-term magnetic cycles (3000 day period)
            value += math.sin(1/3000 * time * 2 * math.pi)

            # add rotational period (21 day period)
            value += 0.3 * math.sin(1/21 * time * 2 * math.pi)

            # add noise

            # use a normal distribution sigma = 0.005
            value += sigma * (np.random.normal(0, sigma))
            print(np.random.normal(0, sigma))

            sig.append(value)
            t.append(time)

    print(len(t))

    def print_best_period(t, y):
        best_period, fap = find_best_period(t, y, FAP=True)
        print("Period: {0:.2f}, FAP: {1:.4f}".format(best_period, fap))

    fig, ((ax1, ax4), (ax2, ax5), (ax3, ax6)) = plt.subplots(3, 2, sharex=False)
    ax1.plot(t, sig, "b.")
    ax1.set_title('Simulated S-values')
    # ax1.axis([min(t), max(t), -2, 4])

    def periodogram(ax, t, sig):
        alpha = 0.001
        baseline = max(t) - min(t)
        ls = LombScargle(t, sig)
        frequency, power = ls.autopower(minimum_frequency=1/baseline, maximum_frequency=1/2)
        periods = 1 / frequency

        ax.plot(periods, power, 'k-')
        ax.set(xlim=(min(periods), max(periods)),
               ylim=min(power),
               xlabel='Period (JD)',
               ylabel='Lomb-Scargle Power',
               xscale='log')

        # Add line to periodogram representing FAP = alpha
        n = 100
        x_values = [1.3**i for i in range(n)] + [1.11]
        y_values_alpha = [ls.false_alarm_level(alpha) for i in range(n + 1)]
        ax.plot(x_values, y_values_alpha, 'b_')
        ax.legend(["{0} FAP".format(alpha)], loc="upper right", frameon=False, handlelength=0)

        best_period = find_best_period(t, sig)

        # Plot aliases, harmonics and sampling periods on the periodogram as vertical lines.
        f_sampling = [1/1, 1/29.5, 1/365]
        aliases, harmonics = find_aliases(1 / best_period, [-1, 1], f_sampling)
        for alias in aliases:
            ax.axvline(alias, c="grey", lw=0.8)
        for harmonic in harmonics:
            ax.axvline(harmonic, c="blue", lw=0.8)
        for f in f_sampling:
            ax.axvline(1/f, c="green", lw=0.8)

    periodogram(ax4, t, sig)

    # filter out magnetic cycles (remove periods > 100 days)
    t, high_filtered = high_pass_filter(t, sig, 1/100)

    ax2.plot(t, high_filtered, "b.")
    ax2.set_title('After 100-day high-pass filter')
    # ax2.axis([min(t), max(t), -2, 4])
    print_best_period(t, high_filtered)

    periodogram(ax5, t, high_filtered)

    # filter out low periods (remove periods < 4 days)
    t, low_filtered = low_pass_filter(t, high_filtered, 1/4)

    ax3.plot(t, low_filtered, "b.")
    ax3.set_title('After additional 4-day low-pass filter')
    # ax3.axis([min(t), max(t), -2, 4])
    ax3.set_xlabel('Time (days)')
    print_best_period(t, low_filtered)

    periodogram(ax6, t, low_filtered)

    plt.tight_layout()
    plt.show()

if (__name__ == '__main__'):
    for i in range(10):
        main()

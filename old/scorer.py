import numpy as np
import matplotlib.pyplot as plt

from astropy.io import ascii
from astropy.timeseries import LombScargle
import sys
import os
from datetime import datetime

import bandpass
from tools import *

def main():

    score_dict = {"excellent": 5, "good": 3, "ok": 2, "poor": 1, "bad": 0}
    # score_dict = {"excellent": 2, "good": 1, "ok": 1, "poor": 1, "bad": 0}

    data_flux = ascii.read("flux_periods_catalog.txt")
    data_cahk = ascii.read("cahk_periods_catalog.txt")
    data_halpha = ascii.read("halpha_periods_catalog.txt")

    stars, periods, scores = [], [], []
    for data in ([], data_cahk, data_halpha):
        stars += list(data["star"])
        periods += list(data["period"])
        scores += list(data["score"])

    star_dict = dict()

    for star in stars:
        star_dict[star] = []

    for i, period in enumerate(periods):
        star = stars[i]
        score = scores[i]
        star_dict[star].append((period, score))

    def within_percent(a, b, percent):
        percent /= 100
        if (a * b == 0):
            return False
        if (abs((a - b) / b) < percent):
            return True
        if (abs((a - b) / a) < percent):
            return True
        return False

    for star in star_dict:
        periods = star_dict[star]
        scores = []
        period_dict = dict()
        for test_period in periods:
            period_score = 0
            f_sampling = [1/1, 1/29.5, 1/365]
            aliases, harmonics = find_aliases(1 / test_period[0], [1, 2], f_sampling)
            for period in periods:
                score = period[1]
                if (within_percent(test_period[0], period[0], 5)):
                    if score in score_dict:
                        period_score += score_dict[period[1]]
                # for alias in aliases + harmonics:
                #     if (within_percent(alias, period[0], 3)):
                #         if score in score_dict:
                #             period_score += score_dict[period[1]] / 2
            period_dict[test_period[0]] = period_score
        star_dict[star] = period_dict
    # print(star_dict)

    print('star,period,score')
    for star in star_dict:
        star_periods = star_dict[star]
        best_score = -1
        best_period = 0
        for period in star_periods:
            score = star_periods[period]
            if (score > best_score):
                best_score = score
                best_period = period
        print("{0},{1},{2}".format(star, best_period, best_score))

if (__name__ == '__main__'):
    main()

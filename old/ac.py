import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import ascii
from gatspy.periodic import LombScargleFast
from astropy.timeseries import LombScargle
from statsmodels.tsa.stattools import acf
import os

def mag_to_flux(mag):
    return pow(10, 0.4 * -mag)

def average(list):
    sum = 0
    for element in list:
        sum += element
    return sum / len(list)

def normalize(list):
    av = average(list)
    newlist = []
    for element in list:
        newlist.append(element / av)
    return newlist

def poly_value(poly, x):
    return poly[0] * x * x + poly[1] * x + poly[2]

def residuals(x, y, n):
    x = np.array(x)
    y = np.array(y)

    # z = [a, b, c] where fit = ax2 + by + c
    z = np.polyfit(x, y, n)

    new_y = []
    for i, value in enumerate(y):
        # print(poly_value(z, x[i]))
        # print(value - poly_value(z, x))
        new_y.append(value - poly_value(z, x[i]))
    return (x, new_y)

def main():
    names = ["d-abc_f.by", "d-abc_f.by.001", "d-abc_f.by.002", "d-ab_f.by", "d-ac_f.by", "d-ab_f.by", "c-ab_f.by", "d-bc_f.by", "c-a_f.by", "d-b_f.by", "d-a_f.by"]
    names_index = 0

    while (names_index < 15):
        filename = names[names_index]
        try:
            file = open(filename)
            break
        except:
            names_index += 1
            continue

    rounded_file = open("rounded.by", "w")
    first_line = True
    last_day = 0
    steps_per_day = 10
    for line in file.readlines():
        words = line.split()
        day = round(float(words[0]) * steps_per_day)
        flux = float(words[1])
        if (first_line):
            first_line = False
            rounded_file.write(str(day) + "\t" + str(flux) + "\n")
            last_day = day
            continue
        if (last_day == day):
            continue
        last_day += 1
        while (last_day != day):
            rounded_file.write(str(last_day) + "\t0\n")
            last_day += 1
        rounded_file.write(str(day) + "\t" + str(flux) + "\n")
    file.close()
    rounded_file.close()

    data = ascii.read("rounded.by")
    fluxes = data["col2"]


    ac = acf(fluxes, nlags=1000)
    print(ac)
    fig, ax = plt.subplots()
    ax.plot(ac, 'k-')
    plt.show()


    # alpha = 0.01
    # file = open("/Users/Ilya/Desktop/SURF/best_periods_using_fap.txt", "a")
    # if (best_power > ls.false_alarm_level(alpha)):
    #     file.write("{0} {1}\n".format(starname, best_period))
    # else:
    #     file.write("{0}\n".format(starname))
    # file.close()
    #
    # # make phased data
    # if (best_power > ls.false_alarm_level(alpha)):
    #     data = ascii.read(filename)
    #     phased_t = []
    #     for element in t:
    #         phased_t.append(element % best_period)
    #     y_fit = ls.model(phased_t, 1/best_period)
    #     fig, ax = plt.subplots()
    #     ax.plot(phased_t, mag, 'k.')
    #     ax.plot(phased_t, y_fit, 'b.')
    #     plt.savefig("phased.png")
    #     plt.show()
    #
    #
    # length = 100
    # x_values = [1.3**n for n in range(length)] + [1.11]
    # y_values_10 = [fa_levels[0] for n in range(length + 1)]
    # y_values_05 = [fa_levels[1] for n in range(length + 1)]
    # y_values_01 = [fa_levels[2] for n in range(length + 1)]
    #
    # fig, ax = plt.subplots()
    # ax.plot(periods, power, 'k-')
    # ax.plot(x_values, y_values_01, 'b*', markersize=4)
    # ax.plot(x_values, y_values_05, 'b.', markersize=4)
    # ax.plot(x_values, y_values_10, 'b_')
    # ax.set(xlim=(2, baseline * 5),
    #        ylim=min(power),
    #        xlabel='period (days)',
    #        ylabel='Lomb-Scargle Power',
    #        xscale='log',
    #        title='{0}'.format(starname),
    #        )
    # ax.legend(["Best Period: {0:.3f} days".format(best_period),
    #            "0.01 FAP", "0.05 FAP", "0.10 FAP"], loc="center right", frameon=False, handlelength=0)
    # plt.savefig("adjusted_periodogram.png")


if (__name__ == '__main__'):
    main()

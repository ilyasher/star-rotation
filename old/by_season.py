import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import ascii
from gatspy.periodic import LombScargleFast
from astropy.timeseries import LombScargle
import bandpass
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
    value = 0
    for n, coefficient in enumerate(poly):
        value += coefficient * (x ** (len(poly) - n - 1))
    return value

def residuals(x, y, n):
    x = np.array(x)
    y = np.array(y)

    # z = [a, b, c] where fit = ax2 + bx + c
    z = np.polyfit(x, y, n)

    new_y = []
    for i, value in enumerate(y):
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

    season_lengths = []
    last_day = 0
    curr_season_length = 0
    for line in file.readlines():
        words = line.split()
        day = float(words[0])
        if (day - last_day > 1000): #first line
            last_day = day
            curr_season_length += 1
            continue
        if (day - last_day > 50): #fix
            season_lengths.append(curr_season_length)
            curr_season_length = 0
        last_day = day
        curr_season_length += 1
    season_lengths.append(curr_season_length)
    file.close()

    newfile = open("seasons.by", "w")
    file = open(filename)

    print("Season\tn\tBest Period\tFAP\tp < 0.05 ?")
    print("-" * 50)

    t = []
    mag = []
    for season_number, season_length in enumerate(season_lengths):
        times = []
        fluxes = []
        for n in range(season_length):
            words = file.readline().split()
            times.append(float(words[0]))
            fluxes.append(float(words[1]))
        times, fluxes = residuals(times, fluxes, 2)
        # fluxes = bandpass.band_pass_filter(times, fluxes, 1/100, 1/4)
        for n in range(season_length):
            newfile.write(str(times[n]) + " " + str(fluxes[n]) + "\n")
        newfile.write("\n")

        # group seasons
        groups_of = 6
        t += list(times)
        mag += list(fluxes)
        if ((season_number + 1) % groups_of == 0 or season_number + 1 == len(season_lengths)):
            pass
        else:
            continue
        first_season = season_number - groups_of + 2
        if (season_number + 1 == len(season_lengths)):
            first_season = season_number - (season_number % groups_of) + 1

        dmag = 1 #arbitrary, doesn't affect anything
        baseline = max(t) - min(t)

        ls = LombScargle(t, mag)
        frequency, power = ls.autopower(minimum_frequency=1/baseline, maximum_frequency=1/2)
        periods = 1 / frequency

        best_power = power.max()
        best_period = periods[list(power).index(best_power)]

        alpha = 0.05
        print("{0}-{4}\t{1}\t{2:.3f}\t\t{3:.4f}\t".format(first_season, len(t), best_period, ls.false_alarm_probability(best_power), season_number + 1), end="")
        if (best_power > ls.false_alarm_level(alpha)):
            print("True")
        else:
            print("False")
        t = []
        mag = []

    newfile.close()
    file.close()

    data = ascii.read("seasons.by")
    # fig = plt.plot(data["col1"], data["col2"], 'k.')
    # plt.xlabel("Day", fontsize=10)
    # plt.ylabel("Res. Flux", fontsize=10)
    # plt.title("Residuals of Relative Flux", fontsize=15)
    # plt.savefig("residuals.png")

    # make periodogram
    t = data["col1"]
    mag = data["col2"]
    dmag = 1 #arbitrary, doesn't affect anything
    baseline = max(t) - min(t)

    cwd = os.getcwd()
    starname = cwd.split('/')[-1];

    ls = LombScargle(t, mag)
    frequency, power = ls.autopower(minimum_frequency=1/baseline, maximum_frequency=1/2)
    periods = 1 / frequency

    best_power = power.max()
    best_period = periods[list(power).index(best_power)]

    probabilities = [0.1, 0.05, 0.01]
    fa_levels = ls.false_alarm_level(probabilities)

    print("1-{0}\t{1}\t{2:.3f}\t\t{3:.4f}\t".format(len(season_lengths), len(t), best_period, ls.false_alarm_probability(best_power)), end="")
    alpha = 0.01
    if (best_power > ls.false_alarm_level(alpha)):
        print("True")
    else:
        print("False")

    # file = open("/Users/Ilya/Desktop/SURF/best_periods_using_fap.txt", "a")
    # if (best_power > ls.false_alarm_level(alpha)):
    #     file.write("{0} {1}\n".format(starname, best_period))
    # else:
    #     file.write("{0}\n".format(starname))
    # file.close()

    # make phased data
    # if (best_power > ls.false_alarm_level(alpha)):
    # data = ascii.read(filename)
    # phased_t = []
    # for element in t:
    #     phased_t.append(element % best_period)
    # y_fit = ls.model(phased_t, 1/best_period)
    # fig, ax = plt.subplots()
    # ax.plot(phased_t, mag, 'k.')
    # ax.plot(phased_t, y_fit, 'b.')
    # plt.savefig("phased.png")
    # plt.show()


    length = 100
    x_values = [1.3**n for n in range(length)] + [1.11]
    y_values_10 = [fa_levels[0] for n in range(length + 1)]
    y_values_05 = [fa_levels[1] for n in range(length + 1)]
    y_values_01 = [fa_levels[2] for n in range(length + 1)]

    fig, ax = plt.subplots()
    ax.plot(periods, power, 'k-')
    ax.plot(x_values, y_values_01, 'b*', markersize=4)
    ax.plot(x_values, y_values_05, 'b.', markersize=4)
    ax.plot(x_values, y_values_10, 'b_')
    ax.set(xlim=(2, baseline * 5),
           ylim=min(power),
           xlabel='period (days)',
           ylabel='Lomb-Scargle Power',
           xscale='log',
           title='{0}'.format(starname),
           )
    ax.legend(["Best Period: {0:.3f} days".format(best_period),
               "0.01 FAP", "0.05 FAP", "0.10 FAP"], loc="center right", frameon=False, handlelength=0)
    plt.show()
    # plt.savefig("adjusted_periodogram.png")


if (__name__ == '__main__'):
    main()

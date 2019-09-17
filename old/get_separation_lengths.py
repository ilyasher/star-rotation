import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from astropy.io import ascii
from gatspy.periodic import LombScargleFast
from astropy.timeseries import LombScargle
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
    for line in file.readlines():
        words = line.split()
        day = round(float(words[0]))
        flux = float(words[1])
        rounded_file.write(str(day) + "\t" + str(flux) + "\n")
    file.close()
    rounded_file.close()

    # newfile = open("seasons.by", "w")
    # file = open(filename)
    # #
    # # for season_length in season_lengths:
    # #     times = []
    # #     fluxes = []
    # #     for n in range(season_length):
    # #         words = file.readline().split()
    # #         times.append(float(words[0]))
    # #         fluxes.append(float(words[1]))
    # #     times, fluxes = residuals(times, fluxes, 2)
    # #     for n in range(season_length):
    # #         newfile.write(str(times[n]) + " " + str(fluxes[n]) + "\n")
    # #     newfile.write("\n")
    # #
    # # newfile.close()
    # # file.close()
    # #
    # #

if (__name__ == '__main__'):
    main()

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter

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

def purge_outliers(list):
    newlist = []
    threshold = 1000
    for i in list:
        if (i < threshold):
            newlist.append(i)
    return newlist

def main():
    file = open("best_periods.txt", "r")
    periods = []
    for line in file.readlines():
        words = line.split()
        try:
            del words[0]
            star_periods = [float(i) for i in words]
            periods += star_periods
        except:
            continue
    file.close()

    periods = purge_outliers(periods)

    n_buckets = 20

    fig, axs = plt.subplots()
    axs.hist(periods, n_buckets, color="b")
    axs.set(xlabel='Period (days)',
           ylabel='Frequency',
           title='Best Periods',
           xlim=0,
           )

    plt.show()

if (__name__ == '__main__'):
    main()

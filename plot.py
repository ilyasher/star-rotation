import numpy as np
import statistics
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib import gridspec
from astropy.timeseries import LombScargle
import tools

def periodogram(times, data):

    # Create Lomb-Scargle Periodogram model
    ls = LombScargle(times, data)
    baseline = max(times) - min(times)
    frequency, power = ls.autopower(minimum_frequency=1/baseline, maximum_frequency=1/(1/10))
    periods = 1 / frequency

    # Find the best period within a reasonable range
    best_power = 0
    best_period = 1
    for i, p in enumerate(power):
        if (periods[i] > 4 and periods[i] < 70):
            if (p > best_power):
                best_power = p
                best_period = periods[i]

    FAP = ls.false_alarm_probability(best_power)

    return ls, periods, power, best_period, FAP

def plot(times, data, unfiltered_times, unfiltered_data, periods, power, ls, best_period, alpha=0.001):
    # Make plot.
    fig = plt.figure(constrained_layout=True)
    gs = gridspec.GridSpec(3, 2, figure=fig)
    f_pdgm = fig.add_subplot(gs[0, 0:])
    u_pdgm = fig.add_subplot(gs[1, 0:])
    u_data = fig.add_subplot(gs[2, 0])
    p_data = fig.add_subplot(gs[2, 1])
    axs = (u_data, u_pdgm, f_pdgm, p_data)

    # Plot filtered data.
    years = tools.jd_to_years(np.array(times))
    axs[0].plot(years, data, 'k.')
    axs[0].set(title='Filtered Flux',
               xlabel='Year',
               ylabel='Rel. Flux')

    # Plot Periodogram.
    u_ls, u_periods, u_power, _, _ = periodogram(unfiltered_times, unfiltered_data)
    axs[1].plot(u_periods, u_power, 'k-')
    axs[1].set(xlim=(1, 10000),
               ylim=0,
               xlabel='Period (days)',
               ylabel='Power',
               # title='LS Periodogram (Unfiltered)',
               xscale='log',)
    axs[1].xaxis.set_major_formatter(mticker.ScalarFormatter())

    # Plot Periodogram.
    axs[2].plot(periods, power, 'k-')
    axs[2].set(xlim=(1, 10000),
               ylim=0,
               # xlabel='Period (days)',
               ylabel='Power',
               title='LS Periodogram (Filtered and Unfiltered)',
               xscale='log',
               )
    axs[2].set(xticklabels = [])

    # Plot phased data.
    phased_t = [time % float(best_period) for time in times]
    axs[3].plot(phased_t, data, 'k.')
    axs[3].set(xlim=(0, best_period),
               xlabel='Cycle day',
               yticklabels = [],
               title='Data phased to {0:.1f} days'.format(best_period))

    # Plot best-fit model on top of phased data
    n = 300
    model_t = [i / n * float(best_period) for i in range(n)]
    y_fit = ls.model(model_t, 1/best_period)
    axs[3].plot(model_t, y_fit, 'b.')

    # Add line to periodogram representing FAP = alpha
    n = 100
    x_values = [1.3**i for i in range(n)] + [1.11]
    y_values_alpha = [ls.false_alarm_level(alpha) for i in range(n + 1)]
    u_y_values_alpha = [u_ls.false_alarm_level(alpha) for i in range(n + 1)]
    axs[2].plot(x_values, y_values_alpha, 'b_')
    axs[1].plot(x_values, u_y_values_alpha, 'b_')
    for ax in axs[1], axs[2]:
        ax.legend(["{0} FAP".format(alpha)], loc="upper right", frameon=False, handlelength=0)

    # Plot aliases, harmonics and sampling periods on the periodogram as vertical lines.
    f_sampling = [1/1, 1/29.5, 1/365]
    aliases, harmonics = tools.find_aliases(1 / best_period, [-2, -1, 1, 2], f_sampling)
    for alias in aliases:
        axs[2].axvline(alias, c="grey", lw=0.8)
    for harmonic in harmonics:
        axs[2].axvline(harmonic, c="blue", lw=0.8)
    for f in f_sampling:
        axs[2].axvline(1/f, c="green", lw=0.8)
        axs[1].axvline(1/f, c="green", lw=0.8)

    return fig, axs

def find_variance(times, values, best_period, FAP,ngroups=0):
    # print('{}\t{}\t{}\t{}'.format('i', 'n', 'period', 'logFAP'))
    # print('{}\t{}\t{}\t{}'.format('all', len(times), round(best_period, 3), round(np.log10(FAP), 3)))
    if not ngroups:
        ngroups = round(len(times)/30)
    grouped_times, grouped_fluxes = tools.group_by_distance(times, values, ngroups)
    periods = []
    for i, time_group in enumerate(grouped_times):
        flux_group = grouped_fluxes[i]

        # Makes periodogram model and finds best period
        ls, _, _, g_best_period, g_FAP = periodogram(time_group, flux_group)

        # # Find signal-to-noise ratio
        # n = 500
        # model_t = [i / n * float(g_best_period) for i in range(n)]
        # y_fit = ls.model(model_t, 1/g_best_period)
        # signal_amplitude = 0.5 * (max(y_fit) - min(y_fit))
        # noise_amplitude = 2 * statistics.stdev(flux_group) / pow(len(time_group), 0.5)
        # sn_ratio = signal_amplitude / noise_amplitude

        if np.log10(g_FAP) < -1.3 and abs(g_best_period - best_period) / best_period < 0.25:
            periods.append(g_best_period)
            # print('{}\t{}\t{:.3f}\t{:.3f}'.format(i, len(time_group), g_best_period, np.log10(g_FAP)))

    if len(periods) >= 3:
        if abs(statistics.mean(periods) - best_period) < statistics.stdev(periods):
            return '{:.3f},{:.3f},{:.3f},{}'.format(
                        statistics.mean(periods), statistics.stdev(periods),
                        statistics.variance(periods), len(periods))
    return 0

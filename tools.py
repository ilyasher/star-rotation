from datetime import datetime
import statistics
import math
import numpy as np

def is_value(value):
    """Determines whether a variable is a positive number."""
    try:
        return value > 0
    except TypeError:
        return False

def utc_to_jd(utc):
    """
    Takes a time in the format 'YYYY-MM-DD HR:MN:SC.MSC'
    and returns the number of days between the time and an arbitrary
    time in the past (Nov 24, -4713).
    """
    t_0 = datetime.strptime('1990-1-01 00:00:00.000', '%Y-%m-%d %H:%M:%S.%f')
    difference = utc - t_0
    seconds = difference.total_seconds()
    seconds_per_day = 86400
    days = round(seconds / seconds_per_day, 5)
    return days + 2447892.5

def jd_to_years(jd):
    """
    Returns the JD in years.
    """
    days_since_1990 = jd - 2447892.5
    return 1990 + days_since_1990 / 365.2422

def remove_outliers(times, values, r=0):
    """
    Returns the list of times and values with all outliers (points more
    than 4 stdev from median) removed.
    Median is used instead of mean because the mean may be affected by outliers.
    """
    if (r > 3):
        return times, values

    new_times = []
    new_values = []

    stdev = statistics.stdev(values)
    median = statistics.median(values)

    for n in range(len(times)):
        if (abs(values[n] - median) < 4 * stdev):
            new_times.append(times[n])
            new_values.append(values[n])

    return remove_outliers(new_times, new_values, r + 1)

def zero_outliers(values):
    """
    Returns the list with all outliers (points more than 4 stdev from median)
    set to the median.
    Median is used instead of mean because the mean may be affected by outliers.
    """
    new_values = []

    stdev = statistics.stdev(values)
    median = statistics.median(values)

    for n in range(len(values)):
        if (abs(values[n] - median) < 4 * stdev):
            new_values.append(values[n])
        else:
            new_values.append(median)

    return new_values

def average_list(lst):
    if lst:
        return sum(lst) / len(lst)
    return 0

def bubble_sort(times, values):
    n = len(times)
    for i in range(n):
        # Last i elements are already in place
        for j in range(0, n-i-1):
            if times[j] > times[j+1] :
                times[j], times[j+1] = times[j+1], times[j]
                values[j], values[j+1] = values[j+1], values[j]

def combine_close_times(times, values, minimum_time=1/24):
    """
    Combines data points that are less minimum_time apart
    and returns the data.
    Issues: loses last data point cluster
    """
    new_times, new_values = [], []
    times_buffer, values_buffer = [], []
    for i, time in enumerate(times):
        if times_buffer and time > times_buffer[0] + minimum_time:
            new_times.append(average_list(times_buffer))
            new_values.append(average_list(values_buffer))
            times_buffer, values_buffer = [], []
        times_buffer.append(time)
        values_buffer.append(values[i])

        if i + 1 == len(times):
            new_times.append(average_list(times_buffer))
            new_values.append(average_list(values_buffer))

    return new_times, new_values

def group_by_n(times, values, sep=100):
    """
    Returns times and values separated into groups.
    Default is 100 elements per group.
    """
    times_groups, values_groups = [], []
    times_group, values_group = [], []
    for i in range(len(times)):
        times_group.append(times[i])
        values_group.append(values[i])
        if ((i + 1) % sep == 0 or i + 1 == len(times)):
            times_groups.append(times_group)
            values_groups.append(values_group)
            times_group, values_group = [], []
    return times_groups, values_groups

def group_by_distance(times, values, ngroups=5):
    """
    Returns times and values separated into groups.
    Groups are determined based on proximity of data points.
    """

    if not times:
        return [], []

    d_times = [times[i] - times[i - 1] for i in range(1, len(times))]
    d_times = np.flip(np.sort(d_times))
    d_times = np.log10(d_times)

    log_threshold = d_times[ngroups - 1]

    times_groups, values_groups = [], []
    times_group, values_group = [], []
    times_group.append(times[0])
    values_group.append(values[0])
    for i in range(1, len(times) + 1):
        # Separate if time separation is above the threshold
        if (i == len(times) or np.log10(times[i] - times[i - 1]) > log_threshold):
            # Can't find a good period with fewer than 10 points
            if len(times_group) >= 10:
                times_groups.append(times_group)
                values_groups.append(values_group)
            # We've reached the end!
            if (i == len(times)):
                break
            times_group, values_group = [], []
        times_group.append(times[i])
        values_group.append(values[i])

    return times_groups, values_groups

def find_aliases(f, m, fs):
    """
    Returns the harmonic periods and alias periods given the sampling frequencies.
    Aliases are found using the formulas
    f_alias = f + m * f_sampling
    f_alias = -f + m * f_sampling
    Where m is an integer.

    Example: aliases, harmonics = find_aliases(f, (-1, 1), (1/1, 1/29.5, 1/365))
    """
    alias_frequencies = []
    harmonic_frequencies = []
    for sample_frequency in fs:
        for alias_number in m:
            alias_frequencies.append(f + alias_number * sample_frequency)
            alias_frequencies.append(-f + alias_number * sample_frequency)
    harmonic_frequencies += [2 * f, 3 * f, 4 * f]

    alias_periods = [abs(1 / alias) for alias in alias_frequencies if alias != 0]
    harmonic_periods = [1 / harmonic for harmonic in harmonic_frequencies]

    return alias_periods, harmonic_periods

def find_peak(ls, power, periods, FAP):
    """
    Returns True if there is a clear peak in the periodogram between 4-70 days.
    """
    # Searches for periods from 4-70 days
    spower = [pwr for i, pwr in enumerate(power) if periods[i] < 100 and periods[i] > 2]

    # Sorts in descending order
    spower = np.sort(spower)[::-1]

    # Candidate peak (first item in list of descending powers)
    best_power = spower[0]
    best_period = periods[list(power).index(best_power)]

    # Examine peaks that are are also high (at least 25% as likely as the
    # top peak). If they are close enough to the first peak or aliases,
    # the top peak is OK.
    for pwr in spower:
        fap_pwr = ls.false_alarm_probability(pwr)

        # Look through peaks until they are relatively unlikely compared to the highest peak
        if FAP * 4 < fap_pwr or fap_pwr > 0.5:
            return True

        period = periods[list(power).index(pwr)]

        ### Compare periods in frequency space:
        ### error = (1/x - 1/y) / (1/y) = y/x - 1, y is expected, x is actual

        # Contender peak close to original
        if abs(best_period / period - 1) < 0.1:
            continue

        # Contender peak close to 60d (often has high power because it is ~1/6 of 365d)
        # If there is a peak at 60d, the unfiltered periodogram should be examined too.
        if abs(60 / period - 1) < 0.05:
            continue

        f_sampling = [1/1, 1/29.5, 1/365]
        f_sampling = [1/1, 1/29.5, 1/365]
        def is_alias():
            aliases, harmonics = find_aliases(1/best_period, [1,], f_sampling)
            for alias in aliases:
                if abs(alias / period - 1) < 0.05:
                    return True
            for harmonic in harmonics:
                if abs(harmonic / period - 1) < 0.1:
                    return True
            return False

        # Contender peak is an alias or harmonic of highest peak
        if is_alias():
            continue

        # Contender peak is a problem
        return False

    # This never happens
    return True

def get_score(peak_found, FAP, mode='lax'):
    """
    Automatically assess the quality of the recovered period based on the
    False alarm probability and whether a clear peak was found.
    Returns 'bad', 'poor', 'ok', 'good', or 'excellent'
    """

    p_min, p_good, p_excellent = 0.05, 0.01, 0.0001
    if mode == 'strict':
        p_min, p_good, p_excellent = 0.01, 0.001, 0.00001

    if FAP > p_min:
        return 'bad'
    if FAP > p_good:
        if peak_found:
            return 'ok'
        return 'bad'
    if FAP > p_excellent:
        if peak_found:
            return 'good'
        return 'poor'
    if peak_found:
        return 'excellent'
    return 'ok' # this case is hopefully rare

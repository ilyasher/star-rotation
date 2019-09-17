import pandas
import matplotlib.pyplot as plt
import statistics
import numpy as np
import scipy.stats

if __name__ == '__main__':
    catalog = pandas.read_csv('star_catalog.csv')
    encyclopedia = pandas.read_csv('specmatch_results.csv')
    # catalog = catalog.query('score >= 3')
    # catalog = catalog.query('period > 0 and stdev > 0')

    stars = catalog['star']
    stars = [star[2:] for star in stars]

    def median(lst):
        lst = [float(element) for element in lst]
        return statistics.median(list(lst))

    spreadsheet_keys = {'teff':'teff', 'logg':'logg', 'fe':'fe', 'vsini':'vsini',
                        'mass':'iso_mass', 'radius':'iso_radius', 'logage':'iso_logage'}
    prop_dict = dict()
    prop_names = list(spreadsheet_keys.keys())
    for prop_name in prop_names + ['period']:
        prop_dict[prop_name] = list()

    for star in stars:
        tome = encyclopedia.query('name == @star')

        for prop_name in prop_names:
            prop_value = median(tome[spreadsheet_keys[prop_name]])
            prop_dict[prop_name].append(prop_value)
        star = 'hd' + star
        period = list(catalog.query('star == @star')['period'])[0]
        prop_dict['period'].append(period)

    var1 = prop_dict['period']
    for prop_name, var2 in prop_dict.items():
        print(prop_name)
        var1 = prop_dict['period']
        # if prop_name == 'vsini':
        #     a, b = [], []
        #     for i, x in enumerate(var2):
        #         if (x > 0.01):
        #             b.append(x)
        #             a.append(var1[i])
        #     print(len(a), len(b))
        #     var1, var2 = a, b

        p = scipy.stats.pearsonr(var1, var2)
        print(p)
        fig, ax = plt.subplots(1, 1, tight_layout=True)
        ax.plot(var1, var2, 'b.', markersize=15)
        ax.set(xlabel='Period (days)',
                   ylabel=prop_name,
                   title='Period vs ' + prop_name,
                   )
        plt.text(0.79, 0.86, 'r = {:.3f}\np = {:.3f}'.format(p[0], p[1]),
                 transform=ax.transAxes, bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 4})
        fig.set_size_inches(5, 4)
        plt.savefig('plots/period_vs_' + prop_name + '.png', dpi=300)

    # print(encyclopedia[::100])


    # periods = catalog['period']
    # stdevs = catalog['stdev']
    # stdevs = stdevs.query('stdev > 0')

    # p = scipy.stats.pearsonr(periods, stdevs / periods)
    # print(p)
    # fig, ax = plt.subplots(1, 1, tight_layout=True)
    # ax.plot(periods, stdevs / periods, 'b.', markersize=15)
    # ax.set(xlabel='Period (days)',
    #            ylabel='St. dev. / Period',
    #            title='Period vs St. Dev.',
    #            )
    # plt.text(0.79, 0.86, 'r = {:.3f}\np = {:.3f}'.format(p[0], p[1]),
    #          transform=ax.transAxes, bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 4})
    # fig.set_size_inches(5, 4)
    # plt.show()
    # plt.savefig('period_vs_stdev.png', dpi=300)

    # # Make historgram of powers
    # # print(plt.style.available)
    # # plt.style.use('ggplot')
    # fig, ax = plt.subplots(1, 1, tight_layout=True)
    # ax.hist(periods, bins=9)
    # ax.set(xlabel='Period (days)',
    #            ylabel='Frequency',
    #            title='APF-50 Rotation Period Distribution',
    #            )
    # mean, stdev = statistics.mean(periods), statistics.stdev(periods)
    # plt.text(0.05, 0.84, r'$\mu={:.3f}$'.format(mean) + '\n' + r'$\sigma={:.3f}$'.format(stdev),
    #          transform=ax.transAxes, bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 4})
    # fig.set_size_inches(5, 4)
    # # plt.show()
    # plt.savefig('periods_histogram.png', dpi=300)

    # fig, ax = plt.subplots(1, 1, tight_layout=True)
    # ax.hist(stdevs, bins=7)
    # ax.set(xlabel='St. Dev. (days)',
    #            ylabel='Frequency',
    #            title='APF-50 Rotation Period St. Dev. Distribution',
    #            )
    # mean, stdev = statistics.mean(stdevs), statistics.stdev(stdevs)
    # plt.text(0.22, 0.84, r'$\mu={:.3f}$'.format(mean) + '\n' + r'$\sigma={:.3f}$'.format(stdev),
    #          transform=ax.transAxes, bbox={'facecolor': 'white', 'alpha': 0.5, 'pad': 4})
    # fig.set_size_inches(5, 4)
    # # plt.show()
    # plt.savefig('stdevs_histogram.png', dpi=300)

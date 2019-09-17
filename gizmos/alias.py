import tools
import pandas as pd

if __name__ == '__main__':

    def is_possible_period(period):
        return period < 100 and period > 2

    catalog = pd.read_csv('../star_catalog.csv')
    print('{0:<10} {1:<8}{2}'.format('star', 'period', '  aliases and harmonics'))
    for i, row in catalog.iterrows():
        star = row['star']
        period = row['period']
        frequency = 1 / period
        aliases, harmonics = tools.find_aliases(frequency, (1,), (1/29.5, 1/365))
        print(('{0:<10} {1:<8}').format(row['star'], round(period, 3)), end='')
        for alias in aliases:
            if is_possible_period(alias):
                print('{0:7}'.format(round(alias, 2)), end = ' ')
        for harmonic in (1/2 * period, 2 * period):
            if is_possible_period(harmonic):
                print('{0:7}'.format(round(harmonic, 2)), end = ' ')
        print("")

import pandas

if __name__ == '__main__':
    catalog = pandas.read_csv('star_catalog.csv')
    stdevs = pandas.read_csv('stdevs.csv')

    for i, star in enumerate(stdevs['star']):
        stdev = stdevs['stdev'][i]
        ngroups = stdevs['ngroups'][i]

        index = list(catalog['star']).index(star)
        catalog['stdev'][index] = round(stdev, 3)
        catalog['ngroups'][index] = ngroups
        catalog['period'] = round(catalog['period'], 3)

    catalog.to_csv('star_catalog.csv', index=False)
 

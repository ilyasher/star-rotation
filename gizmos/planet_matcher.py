import pandas

if __name__ == '__main__':
    planets = pandas.read_csv('planet_list_719.csv')
    catalog = pandas.read_csv('star_catalog.csv')
    stars = catalog['star']
    stars = [star[2:] for star in stars]

    planets = planets.query('hostname in @stars')

    keep_keys = ['hostname', 'status', 'per']
    # keep_keys = ['hostname', 'status', 'mass', 'axis', 'per', 'k', 'e']
    for key in planets.keys():
        if key not in keep_keys:
            del planets[key]

    print(catalog)
    print(planets)

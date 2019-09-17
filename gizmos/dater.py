import sys
import pandas as pd

if __name__ == '__main__':
    # starname = sys.argv[1]
    good_times = pd.read_csv('halpha.csv')
    starnames_all = good_times['star']
    stars = []
    for star in starnames_all:
        if star not in stars:
            stars.append(star)
    for starname in stars:
        print(starname)
        cahk = pd.read_csv('cahk/{}.csv'.format(starname), comment='#')
        file = open('halpha/{}.csv'.format(starname), 'w')
        file.write('time,Ha,tel\n')
        for i, row in cahk.iterrows():
            id = row['observation_id']
            r_id = 'r' + id
            inst = id[0]
            if inst == 'a' or inst == 'b':
                inst = 'apf'
            elif inst == 'j':
                inst = 'hires_j'
            else:
                continue
            if r_id in list(good_times['observation_id']):
                index = list(good_times['observation_id']).index(r_id)
                file.write('{},'.format(row['bjd']))
                file.write('{},'.format(list(good_times['Ha'])[index]))
                file.write('{}\n'.format(inst))
        file.close()

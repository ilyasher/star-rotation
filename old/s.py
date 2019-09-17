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

def main():
    file = open("d-abc.by", "r")
    fluxes = []
    for line in file.readlines():
        words = line.split()
        fluxes.append(mag_to_flux(float(words[1])))
    fluxes = normalize(fluxes)

    file.close()
    file = open("d-abc.by", "r")

    newfile = open("d-abc_f.by", "w")
    for n, line in enumerate(file.readlines()):
        words = line.split()
        flux = float("{0:.6f}".format(fluxes[n]))
        newfile.write(words[0] + " " + str(flux) + "\n")
    file.close()
    newfile.close()

if (__name__ == '__main__'):
    main()

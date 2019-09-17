if __name__ == '__main__':
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
    newfile = open('fluxes.csv', 'w')

    newfile.write('time flux\n')
    for line in file.readlines():
        if line != '\n':
            newfile.write(line)
    file.close()
    newfile.close()

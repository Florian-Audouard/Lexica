from random import randrange
from functools import cmp_to_key


def particionner(tab, deb, fin, func):
    if deb < fin:
        curent = deb
        for i in range(deb + 1, fin):
            if func(tab[curent], tab[i]) and curent < i:
                tmp = tab[curent]
                tab[curent] = tab[i]
                tab[i] = tab[curent + 1]
                tab[curent + 1] = tmp
                curent += 1
        particionner(tab, deb, curent, func)
        particionner(tab, curent + 1, fin, func)


def triRapide(tab, func):
    particionner(tab, 0, len(tab), func)


def compare(elem1, elem2):
    if abs(elem1["x"] - elem2["x"]) < 10 and elem1["y"] < elem2["y"]:
        return 0
    if elem1["x"] < elem2["x"]:
        return 0
    return 1


tab = []
for i in range(20):
    tab.append({"x": randrange(500), "y": randrange(500)})


# print(sorted(tab, key=cmp_to_key(compare)))

# print()
# triRapide(tab, compare)

# print(tab)

print(min({"x": 5}, {"x": 4}, key=lambda x: x["x"]))

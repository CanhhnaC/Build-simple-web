a = ['1','2'], ['4','3']

print(a[0][0])
b = [i[0] for i in a]
c = [i[1] for i in a]
# print(b)
# print(c)
for i, j in a:
    print(i)
    print(j)
a = input("Masukkan angka a: ")
b = input("Masukkan angka b: ")
c = input("Masukkan angka c: ")


if (a > b) and (a > c):
    print(f"{a} adalah angka terbesar.")
    if (b < c):
        print(f"{b} adalah angka terkecil.")
    else:
        print(f"{c} adalah angka terkecil.")
elif (b > a) and (b > c):
    print(f"{b} adalah angka terbesar.")
    if (a < c):
        print(f"{a} adalah angka terkecil.")
    else:
        print(f"{c} adalah angka terkecil.")
elif (c > a) and (c > b):
    print(f"{c} adalah angka terbesar.")
    if (a < b):
        print(f"{a} adalah angka terkecil.")
    else:
        print(f"{b} adalah angka terkecil.")
rata_rata = (float(a) + float(b) + float(c)) / 3
print(rata_rata)

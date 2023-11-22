a = input("Masukkan angka a: ")
b = input("Masukkan angka b: ")
c = input("Masukkan angka c: ")


if (a > b) and (a > c):
    if (b > c):
        print(f"nilai {a} terbesar dan nilai {c} terkecil")
    else:
        print(f"nilai {a} terbesar dan nilai {b} terkecil")
elif (a > b) and (a < c):
    print(f"nilai {c} terbesar dan nilai {b} terkecil")
elif (a < b) and (a > c):
    print(f"nilai {b} terbesar dan nilai {c} terkecil")
elif (b > c):
    print(f"nilai {b} terbesar dan nilai {a} terkecil")
else:
    print(f"nilai {c} terbesar dan nilai {a} terkecil")

import sys

def main():

    filename = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) >= 3 else 2

    with open(filename, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            if line_num >= 2 and (line_num - 2) % n == 0:
                sys.stdout.write(line)

if __name__ == "__main__":
    main()

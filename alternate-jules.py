import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="input file")
    parser.add_argument("-n", type=int, default=2, help="step size")
    args = parser.parse_args()

    with open(args.filename, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            if line_num >= 2 and (line_num - 2) % args.n == 0:
                sys.stdout.write(line)

if __name__ == "__main__":
    main()

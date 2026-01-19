#!/usr/bin/env python3

# don't import numpy or pandas, 
# the autograder environment is 
# Spartan.
import argparse

def alternate_solano(filename, n = 2):
    with open(filename, 'r') as file:
        for linenum, line in enumerate(file, start = 1):
            if linenum >= 2 and (linenum - 2) % n == 0:
                print(line, end = "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("-n", nargs = "?", type = int, default = 2)
    args = parser.parse_args()
    
    alternate_solano(args.filename, args.n)
    
if __name__ == "__main__":
   main()
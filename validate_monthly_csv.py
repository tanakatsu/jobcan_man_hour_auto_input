import pandas as pd
import numpy as np
import re
from argparse import ArgumentParser
import sys


RESERVED_COLS = ["date"]

def main():
    parser = ArgumentParser()
    parser.add_argument('csvfile', help='input csvfile')
    args = parser.parse_args()

    df = pd.read_csv(args.csvfile, dtype=str)
    cols = [col for col in df.columns if col not in RESERVED_COLS]

    errors = 0
    for i, row in df.iterrows():
        count = 0
        for col in cols:
            val = row[col]
            if type(val) is str:
                if re.match("\d\d:\d\d", val) or re.match("\d:\d\d", val):
                    pass
                elif val == 'nan':
                    pass
                elif val == '-1':
                    count = count + 1
                else:
                    print(f"Error in line {i + 2} at {col}: {val}")
                    errors = errors + 1
            else:
                if ~np.isnan(val):
                    print(f"Error in line {i + 2} at {col}: {val}")
                    errors = errors + 1
        if count > 1:
            print(f"Error in line {i + 2}: multiple '-1'")
            errors = errors + 1

    if errors == 0:
        print("validation OK")
    else:
        print("There are {} errors found.".format(errors))
        sys.exit(1)


if __name__ == "__main__":
    main()

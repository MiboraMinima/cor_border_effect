# TODO: add header
# TODO: add comments and structure

import json
import argparse
import param_gen.gen_param_funs as gp

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process files with given parameters.")
    parser.add_argument("input_dir", type=str, help="Input directory path")
    parser.add_argument("output_dir", type=str, help="Output directory path")
    parser.add_argument("--years", nargs="+", default=None, help="Years to process")
    parser.add_argument("--places", nargs="+", default=None, help="Places to process")
    parser.add_argument("param_file", type=str, help="Parameter file in .json")

    args = parser.parse_args()

    gen_list = gp.process_files(args.input_dir, args.output_dir, args.years, args.places)

    # Write .json parameter file for a batch process in QGIS
    with open(args.param_file, "w") as f:
        json.dump(gen_list, f)  # Dump the data list to the JSON file


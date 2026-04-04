import argparse

def get_cli_arguments():
    parser = argparse.ArgumentParser(prog="CLI argument Parser", 
                                     description="CLI Program to specify which steps of the pipelien to run")

    parser.add_argument( "--extract", action="store_true")
    parser.add_argument( "--load", action="store_true")
    parser.add_argument( "--analyse", action="store_true")

    args = parser.parse_args()

    return args.extract, args.load, args.analyse 

# This quick utility tool is meant to take a list of proxies fomatted as
#           ip:port:user:pass
# and convert it to a format to be readily used by Python's request library.
#           user:pass@ip:port
#
# python format_proxies.py <inputfile> <outputfile>
import sys


def process(line):
    fields = line.split(':')
    try:
        with open(sys.argv[2], "a+") as outfile:
            outfile.write(
                f"{fields[2]}:{fields[3].strip()}@{fields[0]}:{fields[1]}\n")
        return True
    except:
        return


bufsize = 65536
try:
    with open(sys.argv[1]) as infile:
        while True:
            lines = infile.readlines(bufsize)
            if not lines:
                break
            for line in lines:
                process(line)
except IOError:
    print("Input file not accessible")

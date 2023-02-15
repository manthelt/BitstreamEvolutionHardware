from __future__ import print_function
from datetime import datetime
# Import the KiCad python helper module and the csv formatter
import kicad_netlist_reader
import kicad_utils
import csv
import sys

if len(sys.argv) != 3:
    print("Usage ", __file__, "<generic_netlist.xml> <output.txt>", file=sys.stderr)
    sys.exit(1)

# Generate an instance of a generic netlist, and load the netlist tree from
# the command line option. If the file doesn't exist, execution will stop
net = kicad_netlist_reader.netlist(sys.argv[1])

# Open a file to write to, if the file cannot be opened output to stdout
# instead
try:
    f = kicad_utils.open_file_writeUTF8(sys.argv[2], "w")
except IOError:
    e = "Can't open output file for writing: " + sys.argv[2]
    print( __file__, ":", e, sys.stderr )
    f = sys.stdout

# Retrieve the revision from the netlist
revision = net.getRevision()

# Check if the revision is an empty string.. If it is, set the
# revision to todays date
if(revision == ''):
    revision = datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
else:
    # Replace all spaces with an underscore in the revision
    revision = revision.replace(' ', '-')

# Write the revision to our out file
f.write(revision)

# Close the out file
f.close()
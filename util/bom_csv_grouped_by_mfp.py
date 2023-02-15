"""
    @package
    Output: CSV (comma-separated)
    Grouped By: MFP then Value
    Sorted By: Ref
    Fields: Reference(s), MFP, Qty, Value, LibPart, Footprint, Datasheet

    Outputs a grouped list of components. Grouping by MFP takes priority
    and components without an MFP field are grouped by Value & Footprint

    Command line:
    python "pathToFile/bom_csv_grouped_by_mfp.py" "%I" "%O.csv"
"""

from __future__ import print_function

# Import the KiCad python helper module and the csv formatter
import kicad_netlist_reader
import kicad_utils
import csv
import sys

# A helper function to filter/convert a string read in netlist
#currently: do nothing
def fromNetlistText( aText ):
    return aText

def myEqu(self, other):
    """myEqu is a more advanced equivalence function for components which is
    used by component grouping. Normal operation is to group components based
    on their value and footprint.

    In this example of a custom equivalency operator we compare the
    value, the part name and the footprint.
    """
    result = True

    # Check if the MFP field even exists
    if( (self.getField("MFP") != '') & (other.getField("MFP") != '')):
        if( self.getField("MFP") != other.getField("MFP") ):
            return False

    if self.getValue() != other.getValue():
        result = False
    elif self.getPartName() != other.getPartName():
        result = False
    elif self.getFootprint() != other.getFootprint():
        result = False

    return result

# Override the component equivalence operator - it is important to do this
# before loading the netlist, otherwise all components will have the original
# equivalency operator.
kicad_netlist_reader.comp.__eq__ = myEqu

if len(sys.argv) != 3:
    print("Usage ", __file__, "<generic_netlist.xml> <output.csv>", file=sys.stderr)
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

# subset the components to those wanted in the BOM, controlled
# by <configure> block in kicad_netlist_reader.py
components = net.getInterestingComponents()

compfields = net.gatherComponentFieldUnion(components)
partfields = net.gatherLibPartFieldUnion()

# remove Reference, Value, Datasheet, and Footprint, they will come from 'columns' below
partfields -= set( ['Reference', 'Value', 'Datasheet', 'Footprint'] )

columnset = compfields | partfields     # union

# prepend an initial 'hard coded' list and put the enchillada into list 'columns'
columns = ['Reference(s)','MFP','Qty','Value','LibPart', 'Footprint', 'Datasheet']

# Create a new csv writer object to use as the output formatter
out = csv.writer( f, lineterminator='\n', delimiter=',', quotechar='\"', quoting=csv.QUOTE_ALL )

# override csv.writer's writerow() to support encoding conversion (initial encoding is utf8):
def writerow( acsvwriter, columns ):
    utf8row = []
    for col in columns:
        utf8row.append( fromNetlistText( str(col) ) )
    acsvwriter.writerow( utf8row )

# Write out our column headers
writerow( out, columns )

# Get all of the components in groups of matching parts + values
# (see kicad_netlist_reader.py)
grouped = net.groupComponents(components)

# Output component information organized by group, aka as collated:
item = 0
row = []
for group in grouped:
    del row[:]
    refs = ""

    # Add the reference of every component in the group and keep a reference
    # to the component so that the other data can be filled in once per group
    for component in group:
        if len(refs) > 0:
            refs += ", "
        refs += component.getRef()
        c = component

    # Fill in the component groups common data
    # columns = ['Qty', 'Reference(s)', 'Value', 'LibPart', 'Footprint', 'Datasheet'] + sorted(list(columnset))
    row.append( refs );
    row.append( net.getGroupField(group, "MFP") )
    row.append( len(group) )
    row.append( c.getValue() )
    row.append( c.getLibName() + ":" + c.getPartName() )
    row.append( net.getGroupFootprint(group) )
    row.append( net.getGroupDatasheet(group) )

    # from column 7 upwards, use the fieldnames to grab the data
    for field in columns[7:]:
        row.append( net.getGroupField(group, field) );

    writerow( out, row  )

f.close()
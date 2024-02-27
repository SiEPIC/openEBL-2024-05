'''
--- Simple MZI ---
  
by Lukas Chrostowski, 2020-2023
   
Example simple script to
 - create a new layout with a top cell
 - create an MZI
 - export to OASIS for submission to fabrication

using SiEPIC-Tools function including connect_pins_with_waveguide and connect_cell

Use instructions:

Run in Python, e.g., VSCode

pip install required packages:
 - klayout, SiEPIC, siepic_ebeam_pdk, numpy

'''

designer_name = 'LukasChrostowski'
top_cell_name = 'EBeam_%s_MZI' % designer_name
export_type = 'PCell'  # static: for fabrication, PCell: include PCells in file

import pya
from pya import *

import SiEPIC
from SiEPIC._globals import Python_Env
from SiEPIC.scripts import connect_cell, connect_pins_with_waveguide, zoom_out, export_layout
from SiEPIC.utils.layout import new_layout, floorplan
from SiEPIC.extend import to_itype
from SiEPIC.verification import layout_check

import os

if Python_Env == 'Script':
    try:
        # For external Python mode, when installed using pip install siepic_ebeam_pdk
        import siepic_ebeam_pdk
    except:
        # Load the PDK from a folder, e.g, GitHub, when running externally from the KLayout Application
        import os, sys
        path_GitHub = os.path.expanduser('~/Documents/GitHub/')
        sys.path.insert(0,os.path.join(path_GitHub, 'SiEPIC_EBeam_PDK/klayout'))
        import siepic_ebeam_pdk

tech_name = 'EBeam'

if SiEPIC.__version__ < '0.5.4':
    raise Exception("Errors", "This example requires SiEPIC-Tools version 0.5.4 or greater.")

'''
Create a new layout using the EBeam technology,
with a top cell
and Draw the floor plan
'''    
cell, ly = new_layout(tech_name, top_cell_name, GUI=True, overwrite = True)
floorplan(cell, 605e3, 410e3)

dbu = ly.dbu

from SiEPIC.scripts import connect_pins_with_waveguide, connect_cell
waveguide_type='Strip TE 1550 nm, w=500 nm'
waveguide_type_delay='Si routing TE 1550 nm (compound waveguide)'

# Load cells from library
cell_ebeam_gc = ly.create_cell('GC_TE_1550_8degOxide_BB', tech_name)
cell_ebeam_y = ly.create_cell('ebeam_y_1550', tech_name)
cell_ebeam_y_dream = ly.create_cell('ebeam_dream_splitter_1x2_te1550_BB', 'EBeam-Dream',{})

# grating couplers, place at absolute positions
x,y = 60000, 15000
t = Trans(Trans.R0,x,y)
instGC1 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))
t = Trans(Trans.R0,x,y+127000)
instGC2 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))

# automated test label
text = Text ("opt_in_TE_1550_device_%s_MZI1" % designer_name, t)
cell.shapes(ly.layer(ly.TECHNOLOGY['Text'])).insert(text).text_size = 5/dbu

# Y branches:
# Version 1: place it at an absolute position:
t = Trans.from_s('r0 %s, %s' % (x+20000,y))
instY1 = cell.insert(CellInstArray(cell_ebeam_y.cell_index(), t))

# Version 2: attach it to an existing component, then move relative
instY2 = connect_cell(instGC2, 'opt1', cell_ebeam_y, 'opt1')
instY2.transform(Trans(20000,-10000))

# Waveguides:

connect_pins_with_waveguide(instGC1, 'opt1', instY1, 'opt1', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instGC2, 'opt1', instY2, 'opt1', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY1, 'opt2', instY2, 'opt3', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY1, 'opt3', instY2, 'opt2', waveguide_type=waveguide_type,turtle_B=[25,-90])

# 2nd MZI using Dream Photonics 1x2 splitter
# grating couplers, place at absolute positions
x,y = 180000, 15000
t = Trans(Trans.R0,x,y)
instGC1 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))
t = Trans(Trans.R0,x,y+127000)
instGC2 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))

# automated test label
text = Text ("opt_in_TE_1550_device_%s_MZI2" % designer_name, t)
cell.shapes(ly.layer(ly.TECHNOLOGY['Text'])).insert(text).text_size = 5/dbu

# Y branches:
instY1 = connect_cell(instGC1, 'opt1', cell_ebeam_y_dream, 'opt1')
instY1.transform(Trans(20000,0))
instY2 = connect_cell(instGC2, 'opt1', cell_ebeam_y_dream, 'opt1')
instY2.transform(Trans(20000,0))

# Waveguides:

connect_pins_with_waveguide(instGC1, 'opt1', instY1, 'opt1', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instGC2, 'opt1', instY2, 'opt1', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY1, 'opt2', instY2, 'opt3', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY1, 'opt3', instY2, 'opt2', waveguide_type=waveguide_type,turtle_B=[125,-90])

# 3rd MZI, with a very long delay line
cell_ebeam_delay = ly.create_cell('spiral_paperclip', 'EBeam_Beta',
                                  {'waveguide_type':waveguide_type_delay,
                                   'length':200,
                                   'flatten':True})
x,y = 60000, 175000
t = Trans(Trans.R0,x,y)
instGC1 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))
t = Trans(Trans.R0,x,y+127000)
instGC2 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))

# automated test label
text = Text ("opt_in_TE_1550_device_%s_MZI3" % designer_name, t)
cell.shapes(ly.layer(ly.TECHNOLOGY['Text'])).insert(text).text_size = 5/dbu

# Y branches:
instY1 = connect_cell(instGC1, 'opt1', cell_ebeam_y_dream, 'opt1')
instY1.transform(Trans(20000,0))
instY2 = connect_cell(instGC2, 'opt1', cell_ebeam_y_dream, 'opt1')
instY2.transform(Trans(20000,0))

# Spiral:
instSpiral = connect_cell(instY2, 'opt2', cell_ebeam_delay, 'optA')
instSpiral.transform(Trans(20000,0))

# Waveguides:
connect_pins_with_waveguide(instGC1, 'opt1', instY1, 'opt1', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instGC2, 'opt1', instY2, 'opt1', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY1, 'opt2', instY2, 'opt3', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY2, 'opt2', instSpiral, 'optA', waveguide_type=waveguide_type)
connect_pins_with_waveguide(instY1, 'opt3', instSpiral, 'optB', waveguide_type=waveguide_type,turtle_B=[5,-90])

# Zoom out
zoom_out(cell)

# Export for fabrication, removing PCells
path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.splitext(os.path.basename(__file__))[0]
if export_type == 'static':
    file_out = export_layout(cell, path, filename, relative_path = '..', format='oas', screenshot=True)
else:
    file_out = os.path.join(path,'..',filename+'.oas')
    ly.write(file_out)

# Verify
file_lyrdb = os.path.join(path,filename+'.lyrdb')
num_errors = layout_check(cell = cell, verbose=False, GUI=True, file_rdb=file_lyrdb)
print('Number of errors: %s' % num_errors)

# Display the layout in KLayout, using KLayout Package "klive", which needs to be installed in the KLayout Application
if Python_Env == 'Script':
    from SiEPIC.utils import klive
    klive.show(file_out, lyrdb_filename=file_lyrdb, technology=tech_name)

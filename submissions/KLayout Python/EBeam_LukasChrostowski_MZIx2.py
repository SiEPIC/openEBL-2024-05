'''
--- Mach-Zehnder ---
   
by Lukas Chrostowski, 2024 
 
Simple script to
 - create a new layout with a top cell
 - create the design
    - approx dL = 100 micron
    - two different MZI: one with single mode, one with multi-mode
    - goal: see if MM waveguides have lower variability than SM, and quantify from FSR variations
 - export to OASIS for submission to fabrication

using SiEPIC-Tools function including connect_pins_with_waveguide and connect_cell

usage:
 - run this script in Python
'''

designer_name = 'LukasChrostowski'
top_cell_name = 'EBeam_%s_MZIx2' % designer_name

import pya
from pya import Trans, CellInstArray, Text 

import SiEPIC
from SiEPIC._globals import Python_Env
from SiEPIC.scripts import connect_cell, connect_pins_with_waveguide, zoom_out, export_layout
from SiEPIC.utils.layout import new_layout, floorplan
from SiEPIC.extend import to_itype

import os

if Python_Env == 'Script':
    try:
        # For external Python mode, when installed using pip install siepic_ebeam_pdk
        import siepic_ebeam_pdk
    except:
        # Load the PDK from a folder, e.g, GitHub, when running externally from the KLayout Application
        import os, sys
        path_GitHub = os.path.expanduser('~/Documents/GitHub/')
        sys.path.append(os.path.join(path_GitHub, 'SiEPIC_EBeam_PDK/klayout'))
        import siepic_ebeam_pdk

tech_name = 'EBeam'

if SiEPIC.__version__ < '0.5.1':
    raise Exception("Errors", "This example requires SiEPIC-Tools version 0.5.1 or greater.")

'''
Create a new layout using the EBeam technology,
with a top cell
and Draw the floor plan
'''    
topcell, ly = new_layout(tech_name, top_cell_name, GUI=True, overwrite = True)
floorplan(topcell, 605e3, 410e3)

dbu = ly.dbu

from SiEPIC.scripts import connect_pins_with_waveguide, connect_cell
waveguide_type='Strip TE 1550 nm, w=500 nm'
waveguide_type_delay='Si routing TE 1550 nm (compound waveguide)'

# Load cells from library
cell_ebeam_gc = ly.create_cell('GC_TE_1550_8degOxide_BB', tech_name)
cell_ebeam_y = ly.create_cell('ebeam_y_1550', tech_name)

# define parameters for the designs
params = [1, 2, 3, 4, 5, 6]
params_WG = [waveguide_type, waveguide_type_delay, waveguide_type, waveguide_type_delay, waveguide_type, waveguide_type_delay]

for i in range(0,len(params)):
    cell = ly.create_cell('cell%s' % i)

    dy = -51000 # -53000 # good for 4
    min_gc_pitch = 60100
    dx = (min_gc_pitch**2 - dy**2) ** 0.5
    x,y = dx*i, dy*i
    t = Trans(Trans.R0,x,y)
    topcell.insert(CellInstArray(cell.cell_index(), t))

    x,y = 41000, 269000
    t = Trans(Trans.R0,x,y)
    instGC1 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))
    t = Trans(Trans.R0,x,y+127000)
    instGC2 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))

    # automated test label
    text = Text ("opt_in_TE_1550_device_%s_MZI%s" % (designer_name, params[i]), t)
    cell.shapes(ly.layer(ly.TECHNOLOGY['Text'])).insert(text).text_size = 5/dbu
    
    # Y branches:
    instY1 = connect_cell(instGC2, 'opt1', cell_ebeam_y, 'opt1')
    instY1.transform(Trans(10000,-16000))
    instY2 = connect_cell(instGC2, 'opt1', cell_ebeam_y, 'opt1')

    # Waveguides:
    L = 370
    connect_pins_with_waveguide(instGC1, 'opt1', instY1, 'opt1', waveguide_type=waveguide_type, turtle_A=[5,90,15,90, 20,-90])
    connect_pins_with_waveguide(instY1, 'opt2', instY2, 'opt3', waveguide_type=params_WG[i], turtle_A=[L,90,1,90])
    instWG = connect_pins_with_waveguide(instY1, 'opt3', instY2, 'opt2', waveguide_type=params_WG[i], turtle_A=[5,-90,10,-90,20,90,10,90,23,90]) # turtle_A=[50,90,1,90])
    instWG.transform(Trans(L/dbu,0))
    connect_pins_with_waveguide(instY1, 'opt3', instWG, 'opt1', waveguide_type=params_WG[i])
    connect_pins_with_waveguide(instY2, 'opt2', instWG, 'opt2', waveguide_type=params_WG[i])
    


# Zoom out
zoom_out(cell)

# Save
path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.splitext(os.path.basename(__file__))[0]
file_out = export_layout(cell, path, filename, relative_path = '..', format='oas', screenshot=False)

# Display the layout in KLayout, using KLayout Package "klive", which needs to be installed in the KLayout Application
if Python_Env == 'Script':
    from SiEPIC.utils import klive
    klive.show(file_out, technology=tech_name)

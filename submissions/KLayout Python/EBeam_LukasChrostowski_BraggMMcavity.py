'''
--- Fabry Perot cavity using Bragg gratings and long multi-mode waveguides ---
   
by Lukas Chrostowski, 2024 
 
Simple script to
 - create a new layout with a top cell
 - create the Bragg cavity
 - export to OASIS for submission to fabrication

using SiEPIC-Tools function including connect_pins_with_waveguide and connect_cell

usage:
 - run this script in Python
'''

designer_name = 'LukasChrostowski'
top_cell_name = 'EBeam_%s_BraggMMcavity' % designer_name

import pya
from pya import *

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
waveguide_type='Strip TE 1310 nm, w=350 nm'
waveguide_type_delay='Si routing TE 1310 nm (compound waveguide)'

# Load cells from library
cell_ebeam_gc = ly.create_cell('GC_TE_1310_8degOxide_BB', tech_name)
cell_ebeam_y = ly.create_cell('ebeam_y_1310', 'EBeam_Beta')

# define parameters for the designs
params_BraggN = [40, 50, 60, 70]

for i in range(0,4):
    cell = ly.create_cell('cell%s' % i)

    x,y = 52000*i, -40000*i
    t = Trans(Trans.R0,x,y)
    topcell.insert(CellInstArray(cell.cell_index(), t))
    
    
    cell_bragg = ly.create_cell('ebeam_bragg_te1310', 'EBeam_Beta', {
        'number_of_periods':params_BraggN[i],
        'grating_period': 0.270,
        'corrugation_width': 0.08,
        'wg_width': 0.35,
        'sinusoidal': True})
    if not cell_bragg:
        raise Exception ('Cannot load Bragg grating cell; please check the script carefully.')
    
    # Circuit design, with a very long delay line
    cell_ebeam_delay = ly.create_cell('spiral_paperclip', 'EBeam_Beta',{
                            'waveguide_type':waveguide_type_delay,
                            'length':160,
                            'loops':1,
                            'flatten':True})
    x,y = 41000, 140000
    t = Trans(Trans.R0,x,y)
    instGC1 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))
    t = Trans(Trans.R0,x,y+127000)
    instGC2 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))
    t = Trans(Trans.R0,x,y+127000*2)
    instGC3 = cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t))
    
    # automated test label
    text = Text ("opt_in_TE_1310_device_%s_BraggMMcavity%s" % (designer_name, params_BraggN[i]), t)
    cell.shapes(ly.layer(ly.TECHNOLOGY['Text'])).insert(text).text_size = 5/dbu
    
    # Y branches:
    instY1 = connect_cell(instGC3, 'opt1', cell_ebeam_y, 'opt3')
    instY1.transform(Trans(10000,0))
    
    # Bragg grating
    instBragg1 = connect_cell(instY1, 'opt1', cell_bragg, 'opt1')
    instBragg1.transform(Trans(10000,0))
    
    # Spiral:
    instSpiral = connect_cell(instBragg1, 'opt2', cell_ebeam_delay, 'optA')
    
    # Bragg grating
    instBragg2 = connect_cell(instSpiral, 'optB', cell_bragg, 'opt2')
    
    # Waveguides:
    connect_pins_with_waveguide(instGC3, 'opt1', instY1, 'opt3', waveguide_type=waveguide_type)
    connect_pins_with_waveguide(instGC2, 'opt1', instY1, 'opt2', waveguide_type=waveguide_type, turtle_B=[5,90,5,-90])
    connect_pins_with_waveguide(instGC1, 'opt1', instBragg2, 'opt1', waveguide_type=waveguide_type, turtle_B=[5,90,10,-90,20,90])
    connect_pins_with_waveguide(instY1, 'opt1', instBragg1, 'opt1', waveguide_type=waveguide_type,turtle_B=[5,-90])
    


# Zoom out
zoom_out(cell)

# Save
path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.splitext(os.path.basename(__file__))[0]
file_out = export_layout(cell, path, filename, relative_path = '..', format='oas', screenshot=False)


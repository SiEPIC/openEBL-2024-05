'''
Scripted layout for ring resonators using SiEPIC-Tools
in the SiEPIC-EBeam-PDK "EBeam" technology

by Lukas Chrostowski, 2023

Use instructions:

Run in Python, e.g., VSCode

pip install required packages:
 - klayout, SiEPIC, siepic_ebeam_pdk, numpy

'''

designer_name = 'AndrewB'
top_cell_name = 'EBeam_%s_Cavities2' % designer_name
export_type = 'PCell'  # static: for fabrication, PCell: include PCells in file

import pya
from pya import *

import SiEPIC
from SiEPIC._globals import Python_Env
from SiEPIC.scripts import zoom_out, export_layout
from SiEPIC.verification import layout_check
import os
import numpy

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

# Example layout function
def cavities():

    # Import functions from SiEPIC-Tools
    from SiEPIC.extend import to_itype
    from SiEPIC.scripts import connect_cell, connect_pins_with_waveguide
    from SiEPIC.utils.layout import new_layout, floorplan

    # Create a layout for testing a double-bus ring resonator.
    # uses:
    #  - the SiEPIC EBeam Library
    # creates the layout in the presently selected cell
    # deletes everything first
    
    # Configure parameter sweep  
    pol = 'TE'
    sweep_n = [45, 60, 75]
    period = 0.27
    sweep_dW = [0.04, 0.05, 0.06]
    # cavity_length = 50_000
    cavity_lengths = [80_000]
    taper_length_um = 20
    
    '''
    Create a new layout using the EBeam technology,
    with a top cell
    and Draw the floor plan
    '''    
    cell, ly = new_layout(tech_name, top_cell_name, GUI=True, overwrite = True)
    floorplan(cell, 605e3, 410e3)

    if SiEPIC.__version__ < '0.5.1':
        raise Exception("Errors", "This example requires SiEPIC-Tools version 0.5.1 or greater.")

    # Layer mapping:
    LayerSiN = ly.layer(ly.TECHNOLOGY['Si'])
    fpLayerN = cell.layout().layer(ly.TECHNOLOGY['FloorPlan'])
    TextLayerN = cell.layout().layer(ly.TECHNOLOGY['Text'])
    
    
    # Create a sub-cell for our Ring resonator layout
    top_cell = cell
    dbu = ly.dbu
    cell = cell.layout().create_cell("Cavities")
    t = Trans(Trans.R0, 40 / dbu, 12 / dbu)

    # place the cell in the top cell
    top_cell.insert(CellInstArray(cell.cell_index(), t))
    
    # Import cell from the SiEPIC EBeam Library
    cell_ebeam_gc = ly.create_cell("GC_%s_1310_8degOxide_BB" % pol, "EBeam")
    # get the length of the grating coupler from the cell
    gc_length = cell_ebeam_gc.bbox().width()*dbu
    # spacing of the fibre array to be used for testing
    GC_pitch = 127
    
    #cell_terminator = ly.create_cell("ebeam_terminator_te1310", "EBeam")
    
    cell_taper_cavity = ly.create_cell('ebeam_taper_te1550', "EBeam", {
        'wg_width1': 0.350,
        'wg_width2': 2.000,
        'wg_length': taper_length_um})
        
    cell_y = ly.create_cell('ebeam_y_1310', 'EBeam_Beta')

    # Loop through the parameter sweep
    #for i in range(len(sweep_gap)):
    # for i in range(len(sweep_period)):
    for index_1, n in enumerate(sweep_n):
        for index_2, dW in enumerate(sweep_dW):
            for index_3, cavity_length in enumerate(cavity_lengths):

                p = period

                i = index_1 + index_2 + index_3
                # place layout at location:
                if i==0:
                    x=0
                else:
                    # next device is placed at the right-most element + length of the grating coupler
                    x = inst_bragg1.bbox().right*dbu + gc_length + 10
                
                # get the parameters
                # n = sweep_n[i]
                # p = sweep_period[i]
                
                # Grating couplers, Ports 0, 1, 2, 3 (from the bottom up)
                instGCs = []
                for j in range(0,4):
                    if j == 1:
                        instGCs.append(0)
                        continue; # Don't create the 2nd GC
                    
                    t = Trans(Trans.R0, to_itype(x,dbu), j*127/dbu + 3/dbu)
                    instGCs.append( cell.insert(CellInstArray(cell_ebeam_gc.cell_index(), t)) )
                
                # Label for automated measurements, laser on Port 2, detectors on Ports 1, 3, 4
                t = Trans(Trans.R90, to_itype(x,dbu), to_itype(GC_pitch*2,dbu))
                # text = Text ("opt_in_%s_1310_device_%s_FPPeriodn%sp%s" % (pol.upper(), designer_name,n,int(round(p*1000))), t)
                text = Text(f"opt_in_{designer_name}_1310_device_n{n}_dW{int(dW*100)}_L{int(cavity_length/10_000)}", t)
                text.halign = 1
                cell.shapes(TextLayerN).insert(text).text_size = 5/dbu

                #cell_splitter = ly.create_cell('ebeam_splitter_swg_assist_te1310', "EBeam")

                cell_bragg = ly.create_cell('ebeam_bragg_te1550', "EBeam", {
                  'number_of_periods': n,
                  'grating_period': p,
                  'corrugation_width': dW,
                  'wg_width': 0.350,
                  'sinusoidal': True})

                if i == 0:
                    inst_y = connect_cell(instGCs[2], 'opt1', cell_y, 'opt1')
                    first_GC2 = instGCs[2]
                else:
                    inst_y = connect_cell(first_GC2, 'opt1', cell_y, 'opt1')

                inst_y.transform(Trans(Trans.R90, 270000 + x*1000, 200000))
                
                inst_bragg1 = connect_cell(inst_y, 'opt1', cell_bragg, 'pin1')
                
                inst_taper_cavity1 = connect_cell(inst_bragg1, 'pin2', cell_taper_cavity, 'pin1')
                
                inst_taper_cavity2 = connect_cell(inst_taper_cavity1, 'pin1', cell_taper_cavity, 'pin1')
                inst_taper_cavity2.transform(Trans(0, -cavity_length))
                
                inst_bragg2 = connect_cell(inst_taper_cavity2, 'pin1', cell_bragg, 'pin2')
                          
                # Ring resonator from directional coupler PCells
                #cell_dc = ly.create_cell("ebeam_dc_halfring_straight", "EBeam", { "r": r, "w": wg_width, "g": g, "bustype": 0 } )
                #y_ring = GC_pitch*3/2
                # first directional coupler
                #t1 = Trans(Trans.R270, to_itype(x+wg_bend_radius, dbu), to_itype(y_ring, dbu))
                #inst_dc1 = cell.insert(CellInstArray(cell_dc.cell_index(), t1))
                # add 2nd directional coupler, snapped to the first one
                #inst_dc2 = connect_cell(inst_dc1, 'pin2', cell_dc, 'pin4')
                
                connect_pins_with_waveguide(inst_taper_cavity1, 'pin2', inst_taper_cavity2, 'pin2', waveguide_type='Multimode Strip TE 1550 nm, w=2000 nm')
                
                # Create paths for waveguides, with the type defined in WAVEGUIDES.xml in the PDK
                waveguide_type='Strip TE 1310 nm, w=350 nm'
                
                # GC1 to bottom-left of ring pin3
                #connect_pins_with_waveguide(instGCs[1], 'opt1', inst_bragg1, 'pin2', waveguide_type=waveguide_type)
                
                # GC2 to top-left of ring pin1
                connect_pins_with_waveguide(instGCs[2], 'opt1', inst_y, 'opt2', waveguide_type=waveguide_type)
                
                # GC0 to top-right of ring
                connect_pins_with_waveguide(instGCs[0], 'opt1', inst_bragg2, 'pin1', waveguide_type=waveguide_type)
                
                # GC3 to bottom-right of ring
                connect_pins_with_waveguide(instGCs[3], 'opt1', inst_y, 'opt3', waveguide_type=waveguide_type)

    # Introduce an error, to demonstrate the Functional Verification
    # inst_dc2.transform(Trans(1000,-1000))

    return ly, cell
    
ly, cell = cavities()

# Zoom out
zoom_out(cell)

# Save
path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.splitext(os.path.basename(__file__))[0]
file_out = export_layout(cell, path, filename, relative_path = '..', format='oas', screenshot=False)

print('layout script done')

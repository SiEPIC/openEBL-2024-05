
# openEBL Design Submissions

- The Silicon Electronic Photonics Integrated Circuits (SiEPIC) fabrication program, <a href="https://siepic.ca/fabrication/">SiEPICfab</a>, presents the open electron beam lithography (EBL) fabrication process, where former and current students of <a href="https://siepic.ca/education/">SiEPIC</a> workshops and courses can submit their design for manufacturing and testing.
- More details about <a href="https://siepic.ca/openEBL/">openEBL</a>.
- This fabrication run had a deadline of May 18, 2024.
- The previous submission was in [February 2024](https://github.com/SiEPIC/openEBL-2024-02), and measurement data is available. 

# Fabrication process: Passive Silicon
## Technical summary:
- SOI wafer, 220 nm silicon
- Baseline process:
  - Single full etch, using a negative resist (HSQ)
  - Oxide cladding
- Process Design Kit: [SiEPIC-EBeam-PDK](https://github.com/siepic/SiEPIC_EBeam_PDK) 

## Layer table
| Name            | Layer/datatype | Description                                                                          |
|-----------------|----------------|--------------------------------------------------------------------------------------|
| Si  | 1/99 | Layer to draw silicon geometries |
| Floorplan | 99/0 | Marks the layout design area |
| Text | 10/0 | Text labels for automated measurements |
| DevRec | 68/0 | Device recognition layer for component connectivity, netlist extraction, and verification|
| PinRec  | 1/10  | Port/pins recognition layer for component connectivity, netlist extraction, and verification|
| Waveguide | 1/99 | Virtual layer, guiding shape for waveguide, used for length calculation |
| SEM | 200/0 | Requests for SEM images. Rectangles in a 4:3 aspect |


# Submission instructions:

The submission involves several steps. First, you need to create your design(s) using the process design kit (PDK) for this specific fabrication run. Then you need to create a Fork of this repository, commit your design(s), ensure that it passes the checks, and create a pull request. Once your pull request is approved, your design(s) will be merged into the layout for fabrication. You should verify that your design is correctly merged. Once the designs are fabricated, they will be tested, and the measurement results will be posted in this repository.

## Design software and PDK installation instructions:
 - Design tools and process design kit (SiEPIC-EBeam-PDK, KLayout implementation)<a href="https://github.com/siepic/SiEPIC_EBeam_PDK/wiki/Installation-instructions"> installation instructions</a>.
 - Create your design using Python ([example Jupyter notebook](https://colab.research.google.com/drive/1q3PU5ESmOa171J6KOkiUUlVXPnPBuCg-?usp=sharing), [example Python file](https://github.com/SiEPIC/openEBL-2024-05/blob/main/submissions/KLayout%20Python/EBeam_LukasChrostowski_MZI.py)) or using the Graphical Interface in KLayout

## Submission via GitHub
 - [Watch this video for a demonstration](https://kaltura.clemson.edu/media/t/1_iwysnxub)
 - Create an account on GitHub
 - Fork a copy of this GitHub repository into your own account:  <a href="../../fork">Create a new fork</a>.
 - Turn on the GitHub Actions on your forked repository: <a href="../../actions">Actions</a> (In your repository's page on GitHub, click on Actions in the top-menu bar, and Enable the workflows).
 - [Optional] Install GitHub Desktop (or git) on your computer, and Clone a local copy: <a href="x-github-client://openRepo/https://github.com/SiEPIC/openEBL-2024-02">Open with GitHub Desktop</a>
 - Create your design, and ensure that the filename contains your <a href="https://www.edx.org/learn/engineering/university-of-british-columbia-silicon-photonics-design-fabrication-and-data-ana">edX.org</a> (or GitHub username if the edX one is a random string that does not contain your name), and be formatted according to the course/workshop as follows:
   - EBeam_username.oas: for the <a href="https://www.edx.org/learn/engineering/university-of-british-columbia-silicon-photonics-design-fabrication-and-data-ana">edX Phot1x silicon photonics design course</a>
   - ELEC413_username.oas: for the <a href="https://ece.ubc.ca/courses/elec-413/">UBC ELEC 413 course</a>
   - SiEPIC_Passives_username.oas: for the <a href="https://www.cmc.ca/passive-silicon-photonics-fabrication-workshop-2023">CMC SiEPIC Passives silicon photonics workshop</a>
   - openEBL_username.gds: for past participants in the above courses, conference short courses
   - For example: EBeam_LukasChrostowski_rings.oas
 - Upload your design(s) into the "submissions" folder, as a binary file, namely a .gds (GDSII format) or .oas (OASIS format) file. 
    - This can be done via the GitHub web page, by navigating to the <a href=../../tree/main/submissions>submissions folder</a>, then clicking on Add file, and Upload files. 
    - Click Commit changes, and wait for the verification (via GitHub actions) to complete. This will appear as a green checkmark or red X next to your commit on GitHub. 
    - If there are errors, please review and correct the errors.
    - Please run your verification locally (press V in KLayout), or download the output .lydrb verification file from GitHub and open in KLayout.
 -  "All checks have failed" <img width="864" alt="image" src="https://github.com/SiEPIC/openEBL-2024-05/assets/15843200/d5689514-eca0-423f-9288-b20ec4fdd5e9">
    - Click on Details
    - In the main, window expand the "Run layout verification"; see if there is a text description of the problem
    - Look for the Artifact file; download it and open it in KLayout
  - After fixing the errors, you should have a green check mark as follows: <img width="488" alt="image" src="https://github.com/SiEPIC/openEBL-2024-05/assets/15843200/4c502cc4-16c1-4115-8ad7-7d5fdfe715d3">   
- Alternatively upload your Python file, which will be compiled by a GitHub Action.  
   - For KLayout designs, use the "submissions/KLayout Python" folder, namely a .py (Python format) file.  e.g., EBeam_LukasChrostowski_MZI.py.  The Python file should save a gds or oas file into the parent "submissions" folder. The Python script needs to be executable in non-GUI mode, namely using "import klayout SiEPIC SiEPIC-EBeam-PDK"
 - Create a <a href="https://help.github.com/articles/using-pull-requests/">Pull Request</a> -- this will notify the team of your contribution, which we can aggregate into the main design file
 - Return to the main repository, and ensure that your design is correctly merged. Download the Latest Merge file, below.

<img width="1281" alt="image" src="https://github.com/SiEPIC/openEBL-2024-02/assets/15843200/e4785a27-b971-4a64-8796-1e351f30c00e">

## Black-box cells (IP Replacement)
- We perform IP replacement on several cells (grating couplers). We call these cells Black Box (BB), and you can identify them by _BB in the cell name, or the presence of the Blackbox layer 998/0 in the cell.
- You must not change the name of the cell, the contents, nor cell origins. Otherwise, the replacement will not work correctly.

## Automated GitHub Actions
Optional: The verification and merging is performed using GitHub actions. The repository implements the following:
1) Running the Python files in the "submissions/KLayout Python" folder, to generate the designs
2) Performing Manufacturing DRC verification on the designs in the "submissions" folder, and outputing the errors as an Artifact
3) Performing Functional verification on the designs in the "submissions" folder, and outputing the errors as an Artifact
4) Merging the designs from the "submissions" folder, and outputing merged layout as an Artifact in the main repository

## Latest Merge Layout File

<!-- start-link -->
https://github.com/SiEPIC/openEBL-2024-05/actions/runs/9019883541/artifacts/1488247589
<!-- end-link -->

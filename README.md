# 4701 Practicum
NYFD Report Predictor  
Developed by Thomas Nappi (tfn9), Berk Tanyeri (bt276), Emily Parker (elp65)

# NYFD Advisor Execution Instructions
1. cd to Advisor folder
2. execute "python server.py"
3. navigate to the webpage displayed in the command line (Server started ...)
4. provide input data based on the codes at the bottom of the page
5. Click advise and recieve recommendations/advisement
   * NOTE: Impossible scenario combinations (such as "134 - Water Vehicle Fire" at "111 - Bowling Establishment") will display no recommendations and instead say "Unprecedented" for all results

# File Organization
- Root
  - README with instructions
- Advisor
  - base.html - Code for the advisor GUI
  - .pickle - Best models generated from Training folder that have the least error, used for predictions
  - At_Codes.csv - Lookup table for finding the description associated with an action code
  - server.py - backend code for predictions
- Training
  - OriginalCSVs - Folder for the original untouched data from [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/Incidents-Responded-to-by-Fire-Companies/tm6d-hbzd) from 2013 to mid 2018
  - project.ipynb - Code for training the models
  - analysis.ipynb - Code for graphical analysis of the data
  - ProjectPreProcess.ipynb - Code for preprocessing and preparing the files in OriginalCSVs for use
  - preprocessed.csv.gzip - Preprocessed data, created from ProjectPreProcess.ipynb and used in project.ipynb
  - .pickle - All models that are generated from project.ipynb
    - NOTE: Models that were determined to be the best and are used for predictions can be found in the Advisor folder; All other models that performed worse were deleted but can be obtained from running project.ipynb
  - .gzip - CSVs with compression for storage in GitHub
- Validation
  - NewCSVs - Folder for the original untouched data from [NYC Open Data](https://data.cityofnewyork.us/Public-Safety/Incidents-Responded-to-by-Fire-Companies/tm6d-hbzd) from 2020 to 2021
  - .pickle - Best models generated from Training folder that have the least error, used for prediction
  - NewData.ipynb - Code for predicting the 2020 to 2021 FDNY responses using models created using 2013 to mid 2018 datasets. Used to show our models extend well to the new data and work over time
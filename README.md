# CFT Analysis

Python package for the analysis of data collected during the Cold Face Test (CFT) procedure.

## Description

This package contains various helper functions to work with the dataset (including [`tpcp`](https://github.com/mad-lab-fau/tpcp) `Dataset` representations) and to process data. Additionally, it contains different analysis experiments performed with the dataset.

## Repository Structure
The repository is structured as follows:

```bash
├── cft_analysis/                                   # cft-analysis Python package
└── experiments/                                    # Folder with conducted analysis experiments; each experiment has its own subfolder
    └── 2022_scientific_reports/                    # Analysis for the 2022 Scientific Reports Paper (see below)
        ├── data/                                   # Processed data and extracted parameters
        ├── notebooks/                              # Notebooks for data processing, analysis and plotting
        │   ├── data_processing/            
        │   │   ├── ECG_Processing_Feature_Computation.ipynb    # Processing and feature extraction from ECG data
        │   │   ├── Questionnaire_Processing.ipynb              # Processing of questionnaire data
        │   │   └── Saliva_Processing.ipynb                     # Processing of saliva data
        │   ├── analysis/                   
        │   │   ├── Subject_Exclusion.ipynb         # Checks whether (and which) subjects need to be excluded from further analysis
        │   │   ├── Demographics.ipynb              # Analysis of general information of study population: Age, Gender, BMI, ...
        │   │   ├── ECG_Analysis.ipynb              # Descriptive and statistical analysis of ECG data
        │   │   ├── Questionnaire_Analysis.ipynb    # Descriptive and statistical analysis of questionnaire data
        │   │   └── Saliva_Analysis.ipynb           # Descriptive and statistical analysis of saliva data
        │   └── plotting/
        ├── results/                                # Plots and statistical results exported by the notebooks in the "analysis" and "plotting" folders
        └── config.json                             # 

```


## Experiments
Currently, this repository contains the following experiments:

### 2022 – Scientific Reports
Analysis of the [CFT Dataset](https://mad-srv.informatik.uni-erlangen.de/MadLab/data/health-psychology/cold-face-test-data) for the paper "Exploring the Cold Face Test as a Mechanism for Reducing Acute Psychosocial Stress Responses", submitted to *Scientific Reports* [TODO: update when published].

#### Usage
In order to run the code, first download the [CFT Dataset](https://mad-srv.informatik.uni-erlangen.de/MadLab/data/health-psychology/cold-face-test-data). Then, create a file named `config.json` in the folder `/experiments/2021_scientific_reports` with the following content:
```json
{
    "base_path": "<path-to-dataset>"
}
```
This config file is parsed by all notebooks to extract the path to the dataset.   
**NOTE**: This file is ignored by git because the path to the dataset depends on the local configuration!

The files in the `data` folder are created by running the notebooks in the `data_processing` folder. The files in the `result` folder are created by running the notebooks in the `analysis` and the `plotting` folders.



## Installation
This package uses [poetry](https://python-poetry.org/) to manage dependencies and packaging. In order to use this project for development, first install poetry, then run the following commands to get the latest source, initialize a virtual env and install all development dependencies:

With ssh access:
```bash
git clone git@mad-srv.informatik.uni-erlangen.de:MadLab/health-psychology/cft-analysis.git
cd cft-analysis
poetry install
```

With https access:
```bash
git clone https://mad-srv.informatik.uni-erlangen.de/MadLab/health-psychology/cft-analysis.git
cd cft-analysis
poetry install
```

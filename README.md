# NFC Tag Response Analysis and Prediction

This repository contains files and resources for research on NFC tag response analysis and prediction using the ISO15693 protocol. The goal of the project is to improve the reliability and security of NFC tag communication by leveraging machine learning and software-defined radio techniques.

---

## Table of Contents

- [Overview](#overview)
- [Folder Structure](#folder-structure)
  - [Machine Learning](#machine_learning)
  - [Script](#script)
    - [MATLAB](#matlab)
    - [Python](#python)
    - [MAPIE_Models](#mapie_models)
    - [GNURadio](#gnuradio)
      - [Send_Command](#send_command)
      - [Response_Collection](#response_collection)
  - [Slides](#slides)
- [Key Features](#key_features)
- [Dependencies and Setup](#dependencies-and-setup)
  - [MAPIE and scikit-learn Versions](#mapie-and-scikit-learn-versions)
- [Reference](#Reference)
- [Contacts](#Contacts)
- [Citing ISO15693-NFC-FINGERPRINT](#Citing_ISO15693-NFC-FINGERPRINT)
- [Acknowledgments](#acknowledgments)
  - WISE Lab, University of Nebraska-Lincoln, School of Computing.

---

## Overview

This project focuses on using **machine/deep learning models** and **conformal prediction** to identify NFC tags based on their unique responses to ISO15693 commands. The key component of the project is the `GNURadio` program, which integrates machine learning models to predict which NFC tag is responding to a transmitted command.

---

## Folder Structure

### Machine_Learning

This folder contains Jupyter notebooks for training and evaluating various machine learning models.  
- **`TagMAPIE.ipynb`**:  
  - Main notebook used for training MAPIE models.  
  - Evaluates accuracy for each model.  
  - Implements conformal prediction to refine the final predictions.


### Slides

- PowerPoint presentation explaining the data collection process.

### Script

- This folder contains the core code and simulations for the research, organized into subfolders:

#### MATLAB

- Contains legacy MATLAB files used in the early stages of the research.

#### Python

- Includes scripts for data visualization and testing functions before integration into the GNURadio flowgraph.

#### MAPIE_Models

- Contains seven machine learning models used in conformal prediction for NFC tag response analysis.

#### GNURadio

- This folder is the backbone of the project and includes the primary programs:

##### Send_Command

- Transmits an ISO15693 command based on the provided flag bits.

##### Response_Collection

- Collects tag responses from 52 NFC tags for training and testing machine learning models.

##### Realtime_Prediction

- **Main program of the project**.
- Performs prediction of NFC tags using conformal prediction:
  1. Sends an **inventory request** to a tag.
  2. Collects responses for **four different response types**:
     - One Subcarrier High Data Rate (OneHigh)
     - One Subcarrier Low Data Rate (OneLow)
     - Two Subcarriers High Data Rate (TwoHigh)
     - Two Subcarriers Low Data Rate (TwoLow)
  3. Uses collected responses with MAPIE models to identify the responding tag.

- **Important Notes**:
  - Requires specific versions of `MAPIE` and `scikit-learn`.
  - Requires adjusting the `self.personal_path` variable in the Predict Tag block to match your local file paths for the repository main folder.
  - The trained MAPIE models used in `Conformal prediction` program are **not included** in this repository due to their large size. 
---

## Key Features

- **Machine Learning Integration**:  
  Utilizes MAPIE and conformal prediction to enhance prediction accuracy.

- **Data Diversity**:  
  Processes four unique response types from NFC tags to train and test models.


- **ISO15693 Protocol Implementation**:  
  Uses software-defined radio to interact with NFC tags using ISO15693 commands.

---

## Dependencies and Setup

### MAPIE and scikit-learn Versions

- The `NFC Tag prediction` program requires specific versions of `MAPIE` and `scikit-learn`. Follow these steps to ensure the correct setup:

1. Open Command Prompt (CMD) as an administrator.
2. Activate the GNURadio Python environment:
   ```bash
   C:\ProgramData\radioconda\Scripts\activate
3. Check installed versions:
    ```bash
    pip show scikit-learn
    pip show mapie
4. Verify that the version are as follows:
    
    scikit-learn: __1.3.2__
    mapie: __0.9.1__
5. If they don't match:
    ```bash
    pip uninstall scikit-learn
    pip uninstall mapie
    pip install scikit-learn==1.3.2
    pip install mapie==0.9.1

### Reference
- Please visit https://github.com/adam-kamrath/ISO15693_Application to run the application in MATLAB and access all the source code.
  
### Contacts
- `dakuokosarpong2@unl.edu`

### Citing ISO15693-NFC-FINGERPRINT
- If you use `ISO15693-NFC-FINGERPRINT` in any scientific publication, we would appreciate citations to the following paper.
  You can use the following BibTeX entry:
```bash 
@article{Sarpong2025ModelAgnosticUQ,
  title={Model-Agnostic Uncertainty Quantification for Fast NFC Tag Identification Using RF Fingerprinting},
  author={Dickson Akuoko Sarpong and Adam Kamrath and Rohit Bhusal and Hongzhi Guo},
  journal={IEEE Internet of Things Journal},
  year={2025},
  volume={12},
  pages={47607-47622},
  url={https://api.semanticscholar.org/CorpusID:276961221}
}
      

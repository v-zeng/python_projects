"""
Exploratory Data Analysis on Imaging Data

Written by: Vinson Zeng

This program retrieves essential information from the DICOM headers of
medical imaging datasets. Information with the following headers are
gathered and saved to a csv file: Patient ID, Patient Age, Patient Weight,
Manufacturer Model Name, MRI image slice thickness, Study Description.
Histograms of patient age, patient weight, and slice thickness are
then created from the csv file. Finally, unique study descriptions are
counted and displayed in a simple table format.

"""


import os
import pandas
import matplotlib.pyplot as plt
from pydicom import dcmread

def getPath():
    """Obtains correct file path from user.

    :param None
    :return: dir_path
    """
    isValid = False
    while isValid == False:
        dir_path = input("\nEnter directory path: ")
        if os.path.isdir(dir_path) == False: # check if directory exists
            print("Invalid directory path, try again")
        else:
            return dir_path
            isValid == True

def lst_files(dir_path):
    """Generates list of file names ending with '.dcm' in the file path.

    :param dir_path
    :return: dcm_files
    """
    dcm_files = []
    for root, dirs, files in os.walk(dir_path):
        for names in files:
            if names.endswith(".dcm"):
                dcm_files.append(os.path.join(root, names))
    return dcm_files

def read_file(data_path):
    """ Reads DICOM files.

    :param data_path: the path to the DICOM file
    :return: ds = DICOM stucture
    """
    ds = dcmread(data_path)
    return ds

def create_ds_list(dcm_files):
    """Reads list of dcm files and returns list of DICOM structures.

    :param dcm_files = list of files ending with '.dcm' from file path
    :return: ds_list
    """
    ds_list = []
    for file in dcm_files:  # for each file in the list of file paths
        ds = read_file(file) # read the file and return the DICOM structure
        ds_list.append(ds)
    return ds_list

def patient_info(ds_list):
    """Creates a dictionary for each patient with the following keys:
    'PatientAge', 'PatientWeight', 'MRI_Model', 'SliceThickness', 'StudyDescription'.
    Corresponding values are obtained from the DICOM data in ds_list.

    :param ds_list = list of DICOM structure data
    :return: patient_data_list
    """
    patient_data_list = []
    for ds in ds_list:
        info = {"PatientID": ds.PatientID,
                        "PatientAge": ds.PatientAge,
                        "PatientWeight": ds.PatientWeight,
                        "MRI_Model": ds.ManufacturerModelName,
                        "SliceThickness": ds.SliceThickness,
                        "StudyDescription": ds.StudyDescription}
        patient_data_list.append(info)
    return patient_data_list

def create_dataFrame(patient_data_list):
    """Creates dataframe from the patient_data_list.

    :param patient_data_list: list of patient data from DICOM headers
    :return: patientDataFrame
    """
    patientDataFrame = pandas.DataFrame(patient_data_list)
    return patientDataFrame

def getSavePath():
    """Obtains save path for saving a csv file.

    :return: csv_path
    """
    isValid = False
    while isValid == False:
        csv_path = input("\nEnter a save path for the csv: ")
        checkCsvPath = input(f"\nIs {csv_path} correct? (Enter 'y' if correct): ")
        if checkCsvPath.lower() == 'y':
            isValid = True
            return csv_path
        else:
            print("\nPlease try again")

def save_csv(patientDataFrame,csv_path):
    """Saves patientDataFrame as a csv file.

    :param patientDataFrame: dataframe of all patient data
    :param csv_path: save path for csv file as specified by user
    :return: None
    """
    patientDataFrame.to_csv(csv_path,index=False)

def createHistAge(df_patients):
    """Creates a histogram of patient age.

    :param df_patients: dataframe list of patients from csv file
    :return: histogram of 'PatientAge'
    """
    df_patients['PatientAge'] = df_patients['PatientAge'].str.extract('(\d+)',expand=False) # pass regex pattern to extract just numeric part from 'PatientAge'
    df_patients['PatientAge'] = df_patients['PatientAge'].astype(int) # convert Dtype of 'PatientAge' to integer

    patient_age = df_patients['PatientAge']
    # label histogram
    plt.xlabel('Age')
    plt.ylabel('Count')
    plt.title('Number of Patients by Age')
    # add grid
    plt.grid()
    plt.hist(patient_age,bins='auto')
    plt.show()

def createHistSlice(df_patients):
    """Creates a histogram of MRI slice thickness.

    :param df_patients: dataframe list of patients from csv file
    :return: histogram of 'SliceThickness'
    """
    sliceThickness = df_patients['SliceThickness']
    # label histogram
    plt.xlabel('Slice Thickness')
    plt.ylabel('Count')
    plt.title('MRI Image Slice Thickness')
    # add grid
    plt.grid()
    plt.hist(sliceThickness,bins='auto')
    plt.show()

def createHistWeight(df_patients):
    """Creates histogram of patient weight.

    :param df_patients: dataframe list of patients from csv file
    :return: histogram of patient weight
    """
    patient_weight = df_patients['PatientWeight']
    # label histogram
    plt.xlabel('Weight')
    plt.ylabel('Count')
    plt.title('Number of Patients by Weight')
    # # add grid
    plt.grid()
    plt.hist(patient_weight,bins='auto')
    plt.show()

# summary of study description
def processData(df_patients):
    """Splits data based on unique values under 'StudyDescription' data header
    and returns count for each.

    :param df_patients: dataframe list of patients from csv file
    :return: printout of study description summary in table format
    """
    # return number of unique study descriptions
    studySummary = df_patients.groupby('StudyDescription').size().reset_index().rename(columns={0:'PatientID'})
    return studySummary

def main():
    """Main function of Exploratory Data Analysis on Imaging Data"""

    # Create Info Sheet
    dir_path = getPath() # get directory path
    dcm_files = lst_files(dir_path) # get list of dcm file paths
    ds_list = create_ds_list(dcm_files) # get list of DICOM structure for each file
    patient_data_list = patient_info(ds_list) # for each patient create a dictionary from the DICOM structure
    patientDataFrame = create_dataFrame(patient_data_list) # create dataframe for each patient in patient_data_list
    csv_path = getSavePath() # get csv path save location from user
    save_csv(patientDataFrame,csv_path) # save dataframe to csv
    df_patients = pandas.read_csv(csv_path) # read in dataset from csv file

    # create histograms
    createHistAge(df_patients) # create histogram of patient age
    createHistSlice(df_patients) # create histogram of slice thickness
    createHistWeight(df_patients) # create histogram of patient weight

    # create summary of Study Description and save to csv
    studySummary = processData(df_patients) # create summary of description
    print(studySummary)
    print("\nProgram will now save the study summary")
    summary_csv_path = getSavePath()
    save_csv(studySummary,summary_csv_path)

main()

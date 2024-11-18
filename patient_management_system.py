import random
import string
import os
import pandas as pd

#"C:\\Users\\Vins\\Desktop\\MBI_Courses\\BMIF_801\\mini_project\\initial_hospital_state.csv"
# get file path
def getFilePath():
    isValid = True
    while isValid == True:
        filePath = input("Enter file path: ")
        if not os.path.isfile(filePath):
            print("\nThere's no file there, try again.")
            continue
        return filePath
        isValid = False

# main menu message
def mainMenuMessage():
    print("Main Menu\n*************************************************") # make this fancier later
    print(
        "   1. Add patient\n"
        "   2. Transfer Patient\n"
        "   3. Update patient status\n"
        "   4. Discharge patient\n"
        "   5. Patient list\n"
        "*************************************************"
        )

def getUserChoice():
    isValid = True
    while isValid == True:
        userChoice = input("\nEnter a number from 1 to 5 or type 'exit': ")
        if userChoice.lower() == 'exit':
            return userChoice
            isValid = False
        elif userChoice.isdigit() == True and 1<=int(userChoice)<=5:
            return userChoice
        else:
            print("Try again.")

class PatientManagementSystem:
    # Read inital CSV file
    def read_hospital_csv(self,filePath):
        df = pd.read_csv(filePath) # file path may differ
        df = df.iloc[:, 1:] # ignore index column
        return df

    # Group data by hospital
    def group_by_hospital(self, df):
        grouped_df = df.groupby(['Hospital']).size().to_frame()
        grouped_df.reset_index(level=0, inplace=True)
        grouped_df.columns = ['Hospitals', 'NumberOfPatients']
        return grouped_df

    # Function for adding a patient
    def add_patient(self, hospitalName, sevStatus, covidPositive):
        nums = random.choices(string.digits, k=3) # return 3 random numbers
        alpha = random.choices(string.ascii_lowercase, k=1) # return random lowercase letter
        id = ''.join(nums + alpha) # create patientID
        df = self.read_hospital_csv()
        grouped_df = self.group_by_hospital(df)
        print(grouped_df)
        x = int(grouped_df[grouped_df['Hospitals'] == hospitalName]['NumberOfPatients'])
        if hospitalName == 'Toronto' and x < 20:
            df.loc[len(df)] = [id, hospitalName, sevStatus, covidPositive]
            df.to_csv("initial_hospital_state.csv", sep=',')
        elif hospitalName == 'Hamilton' and x < 13:
            df.loc[len(df)] = [id, hospitalName, sevStatus, covidPositive]
            df.to_csv("initial_hospital_state.csv", sep=',')
        elif hospitalName == 'Kingston' and x < 10:
            df.loc[len(df)] = [id, hospitalName, sevStatus, covidPositive]
            df.to_csv("initial_hospital_state.csv", sep=',')
        else:
            print("Cannot transfer to " + hospitalName + " Hospital as the ICU at " + hospitalName + " is full.")
            print("Please transfer to another hospital")
            newHospitalName_2 = input('Enter the new hospital')
            self.add_patient(newHospitalName_2, sevStatus, covidPositive)
        main() # run main again

    # Function for transfering a patient
    def transfer_patient(self, patientID, newHospitalName):
        df = self.read_hospital_csv()
        grouped_df = self.group_by_hospital(df)

        x = int(grouped_df[grouped_df['Hospitals'] == newHospitalName]['NumberOfPatients'])
        print(x)
        if newHospitalName == 'Toronto' and x < 20:
            df = self.read_hospital_csv()
            df.loc[df.Patient_ID == patientID, 'Hospital'] = newHospitalName
            print(df)
            df.to_csv("initial_hospital_state.csv", sep=',')
        elif newHospitalName == 'Hamilton' and x < 13:
            df = self.read_hospital_csv()
            df.loc[df.Patient_ID == patientID, 'Hospital'] = newHospitalName
            print(df)
            df.to_csv("initial_hospital_state.csv", sep=',')
        elif newHospitalName == 'Kingston' and x < 10:
            df = self.read_hospital_csv()
            df.loc[df.Patient_ID == patientID, 'Hospital'] = newHospitalName
            print(df)
            df.to_csv("initial_hospital_state.csv", sep=',')
        else:
            print("Cannot transfer to " + newHospitalName + " Hospital as the ICU at " + newHospitalName + " are full.")
            print("Please transfer to another hospital")
            newHospitalName_2 = input('Enter the new hospital')
            self.transfer_patient(patientID, newHospitalName_2)
        main()

    # Function for discharging a patient
    def discharge_patient(self, pateintID):
        df = self.read_hospital_csv()
        df.drop(df[df.Patient_ID == pateintID].index, inplace=True)
        df.reset_index(drop=True)
        df.to_csv("initial_hospital_state.csv", sep=',')
        main()

    # Function for Updating Status for a patient
    def update_status(self, patientID, newStatus):
        df = self.read_hospital_csv()
        df.loc[df.Patient_ID == patientID, 'Status'] = newStatus
        print(df)
        df.to_csv("initial_hospital_state.csv", sep=',')
        main()

filePath = getFilePath() # I put this outside since I looped by using calling main()
def main():

    # Main function for the program
    x = PatientManagementSystem()
    dfPatients = x.read_hospital_csv(filePath) # change to correct file path if required
    print("\nWelcome to the VinsCorp Patient Management System.")
    mainMenuMessage()
    userChoice = getUserChoice()


    # add patient
    if userChoice == '1':
        hospital = input('Enter the hospital where the patient has to be added: ')
        sevStatus = input('Enter severity status of the patient: ')
        covidPositive = input('Enter if the patient has been detected covid or not: ')
        x.add_patient(hospital, sevStatus, covidPositive)

    # transfer patient
    elif userChoice == '2':
        patientID = input('Enter patient ID: ')
        newHospitalName = input('Enter the hospital where the patient should be transferred: ')
        x.transfer_patient(patientID, newHospitalName)

    # discharge patient
    elif userChoice == '3':
        patientID = input('Enter patient ID: ')
        x.discharge_patient(patientID)

    # update patient
    elif userChoice == '4':
        patientID = input('Enter patient ID: ')
        newStatus = input("Enter patient's updated status: ")
        x.update_status(patientID, newStatus)

    # print patient list
    elif userChoice == '5':
        print(dfPatients)
        main()

    # exit program
    elif userChoice == 'exit':
        print("\nTerminating program, goodbye.")
        quit() # stop script execution


# Run main function from the df_pms.py script
if __name__ == '__main__':
    main()

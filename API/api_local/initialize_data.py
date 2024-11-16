'''
This file MUST BE RAN ON THE ROOT DIR!
'''

import subprocess, os, argparse

def empty_stock():
    folder_path = "./API/api_local/Data/Stocks/"
    file_list = os.listdir(folder_path) # Get a list of files in the folder

    # Iterate through the file list and remove each file
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser()
    # Add arguments for each environmental variable
    parser.add_argument('-u', '--update_name_code', action='store_true', help='Update Name Code')
    # Parse the command-line arguments
    args = parser.parse_args()
    # Set the environmental variables based on the parsed arguments
    if args.update_name_code:
        os.environ['UPDATE_NAME_CODE'] = "True"

    file1 = "API/api_local/create_name_code.py"
    file2 = "API/api_local/create_stock_prices.py"
    file3 = "API/api_local/create_basic_info.py"
    file4 = "API/api_local/create_bf_for_analysis.py"

    update_name_code = os.environ.get("UPDATE_NAME_CODE", "False")

    #WHEN YOU WANT TO UPDATE THE LIST OF COMPANIES SUPPORTED
    if update_name_code == "True":
        #1. Creating the name_code
        print('#' * 100)
        print("\nSYSTEM: Creating name_code.pkl file......")
        subprocess.run(['python3', file1])
        print("\nSYSTEM: Finished creating name_code.pkl file")

        #2. Creating all the Stock prices for each cmpny
        print('#' * 100)
        print("\nSYSTEM: Emptying folder /API/api_local/Data/Stocks/")
        empty_stock()
        print("\nSYSTEM: Finished emptying")
        print('#' * 100)
        print("\nSYSTEM: Creating stock price files......")
        subprocess.run(['python3', file2])
        print("\nSYSTEM: Finished creating stock price files")

    #3. Creating the basic info
    print('#' * 100)
    print("\nSYSTEM: Creating basic_info.csv file......")
    subprocess.run(['python3', file3])
    print("\nSYSTEM: Finished creating basic_info.csv file")
    
    #4. Creating the basic info for analysis
    print('#' * 100)
    print("\nSYSTEM: Creating basic_info_for_analysis.csv file......")
    subprocess.run(['python3', file4])
    print("\nSYSTEM: Finished creating basic_info_for_analysis.csv file")

if __name__ == "__main__":
    main()
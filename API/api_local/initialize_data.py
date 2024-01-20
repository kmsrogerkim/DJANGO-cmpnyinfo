import subprocess

def main():
    file1 = "API/api_local/create_name_code.py"
    file2 = "API/api_local/create_basic_info.py"
    file3 = "API/api_local/create_bf_for_analysis.py"

    #1. Creating the name_code
    print("\nSYSTEM: Creating name_code.pkl file......")
    print('#' * 100)
    subprocess.run(['python', file1])
    print("\nSYSTEM: Finished creating name_code.pkl file")

    #2. Creating the basic info
    print("\nSYSTEM: Creating basic_info.csv file......")
    print('#' * 100)
    subprocess.run(['python', file2])
    print("\nSYSTEM: Finished creating basic_info.csv file")
    
    #1. Creating the basic info for analysis
    print("\nSYSTEM: Creating basic_info_for_analysis.csv file......")
    print('#' * 100)
    subprocess.run(['python', file3])
    print("\nSYSTEM: Finished creating basic_info_for_analysis.csv file")

if __name__ == "__main__":
    main()
from matplotlib import pyplot as plt
from matplotlib import rcParams
from tabulate import tabulate
import seaborn as sns
import pandas as pd

def ShowStatusBoxPlot(data: pd.DataFrame, key: str):
    plt.figure(figsize = (10, 6))
    graph_data = []
    for state in ["P_Contd", "L_Contd", "P_Turned", "L_Turned"]:
        value = data[data[key] == state]
        if value.empty:
            graph_data.append(0)
        else:
            graph_data.append(value["Profit"])
    plt.boxplot(graph_data)
    plt.ylim(-100, 100)
    plt.xticks([1, 2, 3, 4], ["P_Contd", "L_Contd", "P_Turned", "L_Turned"])
    plt.ylabel("Profit")
    plt.show()

def main():
    company_name = "삼성전자"

    cols = ["Company_Name", "Year", "Current_Stock", "Future_Stock", "Operating_Income(added)_Profit_Status","Net_Income(added)_Profit_Status" ]
    data = pd.read_csv(f"./Data/{company_name}_basic_info_for_analysis.csv", usecols=cols, encoding="euc-kr")
    data.dropna(inplace=True)

    data["Profit"] = (data["Current_Stock"] - data["Future_Stock"]) / data["Current_Stock"] * 100

    #Visualizing Operating Income
    ShowStatusBoxPlot(data, key="Operating_Income(added)_Profit_Status")
    #Visualizing Net Income
    ShowStatusBoxPlot(data, key="Net_Income(added)_Profit_Status")

if __name__ == "__main__":
    main()
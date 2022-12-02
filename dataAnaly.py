# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

### Clean data
df = pd.read_csv("acElecData.csv", sep= ";", encoding = 'unicode_escape', engine ='python')
df.columns
df = df.iloc[:,[0,1,2,4,7,8,10,11,13,15,16]]
df.rename({"nElectoresAC":"electorate", 
           "nVotosCandidaturaAC": "votesTotal",
           "sumVotesEachPartyACTotal":"votesParty",
           "sumVotesEachPartyACTotalDividedBynVotosCandidaturaAC":"votePerc",
           "totalDepsAvailableInAC" : "depsTotal",
           "totalDepsPerPartyPerAC": "depsParty",
           "totalDepsPerPartyPerACDividedByTotalDepsAvailablePerAC":"depsPerc"},
          axis = 1, inplace = True)

#Convert to right type
df.replace({"#VALUE!":np.NaN}, inplace = True)
df.dtypes
df.iloc[:,[1,4,5,6,8,9]] = df.iloc[:,[1,4,5,6,8,9]].astype("Int64")
df.iloc[:, [7, 10]] = df.iloc[:, [7, 10]].astype("float64")

#Check date data and make date var!!!!!!
np.sum((df.year < 1979) | (df.year > 2020))
np.sum((df.month < 0) | (df.month > 12))
df["date"] = pd.to_datetime(df.month.astype(str) + df.year.astype(str),  
                            format='%m%Y', errors='coerce')

# Data quality check
partyNames = list(df.party.unique())
partyNames.sort()
for i in zip(["PSC-PSOE", "PSE-PSOE", "PSN-PSOE", "GxF+PSIB-PSOE+EUIB", 
              "(UPN-)AP/PP", "AP", "Navarra Suma"], 
             ["PSOE"]*4 + ["PP"]*3):
    df.party.replace(i[0], i[1], inplace = True)
df.party.unique()

#Missing values
df.isna().sum()
#Funtion to fill in missing data
def fillInVals(df, var, datatype = int):
    """Func to insert missing values. Argumens: df, name of object; var, 
    name of var as string; datatype, data type directly, no quotation marks"""
    df_copy = df[df[var].isna()]
    for rowIndex, series in df_copy.iterrows():
        print(rowIndex)
        print(series)
        insertVal = input("Insert missing val for " + var + " for\n" + str(df.iloc[rowIndex][["year", "AC"]])+":")
        if type(insertVal) is not datatype:
            if (datatype == int) | (datatype == float):
                insertVal = pd.to_numeric(insertVal)
        df.iloc[rowIndex, series.index.get_loc(var)] = insertVal
    return df

fillInVals(df, "depsParty")   

#Check duplicate rows and drop
sum(df.duplicated())
df.drop_duplicates(inplace = True)

# Recalculating percentage of deputies and votes vars with additional data and to assure data integrity
df["votePerc"] = (df["votesParty"]/df["votesTotal"])*100
df["depsPerc"] = (df["depsParty"]/df["depsTotal"])*100
df.to_pickle("acElecDataClean.pkl")

####################################################################################
df = pd.read_pickle("acElecDataClean.pkl")

colPal = ["#FF0000", "#0000FF"]
colOrder = ["PSOE", "PP"]
yearParams = [[1978, 2022], [1978, 1996], [1996, 2015], [2015, 2022]]

plt.rcParams.keys()
plt.rcParams.update({'font.size': 14, 'font.family': 'Times New Roman',
                     'figure.titlesize': "xx-large",
                     "axes.titlesize":"large",
#                     'axes.labelsize': 'medium',
                     "figure.dpi": 200.0})
#fontsizefloat or {'xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large'}

### Boxplot, PSOE and PP by AC across time (boxplot)
majorParties = df[(df["party"].isin(["PSOE", "PP"]))].sort_values("AC")
orderPlot = majorParties.groupby(["party", "AC"]).votePerc.median().reset_index().sort_values(["party", "votePerc"], ascending = [True, True])
orderPlot.set_index(orderPlot.party+orderPlot.AC, inplace = True)
orderPlot.index.values

majorParties.set_index(majorParties.party+majorParties.AC, inplace = True)
majorParties["majorPartiesCats"] = majorParties.index.values
plotBox = sns.catplot(x = "votePerc", 
            y = "majorPartiesCats", 
            kind = "box", 
            palette = colPal,
            hue = "party", 
            order = orderPlot.index.values,
            height=15, aspect=1.2,
            data = majorParties,
            facet_kws={'legend_out': True})
plotBox._legend.set_title("Party")
plotBox.set_yticklabels(majorParties.groupby(["party", "AC"]).votePerc.median().reset_index().sort_values(["party", "votePerc"], ascending = [True, True])["AC"])
plt.xlabel("Vote percentage")
plt.ylabel("Autonomous Community")
plotBox.fig.suptitle("Election results by AC across time", y = 1.025)

### Main parties across time periods by AC
majorParties.reset_index(drop = True, inplace = True) 
def partySysPhases(yearStartEnd, df = majorParties, y = "votePerc", titleInsert = "election results",
                   hline = False):
    """yearStartEnd is list containing integer of start and integer of end of period """
    yearStart = yearStartEnd[0]
    yearEnd = yearStartEnd[1]
    df = df[df["year"].isin([i for i in range(yearStart, yearEnd)])].sort_values("AC")
    fig1 = sns.relplot(x= "date", y = y, 
                       hue="party", 
                       palette = colPal, 
                       hue_order = colOrder, 
                       kind="line", 
                       linewidth = 2.75, 
                       marker = "o", 
                       col = "AC", 
                       col_wrap = 3, 
                       data = df,
                       facet_kws={'legend_out': True})
    fig1._legend.set_title("Party")
    fig1.fig.suptitle("PP and PSOE "+titleInsert+", "+str(yearStart)+"-"+str(yearEnd), y = 1.015)
    fig1.set_axis_labels("Year", "Vote percentage")
    axes = fig1.axes.flatten()
    for i, name in enumerate(df.AC.unique()):
        print(i, name)
        axes[i].set_title(name)
    for ax in axes:
        ax.tick_params(labelbottom=True)
        if hline == True:
            ax.axhline(0, linestyle = "--", color = "black")
    plt.subplots_adjust(wspace = 0.1)
    plt.show(fig1)
    return fig1
ACs7896 = partySysPhases(yearParams[1])

### Diff in percentage with rolling average, one plot for trend
majorParties = majorParties.sort_values(["AC", "party", "year", "month"])
majorParties["votePercLagged"] = majorParties.groupby(["AC", "party"])["votePerc"].shift(1)
majorParties["votePercDiff"] = majorParties.votePerc - majorParties.votePercLagged

#17 comunidades, 13 normalmente votan juntos
majorParties2 = majorParties
majorParties2['rollingVotePercDiff'] = majorParties.sort_values(["year", "month"]).\
    groupby("party")["votePercDiff"].transform(lambda x: x.rolling(13).mean())
majorParties2 = majorParties2[["rollingVotePercDiff", "party", "date"]].rename({"rollingVotePercDiff":"votePercDiff",}, axis = "columns")
majorParties2["AC"] = "yRollingAvg"
majorPartiesRoll = pd.concat([majorParties, majorParties2]).reset_index(drop=True)

fig2 = sns.relplot(x = "date", y = "votePercDiff", 
                   col ="party", 
                   col_order = colOrder,
                   hue = "AC",
                   palette = ["gray"]*(len(majorPartiesRoll.AC.unique())-1)+["black"],
                   kind = "line",
                   legend = False,
                   data = majorPartiesRoll) 
fig2.fig.suptitle("Overview of vote evolution across time", y = 1.05)
fig2.set_axis_labels("Year", "Vote difference (percent)")
axes = fig2.axes.flatten()
for i, name in enumerate(colOrder):
    axes[i].set_title(name)

### Means and std for different periods
period = []
for year in majorParties["year"]:
    if year < 1993:
        period.append("1978-92")
    elif year < 2011:
        period.append("1993-2010")
    elif year < 2016:
        period.append("2011-15")
    else:
        period.append("2016-22")
majorParties["period"] = period
majorParties["period"] = majorParties.period.astype("category")

stats = majorParties.groupby(["period", "party"])[["votePerc"]].agg(["mean", "std"]).round(2).reset_index()
fig3 = sns.catplot(x = "period", y= "votePerc", hue = "party", kind = "point", 
            palette = colPal,
            hue_order = colOrder,
            dodge = True,
            capsize = .3,
            data = majorParties,
            facet_kws={'legend_out': True})
fig3._legend.set_title("Party")
fig3.fig.suptitle("Mean vote change across different periods", y = 1.05)

### Diff in percentage of vote across time by AC
partySysPhases(yearParams[0], df = majorParties, y = "votePercDiff", hline = True, titleInsert = "vote percentage changes")

### Heatmaps across time
def heatMap(yearStartEnd, df = majorParties):  
    yearStart = yearStartEnd[0]
    yearEnd = yearStartEnd[1]
    df = df[df["year"].isin([i for i in range(yearStart, yearEnd)])]
    df = df[["AC", "party", "votePerc"]].pivot_table(columns="party", index="AC", values ="votePerc").iloc[:,[1,0]].sort_values("PSOE", ascending = False)
    df = df.astype("float")
    plt.figure(figsize = (9,8))
    heatMap = sns.heatmap(df, annot=True, fmt=".1f", cmap ="RdYlGn")
    plt.xlabel("Party")
    plt.ylabel("Autonomous Community")
    heatMap.set_title("Average election results, " + str(yearStartEnd[0]) + "-" + str(yearStartEnd[1]), y = 1.025)
    return heatMap
out = heatMap(yearParams[0])    


### Absolute majorities
absMaj = majorParties[majorParties["depsPerc"] >= 50].groupby(["party", "AC"])[["AC"]].count().rename({"AC":"Count"}, axis = 1)
absMaj = absMaj[absMaj["Count"]!=0].sort_values(["party", "Count"], ascending = False)
# also by period
absMajPeriod = majorParties[majorParties["depsPerc"] >= 50].groupby(["party", "period", "AC"])[["AC"]].count().rename({"AC":"Count"}, axis = 1)
absMajPeriod = absMajPeriod[absMajPeriod["Count"]!=0].sort_values(["party", "period", "Count"], ascending = [True, False, False]).reset_index()
absMajAgg = absMajPeriod.groupby(["period", "party"]).sum("Count").reset_index()

fig4 = sns.relplot(x= "period", 
            y= "Count", 
            hue="party", 
            palette = colPal, 
            hue_order = colOrder, 
            linewidth = 2.75, 
            marker = "o",  
            kind="line", 
            data = absMajAgg,
            facet_kws={'legend_out': True})
fig4._legend.set_title("Party")
fig4.set_axis_labels("Period")
fig4.fig.suptitle("Number of absolute majorities", y = 1.05)

### Minor observation
propCorr = df[["votePerc", "depsPerc", "AC"]].groupby("AC").corr().votePerc
propCorr[propCorr != 1.0].reset_index().drop("level_1", axis = 1).sort_values("votePerc")


period = []
for year in majorParties["year"]:
    if year < 1993:
        period.append("1978-92")
    elif year < 2011:
        period.append("1993-2010")
    elif year < 2016:
        period.append("2011-15")
    else:
        period.append("2016-22")
majorParties["period"] = period
majorParties["period"] = majorParties.period.astype("category")

stats = majorParties.groupby(["period", "party"])[["votePercDiff"]].agg(["mean", "std"]).round(2).reset_index()

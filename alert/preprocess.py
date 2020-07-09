import scipy
from scipy import stats
import numpy as np
import math
import itertools

def get_preprocessed_data(g_data,param,internalParam):
    """Set docstring here.

    Parameters
    ----------
    g_data: 
    param: 
    internalParam: 

    Returns
    -------

    """
    g_data = create_new_cols(g_data)
    ppdrList = PreProcessData(g_data,param,internalParam)
    return ppdrList



def create_new_cols(g_data):
    """Set docstring here.

    Parameters
    ----------
    g_data: 

    Returns
    -------

    """
    import numpy as np
    for row in g_data:
        # Add some columns
        if(row['NT']>0 and row['NC']>0):
            row["DeltaAbs"] = row["AvgT"] - row["AvgC"]
            row["CleanAvgC"] = row["AvgC"] if (row["AvgC"] > 0) else 0.0
            # print(row["CleanAvgC"])
            if(row["CleanAvgC"]):
                row["DeltaRatio"] = float(np.divide(row["DeltaAbs"], row["CleanAvgC"]))
            else:
                row["DeltaRatio"] = 0.0
            # self.DeltaRatio = self.DeltaAbs / self.CleanAvgC # Can be Double.PositiveInfinity, Double.NegativeInfinity, or Double.Nan

            row["StdErr"] = np.sqrt(
                float(row["StdDevT"] * row["StdDevT"]) / row["NT"] + float(row["StdDevC"] * row["StdDevC"]) / row["NC"])  # Welch
            row["DeltaAbsNormalize"] = float(
                row["DeltaAbs"]) / np.sqrt((1.0 / row["NT"]) + (1.0 / row["NC"]))
            row["Nsum"] = row["NT"] + row["NC"]
            row["Nmin"] = np.min([row["NT"], row["NC"]])

    return g_data
    
# ppdrs = preprocessed data
# Exclude rows with NT=0 or NC=0
# makes vertical in lower case
# makes rollupunit in lower case
# after above 
# Eliminate rows with SRM
# Eliminate Reverse experiments for now

def PreProcessData(drs, param, internalParam):
    """Set docstring here.

    Parameters
    ----------
    drs: 
    param: 
    internalParam: 

    Returns
    -------

    """
    ppdrList = []
    drsFiltered = [dr for dr in drs if (
        (dr["Vertical"].lower() == param["Vertical"].lower())
        and (dr["MetricName"].lower() == param["MetricName"].lower())
    #         and (dr["RollupUnit"].lower() == param["RollupUnit"].lower())
        and (dr["NT"] > 0)
        and (dr["NC"] > 0)
    )]
    #        if (param.Market is not None):
    #            drsFiltered = [dr for dr in drsFiltered if (dr.Market.lower() == param.Market.lower())]
    for row in drsFiltered:
        # Eliminate rows with SRM
        uCntT = row["UserCountT"]
        uCntC = row["UserCountC"]
        trafficT = row["TrafficT"]
        trafficC = row["TrafficC"]
        uCntTIdeal = float((uCntT + uCntC) * trafficT) / (trafficT + trafficC)
        uCntCIdeal = float((uCntT + uCntC) * trafficC) / (trafficT + trafficC)
        srmPVal = scipy.stats.chisquare([uCntT, uCntC], [uCntTIdeal, uCntCIdeal])[1]
        if (srmPVal > internalParam["SrmThreshold"]):
            # Eliminate Reverse experiments for now
            if (row["IsReverseExperiment"] == False):
                # Use this row
    #                 ppdr = PrePropDataRow(row, param, internalParam)
                ppdrList.append(row)
    #     ppdrList = PrePropDataRow.AddNumSegments(ppdrList)
    
    return ppdrList


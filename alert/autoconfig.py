import scipy
from scipy import stats
import numpy as np
import math
import itertools

def get_auto_config(param,internalParam,ppdrList):
    """Set docstring here.

    Parameters
    ----------
    param: 
    internalParam: 
    ppdrList: 

    Returns
    -------

    """ 
    #Read autoconfig parameters from data
    autoconfig_res = {
        "prio0":{
            "auto0":[],
            "auto1":[],
            "auto2":[]
        },
        "prio1":{
            "auto0":[],
            "auto1":[],
            "auto2":[]
        },
        "prio2":{
            "auto0":[],
            "auto1":[],
            "auto2":[]
        }
    }

    for priority in [0, 1, 2]:
        for isPositiveGood in [None,True, False]:
            if(isPositiveGood is None):
                Auto = 'auto0'
            elif(isPositiveGood is True):
                Auto = 'auto1'
            else:
                Auto = 'auto2'
            alertSetting = ConfigureAlert(ppdrList, param, internalParam,isPositiveGood,priority)

            # # Evaluate alertSetting against data
            # edrs = EvalDataRow.EvaluateAlert(ppdrs, alertSetting)

            # # Visualization of alert
            # myPrint(Visualizer.GetString(edrs))

            # Add alert config as AuxData
            isPosiGoodMode = 1 if isPositiveGood else (2 if isPositiveGood==False else 0) # 0:None, 1:True, 2:False
            autoconfig_res['prio'+str(priority)][Auto] = [(v) for k,v in alertSetting.items()]
            

    return autoconfig_res



def GetIndependentRows(ppdrs):
    """Set docstring here.

    Parameters
    ----------
    ppdrs: 

    Returns
    -------

    """
    indRows = []
    dat = [ppdr for ppdr in ppdrs if ppdr['FlightTypeC'] != 'StandardControl']
    dat = sorted(dat, key=lambda x: (x['ScorecardId'], -x['Nsum'], x['SegmentValue1'], x['SegmentValue2']))
    for scorecardId, group in itertools.groupby(dat, lambda x: x['ScorecardId']):
        indRows.append(next(group))

    return indRows

def GetQuantile(dat, pct):
    """Set docstring here.

    Parameters
    ----------
    dat: 
    pct: 

    Returns
    -------

    """
    if(len(dat)==0):
        return 0
    a = np.array(dat)
    return np.percentile(a, pct * 100)  # Default is linear interpolation
    # return np.percentile(a, pct * 100, interpolation='lower')

def GetMinCount(ippdrs, internalParam):
    """Set docstring here.

    Parameters
    ----------
    ippdrs: 
    internalParam: 

    Returns
    -------

    """
    myList = [np.min([item['NT'], item['NC']]) for item in ippdrs]
    minCount = GetQuantile(myList, internalParam['ReqCountPercentile'])

    minCount = max(minCount, internalParam['ReqCountMinLimit'])  # make it larger than MinCountMinLimit
    minCount = min(minCount, internalParam['ReqCountMaxLimit'])  # make it smaller than MinCountMaxLimit

    # Round to 100s (when <=1000) or 1000s (when 1000<)
    if (minCount < 1000):
        minCount = int(math.floor(int(float(minCount) / 100) * 100))
    else:
        minCount = int(math.floor(int(float(minCount) / 1000) * 1000))
    return minCount

def EliminateAbnormalPoints(ippdrs, minCount, internalParam):
    """Set docstring here.

    Parameters
    ----------
    ippdrs: 
    minCount: 
    internalParam: 

    Returns
    -------

    """
    cleanPpdrList = []
    zTh = math.fabs(scipy.stats.norm.ppf(internalParam["PValNormalThreshold"]))
    for ppdr in ippdrs:
        if (ppdr["DeltaAbs"] == 0.0 and ppdr["StdErr"] == 0.0):
            zVal0 = 0.0
        else:
            zVal0 = float(ppdr["DeltaAbs"]) / ppdr["StdErr"]
    #         when zTS > Zcritical i.e Zval0>Zth,means p-val>pvalnormalth thus we fail to reject null
        if (ppdr["Nmin"] >= minCount and math.fabs(zVal0) < zTh):
            cleanPpdrList.append(ppdr)
    return cleanPpdrList

def Median(dat):
    """Set docstring here.

    Parameters
    ----------
    dat: 

    Returns
    -------

    """
    return GetQuantile(dat, 0.5)

def Variance(dat):
    """Set docstring here.

    Parameters
    ----------
    dat: 

    Returns
    -------

    """
    return np.var(dat)

def RoundToSignif(d, digits):
    """Set docstring here.

    Parameters
    ----------
    d: 
    digits: 

    Returns
    -------

    """
    scale = 10 ** np.floor(np.log10(np.abs(d)) + 1)
    return scale * np.round(float(d) / scale, decimals=digits)

def GetAlertRange(cleanPpdrs, isPositiveGood, minCount, sdFactor, minRangeLimit):
    """Set docstring here.

    Parameters
    ----------
    cleanPpdrs: 
    isPositiveGood: 
    minCount: 
    sdFactor: 
    minRangeLimit: 

    Returns
    -------

    """
    absll = None
    absul = None
    ratioll = None
    ratioul = None
    cleanAvgCList = [item["CleanAvgC"] for item in cleanPpdrs]
    cleanMedianAvgC = Median(cleanAvgCList)

    if (cleanMedianAvgC == 0.0):
        ratioll = -minRangeLimit
        ratioul = minRangeLimit
        if (isPositiveGood is not None):
            ratioul = np.inf
        else:
            ratioll = -np.inf
    else:
        deltaAbsNormalizeList = [item["DeltaAbsNormalize"] for item in cleanPpdrs]
        sd = math.sqrt(Variance(deltaAbsNormalizeList))
        dratio = float(sdFactor * sd) / cleanMedianAvgC  # Positive
        dratio = RoundToSignif(dratio, 1)
        if (dratio < minRangeLimit):
            dratio = minRangeLimit
        if (isPositiveGood is None):
            ratioll = -dratio
            ratioul = dratio
        elif (isPositiveGood == False):
            ratioll = -np.inf
            ratioul = dratio
        else:
            ratioll = -dratio
            ratioul = np.inf

    # ratioll is always >=-1.0, so it doesn't make much sense when it's too close to -1.0
    if (ratioll != -np.inf and ratioll < -0.5):
        ratioll = -0.5
    
    AlertRange = {"AbsLowerLimit":absll,"AbsUpperLimit":absul,"RatioLowerLimit":ratioll,"RatioUpperLimit":ratioul}

    return AlertRange

def ConfigureAlert(ppdrs, param, internalParam,isPositiveGood,priority):
    """Set docstring here.

    Parameters
    ----------
    ppdrs: 
    param: 
    internalParam: 
    isPositiveGood: 
    priority: 

    Returns
    -------

    """   
    # Get independent rows
        indPpdrs = GetIndependentRows(ppdrs)
        # print('{0} independent rows'.format(len(indPpdrs)))

            # Set minCount
    #         if (param["ReqCount"] is not None):
    #             minCount = int(param.ReqCount)
    #         else:
    #             minCount = GetMinCount(indPpdrs, internalParam)
        minCount = GetMinCount(indPpdrs, internalParam)

        # Eliminate abnormal points
        cleanPpdrs = EliminateAbnormalPoints(indPpdrs, minCount, internalParam)

            # Set Priority and AlphaTolerance
    #         priority = internalParam.DefaultPriority
    #         if (param.Priority is not None):
    #             priority = int(param.Priority)
        alphaTolerance = internalParam["AlphaTolerance"][priority]
    #         if (param.AlphaTolerance is not None):
    #             alphaTolerance = float(param.AlphaTolerance)
        sdFactor = internalParam["SdFactor"][priority]

        # Determine alert range
        alertRange = GetAlertRange(
            cleanPpdrs=cleanPpdrs,
            isPositiveGood=isPositiveGood,
            minCount=minCount,
            sdFactor=sdFactor,
            minRangeLimit=internalParam["MinRangeLimit"]
        )

    #         alertSetting = AlertSetting(
    #             vertical=param.Vertical,
    #             metricName=param.MetricName,
    #             rollUpUnit=param.RollUpUnit,
    #             priority=priority,
    #             requiredCount=minCount,
    #             alertRange=alertRange,
    #             alphaTolerance=alphaTolerance
    #         )
    #         return alertSetting
        alertRange["RequiredCount"] = minCount
        alertRange["AlphaTolerance"] = alphaTolerance
    
        return alertRange

    
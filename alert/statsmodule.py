import numpy as np


def poz(z):
    """Set docstring here.

    Parameters
    ----------
    z: float

    Returns
    -------

    """
    Z_MAX = 6.0;             

    if (z == 0.0) :
        x = 0.0;
    else:
        y = 0.5 * abs(z);
        if (y >= (Z_MAX * 0.5)):
            x = 1.0;
        elif (y < 1.0):
            w = y * y;
            x = ((((((((0.000124818987 * w
                     - 0.001075204047) * w + 0.005198775019) * w
                     - 0.019198292004) * w + 0.059054035642) * w
                     - 0.151968751364) * w + 0.319152932694) * w
                     - 0.531923007300) * w + 0.797884560593) * y * 2.0;
        else:
            y -= 2.0;
            x = (((((((((((((-0.000045255659 * y
                           + 0.000152529290) * y - 0.000019538132) * y
                           - 0.000676904986) * y + 0.001390604284) * y
                           - 0.000794620820) * y - 0.002034254874) * y
                           + 0.006549791214) * y - 0.010557625006) * y
                           + 0.011630447319) * y - 0.009279453341) * y
                           + 0.005353579108) * y - 0.002141268741) * y
                           + 0.000535310849) * y + 0.999936657524;

    if (z > 0.0):
        return((x + 1.0) * 0.5) 
    else:
        return((1.0 - x) * 0.5)

def get_QVal(g_data,prio):
    """Set docstring here.

    Parameters
    ----------
    g_data: list
        data at which qvalue must be calculated
    prio: int

    Returns
    -------

    """
    # 1. Partition by ScorecardId
    sdata = {}
    for i in range (len(g_data)) :
        scorecardId = g_data[i]['ScorecardId']
        if (scorecardId not in sdata):
            sdata[scorecardId] = []
            
        sdata[scorecardId].append(g_data[i])

    # 2. Calculate Q-value for each group of ScorecardId
    outdat = []
    for scorecardId in sdata.keys():
        d2 = calcQValue(sdata[scorecardId], prio)
        for d2obj in d2:
            outdat.append(d2obj)


    return outdat


def calcQValue(data, prio):
    """Set docstring here.

    Parameters
    ----------
    data: list
    prio: int

    Returns
    -------

    """ 
    i = 0
    #dret = map(lambda a : a['__tmpidx'] = i++,data)
    for dat in data:
        dat['__tmpidx'] = i
        i=i+1
    #print(data)
    dret = data
    d2 = dret
    #    print(d2)

    #since we are always assigning p-values to max 1e-40, it will always be numeric 
    #    for dat in dret:
    #        print('here')
    #        print(dat['PValue'][prio])
    #        if(dat['PValue'][prio] is int):
    #            print('not here')
    #            d2.append(dat)


    #    d2 = dret.map(function (a) { return isNumeric(a.PValue[prio]) ? a : null }).filter(n => n)
    #    d2 = d2.sort(function (a, b) { return a.PValue[prio] - b.PValue[prio] })
    d2= sorted(d2, key = lambda i: i['PValue'][prio]) 
    minAdjPVal = 10000
    qArray = [0]*len(data)
    #len(qArray) = len(data)
    #print('len(d2)',len(d2))
    
    for i in range(len(d2)-1,-1,-1) :
        pVal = d2[i]['PValue'][prio]
        #print('pVal',pVal)
        adjPVal = len(d2)/ (i + 1) * pVal
        minAdjPVal = min(minAdjPVal, adjPVal)
        qVal = minAdjPVal
        idx = d2[i]['__tmpidx']
        #print('idx',idx)
        qArray[idx] = qVal
    
    #print('==')
    #print(qArray)
    #for (var i = 0; i < dret.length; i++) {
    for i in range(len(dret)):
        idx = dret[i]['__tmpidx']
        #print(dret[i].keys())

        #if(dret[i]['ExperimentStepId'] == 'f2ec8a94-08b3-4d3c-b0c8-1df0c579367f' and dret[i]['ScorecardId'] == 214197491):
        #    print('dret[i]',dret[i])
        #    print('qVal',qVal)
        #    print('=====here')
        #    print('idx2',idx)
        #    print('qArray[idx]',qArray[idx])
        #    print('done')
        if (qArray[idx] is not None):
            #print('idx',idx)
            if ('QValue' not in dret[i].keys() or len(dret[i]['QValue'])==0 ):
                dret[i]['QValue'] = [0]*3

            dret[i]['QValue'][prio] = qArray[idx]
        #print(dret[i])
        #del dret[i]['__tmpidx']


    #print(dret)
    return dret


def calcPValue(g_data,absRangeLower,absRangeUpper,ratioRangeLower,ratioRangeUpper,minCount,alphaTolerance,prio):
    """Set docstring here.

    Parameters
    ----------
    g_data: list
    absRangeLower: float
    absRangeUpper: float
    ratioRangeLower: float
    ratioRangeUpper: float
    minCount: int
    alphaTolerance: float
    prio: int

    Returns
    -------

    """
    nList = []
    samplePList = []
    deltaAbsList = []
    deltaRatioList = []
    pList = []
    probDisp = 400.0 / len(g_data)
    
    for dat in g_data:
        r = dat
        if(int(r['NT']) > int(r['NC'])):
            nMin = r['NC']
        else:
            nMin = r['NT']
        r['NMin'] = nMin
        deltaAbs = r['AvgT'] - r['AvgC']
        absAvgC = abs(r['AvgC'])
        deltaRatio = 0.0
        expStepId = r['ExperimentStepId']
        scorecardId = r['ScorecardId']
        nList.append(nMin)

        if (absAvgC > 0):
            deltaRatio = deltaAbs / absAvgC
        stdErr = np.sqrt(r['StdDevT'] ** 2 / r['NT'] + r['StdDevC'] ** 2 / r['NC'])
        zAbsLo = (deltaAbs - absRangeLower) / stdErr
        zAbsHi = (deltaAbs - absRangeUpper) / stdErr
        zRatioLo = (deltaAbs - ratioRangeLower * absAvgC) / stdErr
        zRatioHi = (deltaAbs - ratioRangeUpper * absAvgC) / stdErr
        if(zAbsLo < 0):
            pAbsLo = poz(zAbsLo)
        else:
            pAbsLo = 1

        if(zAbsHi > 0):
            pAbsHi = poz(-zAbsHi)
        else:
            pAbsHi = 1

        if(zRatioLo < 0):
            pRatioLo = poz(zRatioLo)
        else:
            pRatioLo = 1

        if(zRatioLo > 0):
            pRatioHi = poz(-zRatioHi)
        else:
            pRatioHi = 1
        
        pAll = min(pAbsLo, pAbsHi, pRatioLo, pRatioHi)
        pAll = max(1e-40, pAll)
        r['PValue'] = [0]*3
        r['PValue'][prio] = pAll

    return g_data

def filter_result(g_data,prio,minCount,alphaTolerance):
    """Set docstring here.

    Parameters
    ----------
    g_data: list
        the preprocessed data on which filtering is happening based on pval and qval calculations
    prio: int
        alert prioirty  
    minCount: int
        number which is ReqCountPercentile of all Nmin, where Nmin is min(NT,NC)
    alphaTolerance: float

    Returns
    -------
    samplePList :list
        returns the final result as list of data rows

    """
    samplePList = []
    # print('came here')
    for dat in g_data:
        r = dat
        nMin = r['NMin']
        deltaAbs = r['AvgT'] - r['AvgC']
        absAvgC = abs(r['AvgC'])
        deltaRatio = 0.0
        expStepId = r['ExperimentStepId']
        scorecardId = r['ScorecardId']
        pVal = r['PValue']
        expname = r['ExperimentName']
        expstepid = r['ExperimentStepId']
        FlightNameT = r['FlightNameT']
        FlightNameC = r['FlightNameC']
        AvgT = r['AvgT']
        AvgC = r['AvgC']
        NT=r['NT']
        NC=r['NC']
        if (absAvgC > 0):
            deltaRatio = deltaAbs / absAvgC

        #TODO
        if('QValue' in r.keys()):
            qValue = r['QValue'][prio]
        else:
            qValue = 0
        isAlert = (nMin > minCount) and (qValue < alphaTolerance)
        r['IsAlertHypo'] = [False, False, False]
        r['IsAlertHypo'][prio] = isAlert
        # print(type(scorecardId))
        # if(scorecardId == 216829794):
            # print('here')
            # print(qValue)
        if (isAlert):
            samplePList.append({ 
                 "ScorecardId": scorecardId,
                 "ExpStepId":expstepid,
                "Flights":'{}/{}'.format(FlightNameT,FlightNameC),
                "Avg" :'{}/{}'.format(AvgT,AvgC),
                "N":'{}/{}'.format(NT,NC),
                "DeltaAbs":deltaAbs,
                "DeltaRatio":deltaRatio,
                "PValue":pVal,
                "QValue": qValue
                })

    return samplePList

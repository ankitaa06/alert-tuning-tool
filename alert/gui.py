
import json
import autoconfig
import statsmodule
import preprocess
import numpy as np
import pandas as pd
# dummy='abc'
alertSetting = {}
ppdrList=[]
from IPython.display import clear_output

def filter_result(g_data,prio,minCount,alphaTolerance):
    """Set docstring here.

    Parameters
    ----------
    g_data: 
    prio: 
    minCount: 
    alphaTolerance: 

    Returns
    -------

    """amplePList = []
    print('came here')
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
        if (absAvgC > 0):
            deltaRatio = deltaAbs / absAvgC

    #     TODO
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
            samplePList.append({ "nMin": nMin, "qValue": qValue, "expStepId": expStepId, "scorecardId": scorecardId ,"pVal":pVal,"expstepid":expstepid })

    return samplePList

def form(widget1,Layout):
    """Set docstring here.

        Parameters
        ----------
        'StartDate': 

        Returns
        -------

        """
    lbl1=widget1.Label('Start Date')

    text1 = widget1.Text(value='2020-05-24', disabled=False)
    
    lbl2=widget1.Label('End Date')
    text2 = widget1.Text(value='2020-05-25', disabled=False)
    
    lbl3=widget1.Label('Vertical')
    text3 = widget1.Text(value='Search', disabled=False)
    
    lbl4=widget1.Label('Metric')
    text4 = widget1.Text(value='Revenue', disabled=False)

    lbl5=widget1.Label('Number of rows to query')
    text5 = widget1.Text(value='1000', disabled=False)

    lbl6=widget1.Label('Roll Up Unit')
    ruu_list = ['User (\'RAWMUID\'; \'User\'; \'by user\')', 'Session (\'SESSION_ID_RAWMUID\'; \'Session\'; \'by session\')','Query (\'Query\'; \'By query\')', 'Flight (\'Flight\'; \'Page\'; \'By page\')']
    text6 = widget1.Dropdown(options = ruu_list)
    
    left_box = widget1.VBox([lbl1, lbl2,lbl3,lbl4,lbl5,lbl6])
    right_box = widget1.VBox([text1, text2,text3,text4,text5,text6])
    final_box = widget1.HBox([left_box, right_box])

    display(final_box)

    btn = widget1.Button(description='submit')

    def get_data(a):
        global alertSetting
        global ppdrList
        from azure.kusto.data.helpers import dataframe_from_result_table
        start_date = text1.value
        end_date = text2.value
        Vertical = text3.value
        MetricName = text4.value
        nRes = text5.value
        RollupUnit =  text6.value
      
        q = make_query(start_date,end_date,Vertical,MetricName,nRes,RollupUnit)
        print('Please wait, fetching the data....')
        finalRes = execute_query(q)
        df=dataframe_from_result_table(finalRes.primary_results[0])
        finalres_json = df.to_dict('records')
        g_data = finalres_json
        print('Data fetch complete...')
        print('No of scorecards fetched: ',len(g_data) )
        # print(g_data[0])
        
        param = {
                "start_date":start_date,
                "end_date":end_date,
                "Vertical":Vertical,
                "MetricName":MetricName,
                "nRes":nRes,
                "RollupUnit":RollupUnit
            }
        internalParam = {
                "SrmThreshold": 0.0005,  # Bing uses 0.0005 MSN uses 0.0001
                "ReqCountMinLimit": 1000,  # RequiredCount: Minimum limit
                "ReqCountMaxLimit" :10000,  # RequiredCount: Maximum limit
                "ReqCountPercentile": 0.05,  # ReqCount is determined so that 1-{ReqCountPercentile} of all scorecards that are eligible for alerts
                # Equivalence range is based on StdDev * sdFactor
                "SdFactor":[float(1.0) / np.sqrt(1000), float(0.2) / np.sqrt(1000), float(0.04) / np.sqrt(1000)],
                "MinRangeLimit" : 0.001,  # Minimum allowed AlertRange limit 0 should not be allowed
                "PValNormalThreshold" : 0.001,  # P-value threshold used for eliminating abnormal points
                "DefaultPriority" : 1,  # When Priority is not specified assume it as P1
                "AlphaTolerance" : [1e-6, 1e-5, 1e-4]  # P0 P1 P2  
            }
        ppdrList = preprocess.get_preprocessed_data(g_data,param,internalParam)
        # alertSetting = autoconfig.get_auto_config(g_data,param)
        alertSetting = autoconfig.get_auto_config(param,internalParam,ppdrList)
        # print(alertSetting)
        # create_new_cell('')
        # display_auto_config(alertSetting,widget1,Layout)

    def get_data2(a):
        print('here')
        print(a.description)
        # print(b)
    btn.on_click(get_data)
    # btn.on_click(get_data2)

    display(btn)
    create_new_cell('#execute this after prompt\ngui.displayAutoConfigTables(widgets,Layout)')

def displayAutoConfigTables(widget1,Layout):
    """Set docstring here.

        Parameters
        ----------
        'P0': 

        Returns
        -------

        """
    global alertSetting
    print('P0')
    display_auto_config_prio0(alertSetting,widget1,Layout,0)
    print('P1')
    display_auto_config_prio1(alertSetting,widget1,Layout,1)
    print('P2')
    display_auto_config_prio2(alertSetting,widget1,Layout,2)
    # create_new_cell('#execute this after seeing the table above\ngui.displayLastResults()')

def create_new_cell(contents):
    """Set docstring here.

        Parameters
        ----------

        Returns
        -------

        """
    from IPython.core.getipython import get_ipython
    shell = get_ipython()

    payload = dict(
        source='set_next_input',
        text=contents,
        replace=False,
    )
    shell.payload_manager.write_payload(payload, single=False)

def display_auto_config_prio0(alertSettings_dict,widgets,Layout,prio):
    """Set docstring here.

    Parameters
    ----------
    alertSettings_dict: 
    widgets: 
    Layout: 
    prio: 

    Returns
    -------

    """
    dict1 = alertSettings_dict
    lbl0_p0 = widgets.Label('Auto',layout=Layout(width='10%',color='red'))
    bt1_p0 = widgets.Button(description='Auto0',layout=Layout(width='10%'))
    bt2_p0 = widgets.Button(description='Auto1',layout=Layout(width='10%'))
    bt3_p0 = widgets.Button(description='Auto2',layout=Layout(width='10%'))
    bt4_p0 = widgets.Button(description='Custom',layout=Layout(width='10%'))

    lbl1_p0 = widgets.Label('AbsLo',layout=Layout(width='10%'))
    text1_0_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][0]), disabled=True,layout=Layout(width='10%'))
    text1_1_p0 = widgets.Text(value=str(dict1['prio0']['auto1'][0]), disabled=True,layout=Layout(width='10%'))
    text1_2_p0 = widgets.Text(value=str(dict1['prio0']['auto2'][0]), disabled=True,layout=Layout(width='10%'))
    text1_3_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][0]), disabled=False,layout=Layout(width='10%'))

    lbl2_p0 = widgets.Label('AbsHi',layout=Layout(width='10%'))
    text2_0_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][1]), disabled=True,layout=Layout(width='10%'))
    text2_1_p0 = widgets.Text(value=str(dict1['prio0']['auto1'][1]), disabled=True,layout=Layout(width='10%'))
    text2_2_p0 = widgets.Text(value=str(dict1['prio0']['auto2'][1]), disabled=True,layout=Layout(width='10%'))
    text2_3_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][1]), disabled=False,layout=Layout(width='10%'))

    lbl3_p0 = widgets.Label('RatLo',layout=Layout(width='10%'))
    text3_0_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][2]), disabled=True,layout=Layout(width='10%'))
    text3_1_p0 = widgets.Text(value=str(dict1['prio0']['auto1'][2]), disabled=True,layout=Layout(width='10%'))
    text3_2_p0 = widgets.Text(value=str(dict1['prio0']['auto2'][2]), disabled=True,layout=Layout(width='10%'))
    text3_3_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][2]), disabled=False,layout=Layout(width='10%'))

    lbl4_p0 = widgets.Label('RatHi',layout=Layout(width='10%'))
    text4_0_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][3]), disabled=True,layout=Layout(width='10%'))
    text4_1_p0 = widgets.Text(value=str(dict1['prio0']['auto1'][3]), disabled=True,layout=Layout(width='10%'))
    text4_2_p0 = widgets.Text(value=str(dict1['prio0']['auto2'][3]), disabled=True,layout=Layout(width='10%'))
    text4_3_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][3]), disabled=False,layout=Layout(width='10%'))

    lbl5_p0 = widgets.Label('NReq',layout=Layout(width='10%'))
    text5_0_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][4]), disabled=True,layout=Layout(width='10%'))
    text5_1_p0 = widgets.Text(value=str(dict1['prio0']['auto1'][4]), disabled=True,layout=Layout(width='10%'))
    text5_2_p0 = widgets.Text(value=str(dict1['prio0']['auto2'][4]), disabled=True,layout=Layout(width='10%'))
    text5_3_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][4]), disabled=False,layout=Layout(width='10%'))

    lbl6_p0 = widgets.Label('AlphaTol',layout=Layout(width='10%'))
    text6_0_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][5]), disabled=True,layout=Layout(width='10%'))
    text6_1_p0 = widgets.Text(value=str(dict1['prio0']['auto1'][5]), disabled=True,layout=Layout(width='10%'))
    text6_2_p0 = widgets.Text(value=str(dict1['prio0']['auto2'][5]), disabled=True,layout=Layout(width='10%'))
    text6_3_p0 = widgets.Text(value=str(dict1['prio0']['auto0'][5]), disabled=False,layout=Layout(width='10%'))

    header_box_p0 = widgets.HBox([lbl0_p0,lbl1_p0, lbl2_p0,lbl3_p0,lbl4_p0,lbl5_p0,lbl6_p0],layout=Layout(width='70%'))
    auto0_box_p0 = widgets.HBox([bt1_p0,text1_0_p0, text2_0_p0,text3_0_p0,text4_0_p0,text5_0_p0,text6_0_p0],layout=Layout(width='70%'))
    auto1_box_p0 = widgets.HBox([bt2_p0,text1_1_p0, text2_1_p0,text3_1_p0,text4_1_p0,text5_1_p0,text6_1_p0],layout=Layout(width='70%'))
    auto2_box_p0 = widgets.HBox([bt3_p0,text1_2_p0, text2_2_p0,text3_2_p0,text4_2_p0,text5_2_p0,text6_2_p0],layout=Layout(width='70%'))
    custom_box_p0 = widgets.HBox([bt4_p0,text1_3_p0, text2_3_p0,text3_3_p0,text4_3_p0,text5_3_p0,text6_3_p0],layout=Layout(width='70%'))

    final_box_p0 = widgets.VBox([header_box_p0,auto0_box_p0,auto1_box_p0,auto2_box_p0,custom_box_p0])

    def callStatsModule(b):
        # print('stats called')
        neginf_const = -2147483648;
        inf_const = 2147483647; 
        if(b.description=='Custom'):
            absRangeLower = text1_3_p0.value
            absRangeUpper = text2_3_p0.value
            ratioRangeLower = text3_3_p0.value
            ratioRangeUpper = text4_3_p0.value
            minCount = text5_3_p0.value
            alphaTolerance = text6_3_p0.value
            if(absRangeLower == 'None'):
                absRangeLower = neginf_const
            if(absRangeUpper == 'None'):
                absRangeUpper = inf_const
            ratioRangeLower = float(ratioRangeLower)
            ratioRangeUpper = float(ratioRangeUpper)
            minCount =int(minCount)
            alphaTolerance = float(alphaTolerance)
            
            print('Given alert configurations for P0')
            print('Abslo = {},AbsHi = {}, RatLo = {}, RatHi = {}, minCount = {},alphaTol = {}, prio = {}'.format(absRangeLower,absRangeUpper,ratioRangeLower,ratioRangeUpper,minCount,alphaTolerance,prio))
            g_data = statsmodule.calcPValue(ppdrList,absRangeLower,absRangeUpper,ratioRangeLower,ratioRangeUpper,minCount,alphaTolerance,prio)
            g_data = statsmodule.get_QVal(ppdrList,prio)
            filteredResults = statsmodule.filter_result(ppdrList,prio,minCount,alphaTolerance)
            # print('======================================================================================')
            print('No of scorecards with possible alerts in p0=',len(filteredResults))
            for i in range(len(filteredResults)):
                print(filteredResults[i]['ScorecardId'])
                print(filteredResults[i])
            print('======================================================================================')


    bt4_p0.on_click(callStatsModule)
    
    display(final_box_p0)
    

def display_auto_config_prio1(alertSettings_dict,widgets,Layout,prio):
    """Set docstring here.

    Parameters
    ----------
    alertSettings_dict: 
    widgets: 
    Layout: 
    prio: 

    Returns
    -------

    """
    dict1 = alertSettings_dict
    lbl0_p1 = widgets.Label('Auto',layout=Layout(width='10%',color='red'))
    bt1_p1 = widgets.Button(description='Auto0',layout=Layout(width='10%'))
    bt2_p1 = widgets.Button(description='Auto1',layout=Layout(width='10%'))
    bt3_p1 = widgets.Button(description='Auto2',layout=Layout(width='10%'))
    bt4_p1 = widgets.Button(description='Custom',layout=Layout(width='10%'))

    lbl1_p1 = widgets.Label('AbsLo',layout=Layout(width='10%'))
    text1_0_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][0]), disabled=True,layout=Layout(width='10%'))
    text1_1_p1 = widgets.Text(value=str(dict1['prio1']['auto1'][0]), disabled=True,layout=Layout(width='10%'))
    text1_2_p1 = widgets.Text(value=str(dict1['prio1']['auto2'][0]), disabled=True,layout=Layout(width='10%'))
    text1_3_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][0]), disabled=False,layout=Layout(width='10%'))

    lbl2_p1 = widgets.Label('AbsHi',layout=Layout(width='10%'))
    text2_0_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][1]), disabled=True,layout=Layout(width='10%'))
    text2_1_p1 = widgets.Text(value=str(dict1['prio1']['auto1'][1]), disabled=True,layout=Layout(width='10%'))
    text2_2_p1 = widgets.Text(value=str(dict1['prio1']['auto2'][1]), disabled=True,layout=Layout(width='10%'))
    text2_3_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][1]), disabled=False,layout=Layout(width='10%'))

    lbl3_p1 = widgets.Label('RatLo',layout=Layout(width='10%'))
    text3_0_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][2]), disabled=True,layout=Layout(width='10%'))
    text3_1_p1 = widgets.Text(value=str(dict1['prio1']['auto1'][2]), disabled=True,layout=Layout(width='10%'))
    text3_2_p1 = widgets.Text(value=str(dict1['prio1']['auto2'][2]), disabled=True,layout=Layout(width='10%'))
    text3_3_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][2]), disabled=False,layout=Layout(width='10%'))

    lbl4_p1 = widgets.Label('RatHi',layout=Layout(width='10%'))
    text4_0_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][3]), disabled=True,layout=Layout(width='10%'))
    text4_1_p1 = widgets.Text(value=str(dict1['prio1']['auto1'][3]), disabled=True,layout=Layout(width='10%'))
    text4_2_p1 = widgets.Text(value=str(dict1['prio1']['auto2'][3]), disabled=True,layout=Layout(width='10%'))
    text4_3_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][3]), disabled=False,layout=Layout(width='10%'))

    lbl5_p1 = widgets.Label('NReq',layout=Layout(width='10%'))
    text5_0_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][4]), disabled=True,layout=Layout(width='10%'))
    text5_1_p1 = widgets.Text(value=str(dict1['prio1']['auto1'][4]), disabled=True,layout=Layout(width='10%'))
    text5_2_p1 = widgets.Text(value=str(dict1['prio1']['auto2'][4]), disabled=True,layout=Layout(width='10%'))
    text5_3_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][4]), disabled=False,layout=Layout(width='10%'))

    lbl6_p1 = widgets.Label('AlphaTol',layout=Layout(width='10%'))
    text6_0_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][5]), disabled=True,layout=Layout(width='10%'))
    text6_1_p1 = widgets.Text(value=str(dict1['prio1']['auto1'][5]), disabled=True,layout=Layout(width='10%'))
    text6_2_p1 = widgets.Text(value=str(dict1['prio1']['auto2'][5]), disabled=True,layout=Layout(width='10%'))
    text6_3_p1 = widgets.Text(value=str(dict1['prio1']['auto0'][5]), disabled=False,layout=Layout(width='10%'))

    header_box_p1 = widgets.HBox([lbl0_p1,lbl1_p1, lbl2_p1,lbl3_p1,lbl4_p1,lbl5_p1,lbl6_p1],layout=Layout(width='70%'))
    auto0_box_p1 = widgets.HBox([bt1_p1,text1_0_p1, text2_0_p1,text3_0_p1,text4_0_p1,text5_0_p1,text6_0_p1],layout=Layout(width='70%'))
    auto1_box_p1 = widgets.HBox([bt2_p1,text1_1_p1, text2_1_p1,text3_1_p1,text4_1_p1,text5_1_p1,text6_1_p1],layout=Layout(width='70%'))
    auto2_box_p1 = widgets.HBox([bt3_p1,text1_2_p1, text2_2_p1,text3_2_p1,text4_2_p1,text5_2_p1,text6_2_p1],layout=Layout(width='70%'))
    custom_box_p1 = widgets.HBox([bt4_p1,text1_3_p1, text2_3_p1,text3_3_p1,text4_3_p1,text5_3_p1,text6_3_p1],layout=Layout(width='70%'))

    final_box_p1 = widgets.VBox([header_box_p1,auto0_box_p1,auto1_box_p1,auto2_box_p1,custom_box_p1])

    def callStatsModule(b):
        # create_new_cell('created from prio1')
        # create_code_cell('print("Hello world!")')
        # make_cell('here')
        # print('stats called')
        neginf_const = -2147483648;
        inf_const = 2147483647; 
        if(b.description=='Custom'):
            absRangeLower = text1_3_p1.value
            absRangeUpper = text2_3_p1.value
            ratioRangeLower = text3_3_p1.value
            ratioRangeUpper = text4_3_p1.value
            minCount = text5_3_p1.value
            alphaTolerance = text6_3_p1.value
            if(absRangeLower == 'None'):
                absRangeLower = neginf_const
            if(absRangeUpper == 'None'):
                absRangeUpper = inf_const
            ratioRangeLower = float(ratioRangeLower)
            ratioRangeUpper = float(ratioRangeUpper)
            minCount =int(minCount)
            alphaTolerance = float(alphaTolerance)
            
            print('Given alert configurations for P1')
            print('Abslo = {},AbsHi = {}, RatLo = {}, RatHi = {}, minCount = {},alphaTol = {}, prio = {}'.format(absRangeLower,absRangeUpper,ratioRangeLower,ratioRangeUpper,minCount,alphaTolerance,prio))
            g_data = statsmodule.calcPValue(ppdrList,absRangeLower,absRangeUpper,ratioRangeLower,ratioRangeUpper,minCount,alphaTolerance,prio)
            g_data = statsmodule.get_QVal(ppdrList,prio)
            filteredResults = statsmodule.filter_result(ppdrList,prio,minCount,alphaTolerance)
            # print('======================================================================================')
            print('No of scorecards with possible alerts in p1 = ',len(filteredResults))
            # df = pd.DataFrame(filteredResults)
            # create_code_cell(df.to_string())
            
            for i in range(len(filteredResults)):
                print(filteredResults[i]['ScorecardId'])
                print(filteredResults[i])
            print('======================================================================================')




    bt4_p1.on_click(callStatsModule)
    
    display(final_box_p1)
    # display(bt4_p1)
    
def display_auto_config_prio2(alertSettings_dict,widgets,Layout,prio):
    """Set docstring here.

    Parameters
    ----------
    alertSettings_dict: 
    widgets: 
    Layout: 
    prio: 

    Returns
    -------

    """
    global ppdrList
    dict1 = alertSettings_dict
    lbl0_p2 = widgets.Label('Auto',layout=Layout(width='10%',color='red'))
    bt1_p2 = widgets.Button(description='Auto0',layout=Layout(width='10%'))
    bt2_p2 = widgets.Button(description='Auto1',layout=Layout(width='10%'))
    bt3_p2 = widgets.Button(description='Auto2',layout=Layout(width='10%'))
    bt4_p2 = widgets.Button(description='Custom',layout=Layout(width='10%'))

    lbl1_p2 = widgets.Label('AbsLo',layout=Layout(width='10%'))
    text1_0_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][0]), disabled=True,layout=Layout(width='10%'))
    text1_1_p2 = widgets.Text(value=str(dict1['prio2']['auto1'][0]), disabled=True,layout=Layout(width='10%'))
    text1_2_p2 = widgets.Text(value=str(dict1['prio2']['auto2'][0]), disabled=True,layout=Layout(width='10%'))
    text1_3_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][0]), disabled=False,layout=Layout(width='10%'))

    lbl2_p2 = widgets.Label('AbsHi',layout=Layout(width='10%'))
    text2_0_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][1]), disabled=True,layout=Layout(width='10%'))
    text2_1_p2 = widgets.Text(value=str(dict1['prio2']['auto1'][1]), disabled=True,layout=Layout(width='10%'))
    text2_2_p2 = widgets.Text(value=str(dict1['prio2']['auto2'][1]), disabled=True,layout=Layout(width='10%'))
    text2_3_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][1]), disabled=False,layout=Layout(width='10%'))

    lbl3_p2 = widgets.Label('RatLo',layout=Layout(width='10%'))
    text3_0_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][2]), disabled=True,layout=Layout(width='10%'))
    text3_1_p2 = widgets.Text(value=str(dict1['prio2']['auto1'][2]), disabled=True,layout=Layout(width='10%'))
    text3_2_p2 = widgets.Text(value=str(dict1['prio2']['auto2'][2]), disabled=True,layout=Layout(width='10%'))
    text3_3_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][2]), disabled=False,layout=Layout(width='10%'))

    lbl4_p2 = widgets.Label('RatHi',layout=Layout(width='10%'))
    text4_0_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][3]), disabled=True,layout=Layout(width='10%'))
    text4_1_p2 = widgets.Text(value=str(dict1['prio2']['auto1'][3]), disabled=True,layout=Layout(width='10%'))
    text4_2_p2 = widgets.Text(value=str(dict1['prio2']['auto2'][3]), disabled=True,layout=Layout(width='10%'))
    text4_3_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][3]), disabled=False,layout=Layout(width='10%'))

    lbl5_p2 = widgets.Label('NReq',layout=Layout(width='10%'))
    text5_0_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][4]), disabled=True,layout=Layout(width='10%'))
    text5_1_p2 = widgets.Text(value=str(dict1['prio2']['auto1'][4]), disabled=True,layout=Layout(width='10%'))
    text5_2_p2 = widgets.Text(value=str(dict1['prio2']['auto2'][4]), disabled=True,layout=Layout(width='10%'))
    text5_3_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][4]), disabled=False,layout=Layout(width='10%'))

    lbl6_p2 = widgets.Label('AlphaTol',layout=Layout(width='10%'))
    text6_0_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][5]), disabled=True,layout=Layout(width='10%'))
    text6_1_p2 = widgets.Text(value=str(dict1['prio2']['auto1'][5]), disabled=True,layout=Layout(width='10%'))
    text6_2_p2 = widgets.Text(value=str(dict1['prio2']['auto2'][5]), disabled=True,layout=Layout(width='10%'))
    text6_3_p2 = widgets.Text(value=str(dict1['prio2']['auto0'][5]), disabled=False,layout=Layout(width='10%'))

    header_box_p2 = widgets.HBox([lbl0_p2,lbl1_p2, lbl2_p2,lbl3_p2,lbl4_p2,lbl5_p2,lbl6_p2],layout=Layout(width='70%'))
    auto0_box_p2 = widgets.HBox([bt1_p2,text1_0_p2, text2_0_p2,text3_0_p2,text4_0_p2,text5_0_p2,text6_0_p2],layout=Layout(width='70%'))
    auto1_box_p2 = widgets.HBox([bt2_p2,text1_1_p2, text2_1_p2,text3_1_p2,text4_1_p2,text5_1_p2,text6_1_p2],layout=Layout(width='70%'))
    auto2_box_p2 = widgets.HBox([bt3_p2,text1_2_p2, text2_2_p2,text3_2_p2,text4_2_p2,text5_2_p2,text6_2_p2],layout=Layout(width='70%'))
    custom_box_p2 = widgets.HBox([bt4_p2,text1_3_p2, text2_3_p2,text3_3_p2,text4_3_p2,text5_3_p2,text6_3_p2],layout=Layout(width='70%'))

    final_box_p2 = widgets.VBox([header_box_p2,auto0_box_p2,auto1_box_p2,auto2_box_p2,custom_box_p2])

    def callStatsModule(b):
        
        # print('stats called')
        neginf_const = -2147483648;
        inf_const = 2147483647; 
        if(b.description=='Custom'):
            absRangeLower = text1_3_p2.value
            absRangeUpper = text2_3_p2.value
            ratioRangeLower = text3_3_p2.value
            ratioRangeUpper = text4_3_p2.value
            minCount = text5_3_p2.value
            alphaTolerance = text6_3_p2.value
            if(absRangeLower == 'None'):
                absRangeLower = neginf_const
            if(absRangeUpper == 'None'):
                absRangeUpper = inf_const
            ratioRangeLower = float(ratioRangeLower)
            ratioRangeUpper = float(ratioRangeUpper)
            minCount =int(minCount)
            alphaTolerance = float(alphaTolerance)
            
            print('Given alert configurations for P2')
            print('Abslo = {},AbsHi = {}, RatLo = {}, RatHi = {}, minCount = {},alphaTol = {}, prio = {}'.format(absRangeLower,absRangeUpper,ratioRangeLower,ratioRangeUpper,minCount,alphaTolerance,prio))
            g_data = statsmodule.calcPValue(ppdrList,absRangeLower,absRangeUpper,ratioRangeLower,ratioRangeUpper,minCount,alphaTolerance,prio)
            g_data = statsmodule.get_QVal(ppdrList,prio)
            filteredResults = statsmodule.filter_result(ppdrList,prio,minCount,alphaTolerance)
            # print('======================================================================================')
            print('No of scorecards with possible alerts in p2=',len(filteredResults))
            for i in range(len(filteredResults)):
                print(filteredResults[i]['ScorecardId'])
                print(filteredResults[i])
            print('======================================================================================')


    bt4_p2.on_click(callStatsModule)
    
    display(final_box_p2)
    




def make_query(start_date,end_date,vertical,metric,nRes,rollupUnit):
    """Set docstring here.

    Parameters
    ----------
    start_date: 
    end_date: 
    vertical: 
    metric: 
    nRes: 
    rollupUnit: 

    Returns
    -------

    """
    with open('customquery.txt') as f:
        query = f.readlines()

    newquery = []
    for i in query:
        if '?' in i:
            if 'Picked' in i:
                i = i.replace('?',rollupUnit)
            if 'datetime' in i:
                i = i.replace('?',start_date,1)
                i = i.replace('?',end_date,1)
            elif 'Metric' in i:
                i = i.replace('?',metric)
            elif 'Vertical' in i:
                i = i.replace('?',vertical)
            elif 'take' in i:
                i = i.replace('?',nRes)
        newquery.append(i)

    q = ''.join(newquery)
    return q



def execute_query(q):
    """Set docstring here.

    Parameters
    ----------
    q: 

    Returns
    -------

    """
    from azure.kusto.data.request import KustoClient, KustoConnectionStringBuilder
    from azure.kusto.data.exceptions import KustoServiceError
    cluster = "https://ane.kusto.windows.net"
    kcsb = KustoConnectionStringBuilder.with_aad_device_authentication(cluster)
    client = KustoClient(kcsb)
    db = "ExpData"

    try:
        response = client.execute_query(db, q)
    except KustoServiceError as error:
        print("2. Error:", error)
        print("2. Is semantic error:", error.is_semantic_error())
        print("2. Has partial results:", error.has_partial_results())
        print("2. Result size:", len(error.get_partial_results()))
    else:
        return response

#from IPython.display import display_javascript

#import base64
#from IPython.display import Javascript, display
# from IPython.utils.py3compat import str_to_bytes, bytes_to_str
#def create_code_cell(code='', where='below'):
#    """Create a code cell in the IPython Notebook.

#    Parameters
#    code: unicode
#        Code to fill the new code cell with.
#    where: unicode
#        Where to add the new code cell.
#        Possible values include:
#            at_bottom
#            above
#            below"""
#    encoded_code = (base64.b64encode(str.encode(code))).decode()
#    display(Javascript("""
#        var code1 = IPython.notebook.insert_cell_{0}('code');
#        code1.set_text(atob("{1}"));
#        var t_index = IPython.notebook.get_cells().indexOf(code1);
#        IPython.notebook.to_markdown(t_index);
#    """.format(where, encoded_code)))
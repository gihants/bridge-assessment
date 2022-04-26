import pandas as pd
import numpy as np
from scipy.interpolate import interp1d
import folium
from folium import plugins
import yaml
from typing import Dict
import geopandas
from shapely.geometry import Point, LineString

def open_route_file(routefile: str) -> Dict:
    with open(routefile, "r") as route_stream:
        try:
            route_dict = yaml.safe_load(route_stream)
            return route_dict
        except yaml.YAMLError as exc:
            print(exc)

# {'Axle number': [1, 2, 3, 4], 'Load': ['2.5', '4.4', '4.9', '923.4'], 'Axle Spacing': [0, '64', '3', '35']}
# bridge_data_path = "inputs/bridge_data.csv"
# coordinate_path = "inputs/coordinate.txt"
# route_path = "inputs/route.yaml"

def ProduceMap(original_dict, bridge_data_path, coordinate_path, route_path):

    original_df = pd.DataFrame(original_dict)
    original_df['Load'] = pd.to_numeric(original_df['Load'])
    original_df['Axle spacing'] = pd.to_numeric(original_df['Axle spacing'])

    df = original_df.copy()

    #####################################
    ### EDDIE'S ALGORITHM BEGINS HERE ###
    #####################################

    ########## TRUCK ALGORITHM ##########

    axleSpacingOriginalpd = -1*df["Axle spacing"].cumsum()
    axleSpacingOriginalpd = axleSpacingOriginalpd.fillna(0)

    # converting df to a list
    axleSpacingOriginal = axleSpacingOriginalpd.values.tolist()
    
    # calculating total truck length by summing the original axle spacing
    TruckLength = (df["Axle spacing"]).sum()

    # calculating axle load under gravity and storing in a list
    axleLoadpd = 9.8*df["Load"]
    axleLoad = axleLoadpd.values.tolist()

    #DLA for range 5m to 60m
    DynamicFactor = [1.3,1.3,1.3,1.3,1.3,1.3,1.3,1.3,1.3,
    1.296296296,1.290909091,1.285714286,1.280701754,1.275862069,1.271186441,1.266666667,
    1.262295082,1.258064516,1.253968254,1.25,1.246153846,1.242424242,1.23880597,1.235294118,
    1.231884058,1.228571429,1.225352113,1.222222222,1.219178082,1.216216216,1.213333333,1.210526316,
    1.207792208,1.205128205,1.202531646,1.2,1.197530864,1.195121951,1.192771084,1.19047619,1.188235294,
    1.186046512,1.183908046,1.181818182,1.179775281,1.177777778,1.175824176,1.173913043,1.172043011,
    1.170212766,1.168421053,1.166666667,1.164948454,1.163265306,1.161616162,1.16]

    Result_Moment = []


    for SpanLength in range(5, 61, 1):

        MovementDist = SpanLength / 2 + TruckLength #travel distance by vehicle to cross a span

        maxMoment = 0
        
        for FirstWheelPosition in np.arange(SpanLength / 2, MovementDist, 0.1):
            axleSpacing = np.array(axleSpacingOriginal) + FirstWheelPosition

            maxMomentAtPos = 0
            for x in np.arange( SpanLength /2 - 2, SpanLength / 2 + 2, 0.1):

                MatX = 0
                tempA = 0
                tempB = 0
                tempMom = 0
                
                for a, l in zip(axleSpacing, axleLoad):

                    b = SpanLength - a

                    if a < 0 or a > SpanLength:
                        pass

                    else:
                        if x <= a:
                            tempA = l * b / SpanLength
                            tempMom = tempA * x

                        else:
                            tempB = l * a / SpanLength
                            tempMom = tempB * (SpanLength - x)

                        MatX += tempMom

                    if abs(maxMomentAtPos) < abs(MatX):
                        maxMomentAtPos = MatX

                    if abs(maxMoment) < abs(maxMomentAtPos):
                        maxMoment = maxMomentAtPos
        
        Result_Moment.append(maxMoment)

    Result_Shear = []
    Result_Reaction = []
    Span = []

    axleNumber = len(axleLoad)

    for SpanLength in np.arange(5, 60.1, 1):
        MovementDist = SpanLength + TruckLength

        maxShear = 0
        maxReaction = 0
        for FirstWheelPosition in np.arange(0, MovementDist, 0.1):

            axleSpacing = np.array(axleSpacingOriginal) + FirstWheelPosition

            tempA = 0
            tempB = 0
            tempRA = 0
            tempRB = 0

            for TempIndex in np.arange(0, axleNumber):
                a = axleSpacingOriginal[TempIndex] + FirstWheelPosition
                AxleLoad = axleLoad[TempIndex]

                b = SpanLength - a

                if a < 0:
                    if a <= SpanLength * -1:
                        pass
                    else:
                        tempRA += (AxleLoad * (SpanLength + a) / SpanLength)

                elif a >= 0:
                    if b >= 0:
                        tempA += (AxleLoad * b) / SpanLength
                        tempB += (AxleLoad * a) / SpanLength

                    elif b < 0:
                        if b <= SpanLength * -1:
                            pass
                        else:
                            tempRB += (AxleLoad * (SpanLength + b) / SpanLength)

            tempRA += tempA
            tempRB += tempB

            #print(a,b,l,tempRA, tempRB)

            if tempA > tempB:
                maxShearAtPos = tempA
            else:
                maxShearAtPos = tempB

            if tempRA > tempRB:
                maxReactionAtPos = tempRA
            else:
                maxReactionAtPos = tempRB

            if abs(maxShear) < abs(maxShearAtPos):
                maxShear = maxShearAtPos
            if abs(maxReaction) < abs(maxReactionAtPos):
                maxReaction = maxReactionAtPos
        
        Result_Shear.append(maxShear)
        Result_Reaction.append(maxReaction)
        Span.append(SpanLength)

    d = {'Span':Span, 'Max Bending Moment':Result_Moment, 'Max Shear Force':Result_Shear, 'Max Reaction':Result_Reaction, 'DLA':DynamicFactor}
    result = pd.DataFrame(d)

    result['DLA Max Bending Moment'] = (result['Max Bending Moment'] * result['DLA'])
    result['DLA Max Shear Force'] = (result['Max Shear Force'] * result['DLA'])
    result['DLA Max Reaction'] = (result['Max Reaction'] * result['DLA'])

    resultcsv = result.filter(items=['Span', 'DLA Max Bending Moment','DLA Max Shear Force', 'DLA Max Reaction'])

    ###### BRIDGE ALGORITHM ######

    # importing bridge data

    df_bridge = pd.read_csv(bridge_data_path)

    data = df_bridge.sort_values(by=['BRG NO'])
    vf = resultcsv
    
    x = vf["Span"].values.tolist()
    y1 = vf["DLA Max Bending Moment"].values.tolist()
    y2 = vf["DLA Max Shear Force"].values.tolist()
    #y3 = vf["DLA Max Reaction"].values.tolist()

    interp_func1 = interp1d(x, y1, fill_value="extrapolate")
    interp_func2 = interp1d(x, y2, fill_value="extrapolate")
    #interp_func3 = interp1d(x, y3, fill_value="extrapolate")
    data["Max Bending Moment"] = df_bridge.apply(lambda x:  interp_func1(x["Span Length"]), axis=1)
    data["Max Shear Force"] = df_bridge.apply(lambda x:  interp_func2(x["Span Length"]), axis=1)
    #data["Max Reaction"] = df_bridge.apply(lambda x:  interp_func3(x["Span Length"]), axis=1)

    Select_columns = data[["BRG NO","Span Grp", "LL:DL Ratio", "DESIGNBM","DESIGNShear","Final BM","Final Shear","Max Bending Moment","Max Shear Force","Allowance (DesignLoad)"]]
    new_data = Select_columns.copy()

    new_data.loc[((new_data['Max Bending Moment']-new_data['DESIGNBM'])/new_data['DESIGNBM']) > (new_data['Allowance (DesignLoad)'] * new_data['LL:DL Ratio']), 'Pass Design Load BM'] = 'Fail'
    new_data.loc[new_data['Pass Design Load BM'].isnull(), 'Pass Design Load BM'] = "Pass"

    new_data.loc[((new_data['Max Shear Force']-new_data['DESIGNShear'])/new_data['DESIGNShear']) > (new_data['Allowance (DesignLoad)'] * new_data['LL:DL Ratio']), 'Pass Design Load VF'] = 'Fail'
    new_data.loc[new_data['Pass Design Load VF'].isnull(), 'Pass Design Load VF'] = "Pass"

    new_data.loc[(new_data['Pass Design Load BM'] =='Fail')| (new_data['Pass Design Load VF'] =='Fail'), 'Pass Design Load'] = 'FAIL'
    new_data.loc[new_data['Pass Design Load'].isnull(), 'Pass Design Load'] = "PASS"

    Allowance_LLF = 2/1.8 - 1

    new_data.loc[((new_data['Max Bending Moment']-new_data['Final BM'])/new_data['Final BM']) > Allowance_LLF, 'Pass Final Rating BM'] = 'Fail'
    new_data.loc[new_data['Pass Final Rating BM'].isnull(), 'Pass Final Rating BM'] = "Pass"

    new_data.loc[((new_data['Max Shear Force']-new_data['Final Shear'])/new_data['Final Shear']) > Allowance_LLF, 'Pass Final Rating VF'] = 'Fail'
    new_data.loc[new_data['Pass Final Rating VF'].isnull(), 'Pass Final Rating VF'] = "Pass"

    new_data.loc[(new_data['Pass Final Rating BM'] =='Fail')| (new_data['Pass Final Rating VF'] =='Fail'), 'Pass Final Load'] = 'FAIL'
    new_data.loc[new_data['Pass Final Load'].isnull(), 'Pass Final Load'] = "PASS"

    Data_Filter = new_data.loc[(new_data['Pass Design Load'] == 'FAIL')&(new_data['Pass Final Load'] == 'FAIL')]

    b = Data_Filter.filter(items=['BRG NO'])
    list_restricted_br = b.drop_duplicates(subset=['BRG NO'])
    


    df2 = pd.read_csv(coordinate_path)

    Select_columns2 = df2[["BRG NO","BRIDGE_NAM","DESCRIPT_1","DESCRIPTIO","DESCRIPT_2","Lat","Long"]]
    new_data2 = Select_columns2.copy()
    new_data2 = new_data2.sort_values(by=['BRG NO'])
    inner_join = pd.merge(list_restricted_br, new_data2, on ='BRG NO', how ='inner')

    BridgeDescription = inner_join.copy()

    BridgeDescription["DESCRIPT_1"] = BridgeDescription["DESCRIPT_1"].str.cat(BridgeDescription["DESCRIPTIO"],sep=" ,")
    BridgeDescription["DESCRIPT_1"] = BridgeDescription["DESCRIPT_1"].str.cat(BridgeDescription["DESCRIPT_2"],sep=" ,")
    BridgeDescription = BridgeDescription[["BRG NO","BRIDGE_NAM","DESCRIPT_1"]]

    ##### PRODUCING THE MAP #####
    
    m = folium.Map(location=[-33.854710,151.209140], tiles="OpenStreetMap", zoom_start=6)

    for i in range(0,len(inner_join)):
        iframe = folium.IFrame('Bridge Number#: ' + str(inner_join.iloc[i]['BRG NO']) + '<br>' + 'DESCRIPTION 1: ' + inner_join.iloc[i]['DESCRIPT_1'] + '<br>' + 'DESCRIPTION 2: ' + inner_join.iloc[i]['DESCRIPTIO'] + '<br>' + 'DESCRIPTION 3: ' + inner_join.iloc[i]['DESCRIPT_2'])
        popup = folium.Popup(iframe, min_width=350, max_width=300)
        folium.CircleMarker(
            location=[inner_join.iloc[i]['Lat'], inner_join.iloc[i]['Long']],
            radius = '7',
            color= 'black',
            fill_color = 'red',
            fill_opacity=1,
            tooltip = inner_join.iloc[i]['BRG NO'],
            popup= popup,
    ).add_to(m)

    #request route in yaml file downloaded from NHVR Portal
    route_dict = open_route_file(route_path)

    New_List = []
    TopSegment = route_dict['routes'][0]['RM_SEGMENTS']

    i = 0
    for item in TopSegment:
        
        Segment = route_dict['routes'][0]['RM_SEGMENTS'][i]
        
        j = 0
        Geometry = Segment['NA ANALYSIS'][0]['GEOMETRY']
        
        for index, coordinate in enumerate(Geometry):

            New_List.extend(coordinate)
            j += 1
        i += 1

    df3 = pd.DataFrame(New_List)
    Path_Lat = df3[1].values.tolist()
    Path_Long = df3[0].values.tolist()
    df4 = pd.DataFrame(Path_Lat)
    df4['Lon'] = Path_Long
    df4list = df4.values.tolist()

    folium.plugins.AntPath([df4list]).add_to(m)

    gdf = geopandas.GeoDataFrame(inner_join, geometry=geopandas.points_from_xy(inner_join.Long, inner_join.Lat))
    route_lyr = LineString(New_List)
    Bufroute = route_lyr.buffer(0.01)
    Newdata3 = gdf['geometry'].within(Bufroute)
    pipdata = gdf.loc[Newdata3]
    ReportTable = BridgeDescription.loc[Newdata3]
    ReportTable = ReportTable.rename(columns={'BRG NO':'BRIDGE NUMBER','BRIDGE_NAM':'BRIDGE NAME' ,'DESCRIPT_1': 'BRIDGE DESCRIPTION'})

    for i in range(0,len(pipdata)):
        iframe = folium.IFrame('Bridge Number#: ' + str(inner_join.iloc[i]['BRG NO']) + '<br>' + 'DESCRIPTION 1: ' + inner_join.iloc[i]['DESCRIPT_1'] + '<br>' + 'DESCRIPTION 2: ' + inner_join.iloc[i]['DESCRIPTIO'] + '<br>' + 'DESCRIPTION 3: ' + inner_join.iloc[i]['DESCRIPT_2'])
        popup = folium.Popup(iframe, min_width=350, max_width=300)
        folium.CircleMarker(
            location=[pipdata.iloc[i]['Lat'], pipdata.iloc[i]['Long']],
            radius = '7',
            color= 'black',
            fill_color = 'red',
            fill_opacity=1,
            tooltip = pipdata.iloc[i]['BRG NO'],
            popup= popup,
    ).add_to(m)
    folium.plugins.AntPath([df4list]).add_to(m)

    m.save('static/map.html')
        
    return m._repr_html_()
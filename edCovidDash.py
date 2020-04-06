import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
from uncertainties import ufloat
import copy

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

mortalityDF = pd.read_csv('mortalityByAge.csv')
mortalityDF.index = mortalityDF.ageCat
mortalityDF = mortalityDF.drop(labels=mortalityDF.columns[0], axis='columns')

icuCoeffs = pd.read_csv('icuAdmitCoeffs-4-6-20.csv', index_col=0)

# currently unused...saving because we might bring it back...
baselineChartData = [{'x': mortalityDF.ageMedian, 'y': mortalityDF.caseFatality, 'type': 'scatter',
                      'name': 'Median Mortality for Age', 'mode': 'markers', 'marker': {'size': '10'}}]
baselineChartLayout = {'title': 'Age-Mortality Relationship', 'xaxis': {'title': 'Age',
                                                                        'range': [30, 90]}, 'yaxis': {'title': 'Mortality', 'range': [-0.10, 1.0]}}

app.layout = html.Div(children=[
    html.H1(children='ED Covid Risk Predictor'),

    html.Div(children=[
        html.Div(children=[
            html.H4('Demographics'),
            html.Div(children=[html.Label('Age'), dcc.Input(
                type='number', value=65, id='ageInput')], id="agePanel"),
            html.Div(children=[dcc.Checklist(options=[{'label': 'Female', 'value': 1}], value=[1], id="femaleInput")], id='femalePanel'),
            html.Br(), html.H4('Lab Values'),
            html.Div(children=[html.Label('D-Dimer'), dcc.Input(type='number', value=12.5, id='dDimerInput')], id="dDimerPanel"),
            html.Div(children=[html.Label('Ferritin'), dcc.Input(type='number', value=250, id='ferritinInput')], id="ferritinPanel"),
            html.Div(children=[html.Label('CRP'), dcc.Input(type='number', value=4, id='crpInput')], id="crpPanel"),
            html.Div(children=[html.Label('High Sensitivity Troponin'), dcc.Input(type='number', value=13, id='hsTropInput')], id="hsTropPanel"),
            html.Div(children=[html.Label('Lymphocyte Count'), dcc.Input(type='number', value=18, id='lymphInput')], id="lympthPanel"),
            html.Br(), html.H4('SOFA Elements'),
            html.Div(children=[html.Label('PA O2'), dcc.Input(type='number', value=100, id='paO2Input')], id="paO2Panel"),
            html.Div(children=[html.Label('Fi O2'), dcc.Slider(id='fiO2Input', min=0.21, max=1.0, step=0.501, value=0.21, 
                                                               tooltip={'always_visible': True, 'placement': 'right'})]),
            html.Div(children=[html.Label('Platelets'), dcc.Input(type='number', value=225, id='plateletInput')], id="plateletPanel"),
            html.Div(children=[html.Label('Glasgow Coma Scale'), dcc.Slider(id='gcsInput', min=0, max=15, step=1, value=15, 
                                                               tooltip={'always_visible': True, 'placement': 'right'})], id="gcsPanel"),
            html.Div(children=[html.Label('Bilirubin'), dcc.Input(type='number', value=0.9, id='biliInput')], id="biliPanel"),
            html.Div(children=[html.Label('Creatinine'), dcc.Input(type='number', value=1.2, id='creatinineInput')], id="creatininePanel"),
            html.Div(style={'font-size': '12px', }, children=[html.Label('Mean Arterial Pressure (MAP)'), 
                dcc.Dropdown(id='mapInput',
                    options=[
                        {'label': 'No Hypotension', 'value': '0'},
                        {'label': 'MAP < 70 mm Hg', 'value': '1'},
                        {'label': 'Dopamine <= 5 or Dobutamine (any dose)', 'value': '2'},
                        {'label': 'Dopamine > 5, Epinephrine <= 0.1 or Norepinephrine <= 0.1', 'value': '3'},
                        {'label': 'Dopamine > 15 Epinephrine > 0.1 or Norepinephrine >  0.1', 'value': '4'}
                    ],
                value='0')], id="mapPanel"),
        ], className='column', id="inputPanel", style={'width': '25%'}),
        html.Div(children=[html.H4('ICU Probability'), html.H3(id='icuProb'), html.H3(
            id='icuCI')], className='column', id="outcomeRisk", style={'width': '25%'}),
    ], className='row', id='inputOutputContainer'),
], id="outermost")


@app.callback(
    [Output(component_id='icuProb', component_property='children'),
     Output(component_id='icuCI', component_property='children')],
    [Input(component_id='ageInput', component_property='value'),
     Input(component_id='dDimerInput', component_property='value'),
     Input(component_id='ferritinInput', component_property='value'),
     Input(component_id='crpInput', component_property='value'),
     Input(component_id='hsTropInput', component_property='value'),
     Input(component_id='lymphInput', component_property='value'),
     Input(component_id='paO2Input', component_property='value'),
     Input(component_id='fiO2Input', component_property='value'),
     Input(component_id='plateletInput', component_property='value'),
     Input(component_id='gcsInput', component_property='value'),
     Input(component_id='biliInput', component_property='value'),
     Input(component_id='creatinineInput', component_property='value'),
     Input(component_id='mapInput', component_property='value'),
     Input(component_id='femaleInput', component_property='value')]
)
def update_risks(age, dDimer, ferritin, crp, hsTrop, lymph, paO2, fiO2, platelets, gcs, bili, creatinine, meanArtPressure, female):
    xb = getCoeff('alpha')
    xb += getCoeff('betaAge') * age
    xb += getCoeff('betaDDimer') * dDimer
    xb += getCoeff('betaFerritin') * ferritin
    xb+= getCoeff('betaCRP') * crp
    xb += getCoeff('betaLymph') * lymph
    xb += getCoeff('betaFemale') * len(female)
    xb += getCoeff('betaSofa') * calcSofa(paO2, fiO2, platelets, gcs, bili, creatinine, meanArtPressure)

    icuProb = np.e**xb/(1+np.e**xb)

    icuString = f"{icuProb.nominal_value*100:.0f}%"
    ciString = f"95% CI [{(icuProb.nominal_value-icuProb.std_dev*1.96)*100:.0f}% - {(icuProb.nominal_value+icuProb.std_dev*1.96)*100:.0f}%]"

    return icuString, ciString

def getCoeff(coeffName):
    return ufloat(icuCoeffs.loc[coeffName]['mean'], icuCoeffs.loc[coeffName]['sd'])

def calcSofa(paO2, fiO2, platelets, gcs, bili, creatinine, meanArtPressure):
    o2Product = paO2 / fiO2
    sofa = 4 - pd.cut([o2Product], bins=[0, 100, 200, 300, 400, 1000]).codes[0]
    sofa += 4- pd.cut([platelets], bins=[0, 20, 50, 100, 150, 1000]).codes[0]
    sofa += 4 - pd.cut([gcs], bins=[0, 6, 9, 12, 14, 15]).codes[0]
    sofa +=  pd.cut([bili], bins=[0, 1.2, 1.9, 5.9, 11.0, 1000]).codes[0]
    sofa +=  pd.cut([creatinine], bins=[0, 1.2, 1.9, 3.4, 4.9, 1000]).codes[0]
    sofa +=  int(meanArtPressure)
    return sofa

# currently unused...
def getCrudeMortalityEstimate(age, dDimer, ferritin):
    cat = pd.cut(x=[age], bins=[0, 9, 19, 29, 39, 49, 59, 69, 79, 120])
    ageMean = mortalityDF.iloc[cat.codes[0], 0]
    ageSE = mortalityDF.iloc[cat.codes[0], 1]
    ageMortality = ufloat(ageMean, ageSE)

    ddimerCat = pd.cut(x=[dDimer], bins=[0, 0.5, 1, 1000])
    ddimerCoeffs = [ufloat(1, 0), ufloat(1.96, 0.73), ufloat(20.04, 6.89)]
    ddimerOR = ddimerCoeffs[ddimerCat.codes[0]]

    ferritinCat = pd.cut(x=[ferritin], bins=[0, 300, 10000])
    ferritinCoeffs = [ufloat(1, 1), ufloat(9.1, 3.6)]
    ferritinOR = ferritinCoeffs[ferritinCat.codes[0]]

    #il6OR = il6 * ufloat(1.12, 0.046)
    totalBiomarkerOR = ddimerOR * ferritinOR  # * il6OR
    combinedOdds = ageMortality/(1-ageMortality)*totalBiomarkerOR
    combinedProb = combinedOdds/(combinedOdds+1)
    return combinedProb


def getChartData(combinedProb):
    newChartData = {'x': [age], 'y': [combinedProb.nominal_value], 'type': 'scatter',
                    'mode': 'marker', 'name': 'Predicted Mortality for Characteristics', 'marker': {'size': 20}}
    updatedData = copy.deepcopy(baselineChartData)
    updatedData.append(newChartData)
    figure = {'data': updatedData, 'layout': baselineChartLayout}
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)

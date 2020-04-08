import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
from uncertainties import ufloat
import copy
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
pd.options.display.float_format = '{:.2f}'.format
mortalityDF = pd.read_csv('mortalityByAge.csv')
mortalityDF.index = mortalityDF.ageCat
mortalityDF = mortalityDF.drop(labels=mortalityDF.columns[0], axis='columns')

icuCoeffs = pd.read_stata('icuAdmitCoeffs-2020-04-08.dta')
icuCoeffs.index = icuCoeffs['index']

coeffsForDisplay = icuCoeffs.copy(deep=True)
coeffsForDisplay['priority'] = coeffsForDisplay['priority'].map('{:.2f}'.format)
coeffsForDisplay['beta'] = coeffsForDisplay['beta'].map('{:.2f}'.format)
coeffsForDisplay['sdBeta'] = coeffsForDisplay['sdBeta'].map('{:.2f}'.format)

with open('icuModelPerformance-2020-04-08.json', 'r') as file:
    modelPerformanceDict = json.load(file)
roc = modelPerformanceDict['roc']
# currently unused...saving because we might bring it back...
baselineChartData = [{'x': mortalityDF.ageMedian, 'y': mortalityDF.caseFatality, 'type': 'scatter',
                      'name': 'Median Mortality for Age', 'mode': 'markers', 'marker': {'size': '10'}}]
baselineChartLayout = {'title': 'Age-Mortality Relationship', 'xaxis': {'title': 'Age',
                                                                        'range': [30, 90]}, 'yaxis': {'title': 'Mortality', 'range': [-0.10, 1.0]}}

labelsForLabs = {'crp': 'CRP (mcg/mL)', 'ferritin':'Ferritin (ng/mL)', 'ddimer':'D-Dimer (mcg/mL)', 'hstrop':'High Sensitivity Troponin (ng/ml',
                 'hgb': 'Hemoglobin (g/dl)', 'lac':'Lactate (mmol/L)', 'ldh':'LDH (U/L)', 'albumin':'Albumin (g/dl)'}


def getInputsForLabs():
    labs = icuCoeffs.loc[icuCoeffs.priority.notnull()]
    labs.sort_values(by='priority', axis='index',ascending=False, inplace=True)
    labInputs = []
    for i, labRow in labs.iterrows():
        labName = labRow['name']
        if (labName in ['hr', 'rr', 'temp']):
            continue
        label = html.Label(labelsForLabs[labName])
        input = dcc.Input(type='number', value=labRow.p50, id=labName + "Input", min=0)
        labInputs.append(html.Div(children=[label, input], id=labName + "Panel"))
    return labInputs

def getRiskPredictorChildren():
    children = []
    children.append(html.H4('Demographics'))
    children.append(html.Div(children=[html.Label('Age'), dcc.Input(
        type='number', value=65, id='ageInput', min=0)], id="agePanel"))
    children.append(html.Div(children=[dcc.Checklist(options=[{'label': 'Female', 'value': 1}], value=[1], id="femaleInput")], id='femalePanel'))
    children.append(html.Br())
    children.append(html.H4('Vital Signs'))
    children.append(html.Div(children=[html.Label('Respiratory Rate'), dcc.Input(type='number', value=icuCoeffs.loc[icuCoeffs.name=='rr']['p50'].values[0], id='rrInput', min=0)], id="rrPanel"))
    children.append(html.Div(children=[html.Label('Temperature'), dcc.Input(type='number', value=icuCoeffs.loc[icuCoeffs.name=='temp']['p50'].values[0], id='tempInput', min=0)], id="tempPanel"))
    children.append(html.Div(children=[html.Label('Heart Rate'), dcc.Input(type='number', value=icuCoeffs.loc[icuCoeffs.name=='hr']['p50'].values[0], id='hrInput', min=0)], id="hrPanel"))
    children.append(html.Br())
    children.append(html.H4('SOFA Elements'))
    children.append(html.Div(children=[html.Label('PA O2'), dcc.Input(type='number', value=100, id='paO2Input', min=0)], id="paO2Panel"))
    children.append(html.Div(children=[html.Label('Fi O2'), dcc.Slider(id='fiO2Input', min=0.21, max=1.0, step=0.501, value=0.21, 
                                                    tooltip={'always_visible': True, 'placement': 'right'})]))
    children.append(html.Div(children=[html.Label('Platelets (x10^9 per L)'), dcc.Input(type='number', value=225, id='plateletInput', min=0)], id="plateletPanel"))
    children.append(html.Div(children=[html.Label('Glasgow Coma Scale'), dcc.Slider(id='gcsInput', min=0, max=15, step=1, value=15, 
                                                    tooltip={'always_visible': True, 'placement': 'right'})], id="gcsPanel"))
    children.append(html.Div(children=[html.Label('Bilirubin (mg/dL)'), dcc.Input(type='number', value=0.9, id='biliInput', min=0)], id="biliPanel"))
    children.append(html.Div(children=[html.Label('Creatinine (mg/dL)'), dcc.Input(type='number', value=1.2, id='creatinineInput', min=0)], id="creatininePanel"))
    children.append(html.Div(style={'font-size': '12px', }, children=[html.Label('Mean Arterial Pressure (MAP)'), 
        dcc.Dropdown(id='mapInput',
            options=[
                {'label': 'No Hypotension', 'value': '0'},
                {'label': 'MAP < 70 mm Hg', 'value': '1'},
                {'label': 'Dopamine <= 5 or Dobutamine (any dose)', 'value': '2'},
                {'label': 'Dopamine > 5, Epinephrine <= 0.1 or Norepinephrine <= 0.1', 'value': '3'},
                {'label': 'Dopamine > 15 Epinephrine > 0.1 or Norepinephrine >  0.1', 'value': '4'}
            ],
        value='0')], id="mapPanel"))
    children.append(html.Br())
    children.append(html.H4('Biomarkers'))
    children.append(html.Div(children=[html.Label('Lymphocyte Count (x 10^9 per L)' ), dcc.Input(type='number', value=18, id='lymphInput', min=0)], id="lymphPanel"))
    children.extend(getInputsForLabs())
    return children

app.layout = html.Div(children=[
    html.H1(children='Covid ICU admission risk predictor'),

    html.Div(children=[
        html.Div(style={'width': '22%'}, className='column', children=[
            dcc.Tabs(className='column', children=[
                dcc.Tab(label='Model Inputs', id='modelInputTab', children=[
                    html.Div(children=getRiskPredictorChildren(), className='column', id="inputPanel", style={'width': '100%'})
                ]),
                dcc.Tab(label="About", id='about-tab', children=[
                    html.Label('This calculator is based on a model fit to Emergency Department data at the University of Michigan and, thus calibrated to this setting. It uses Bayesian logistic regression, incorporating prior informaiton from the published literature. The model estimates the probability that a pateint will be admitted to the ICU, based on their initial ED/triage demographics, biomarkers and SOFA score.'),
                    html.Br(),
                    html.H4("Regression Coefficients for Model"),
                    dash_table.DataTable(id='regressionCoefficients', columns=[{'name':'name', 'id':'name'}, {'name':'beta', 'id':'beta'}, {'name':'sdBeta', 'id':'sdBeta'}, {'name':'priority', 'id':'priority'}],
                                        data=coeffsForDisplay.to_dict('records')),
                    html.Br(),
                    html.H4('Model Performance'),
                    html.Label(f"c-statistic: {roc:0.2f}"),
                    html.Br(),
                    html.Label("Model Calibration plot"),
                    html.Img(src='/static/calibration2020-04-08.jpg')
                ])
            ])
        ]),
        html.Div(children=[html.H4('ICU Probability'), html.H3(id='icuProb'), html.H3(
            id='icuCI')], className='column', id="outcomeRisk", style={'width': '25%'}),
    ], className='row', id='incomeOutcomePanel'),
])


@app.callback(
    [Output(component_id='icuProb', component_property='children'),
     Output(component_id='icuCI', component_property='children')],
    [Input(component_id='ageInput', component_property='value'),
     Input(component_id='ddimerInput', component_property='value'),
     Input(component_id='ferritinInput', component_property='value'),
     Input(component_id='crpInput', component_property='value'),
     Input(component_id='lymphInput', component_property='value'),
     Input(component_id='paO2Input', component_property='value'),
     Input(component_id='fiO2Input', component_property='value'),
     Input(component_id='plateletInput', component_property='value'),
     Input(component_id='gcsInput', component_property='value'),
     Input(component_id='biliInput', component_property='value'),
     Input(component_id='creatinineInput', component_property='value'),
     Input(component_id='mapInput', component_property='value'),
     Input(component_id='femaleInput', component_property='value'),
     Input(component_id='hgbInput', component_property='value'),
     Input(component_id='ldhInput', component_property='value'),
     Input(component_id='lacInput', component_property='value'),
     Input(component_id='albuminInput', component_property='value'),
     Input(component_id='hstropInput', component_property='value'),
     Input(component_id='hrInput', component_property='value'),
     Input(component_id='rrInput', component_property='value'),
     Input(component_id='tempInput', component_property='value')]
)
def update_risks(age, dDimer, ferritin, crp, lymph, paO2, fiO2, platelets, gcs, bili, creatinine, meanArtPressure, female,
                hgb, ldh, lac, albumin, hstrop, hr, rr, temp):
    xb = getCoeff('alpha')
    xb += getCoeff('betaAge') * age
    xb += getCoeff('betaDdimer') * dDimer
    xb += getCoeff('betaFerritin') * ferritin
    xb+= getCoeff('betaCrp') * crp
    xb += getCoeff('betaLymph') * lymph
    
    xb += getCoeff('betaHr') * hr
    xb += getCoeff('betaRr') * rr
    xb += getCoeff('betaTemp') * temp

    xb += getCoeff('betaHgb') * hgb
    xb += getCoeff('betaLdh') * ldh
    xb += getCoeff('betaLac') * lac
    xb += getCoeff('betaAlbumin') * albumin
    xb += getCoeff('betaHstrop') * hstrop

    xb += getCoeff('betaFemale') * len(female)
    xb += getCoeff('betaSofa') * calcSofa(paO2, fiO2, platelets, gcs, bili, creatinine, meanArtPressure)

    icuProb = np.e**xb/(1+np.e**xb)

    icuString = f"{icuProb.nominal_value*100:.0f}%"
    ciString = f"95% CI [{(icuProb.nominal_value-icuProb.std_dev*1.96)*100:.0f}% - {(icuProb.nominal_value+icuProb.std_dev*1.96)*100:.0f}%]"

    return icuString, ciString

def getCoeff(coeffName):
    return ufloat(icuCoeffs.loc[coeffName]['beta'], icuCoeffs.loc[coeffName]['sdBeta'])

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

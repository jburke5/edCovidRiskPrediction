import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
import numpy as np
from uncertainties import ufloat
import plotly.figure_factory as ff
import plotly.graph_objects as go


import scipy.stats

import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
pd.options.display.float_format = '{:.2f}'.format

date = '2020-05-05'

def loadCoefficients(fileName):
    coeffs = pd.read_stata(fileName)
    coeffs.index = coeffs['index']

    coeffsForDisplay = coeffs.copy(deep=True)
    coeffsForDisplay['priority'] = coeffsForDisplay['priority'].map('{:.2f}'.format)
    coeffsForDisplay['beta'] = coeffsForDisplay['beta'].map('{:.2f}'.format)
    coeffsForDisplay['sdBeta'] = coeffsForDisplay['sdBeta'].map('{:.2f}'.format)
    return coeffs, coeffsForDisplay

icuCoeffs, icuCoeffsForDisplay = loadCoefficients(f'ICUCoeffs-{date}.dta')
primaryCoeffs, primaryCoeffsForDisplay = loadCoefficients(f'PrimaryOutcomeCoeffs-{date}.dta')
survivalCoeffs, survival5CoeffsForDisplay = loadCoefficients(f'SurvivalCoeffs-{date}.dta')

labelsForLabs = {'crp': 'CRP (mcg/mL)', 'ferritin':'Ferritin (ng/mL)', 'ddimer':'D-Dimer (mcg/mL)', 'hstrop':'High Sensitivity Troponin (ng/ml)',
                 'hgb': 'Hemoglobin (g/dl)', 'lac':'Lactate (mmol/L)', 'ldh':'LDH (U/L)', 'albumin':'Albumin (g/dl)', 
                 'platelets' :'Platelets (x10^9 per L)', 'tbili' : 'Bilirubin (mg/dL)', 'creatinine':'Creatinine (mg/dL)',
                 'lymph': 'Lymphocyte Count (x 10^9 per L)'}

with open(f'modelPerformance-{date}.json', 'r') as file:
    modelPerformanceDict = json.load(file)
icuROC = modelPerformanceDict['icuROC']
primaryROC = modelPerformanceDict['primaryROC']


# Create distplot with custom bin_size
modelData = pd.read_stata(f'modelData-{date}.dta')

def getDistributionFig(prob):
    kde = scipy.stats.gaussian_kde(modelData["posteriorPrimaryOutcome"]).pdf(prob)
    distributionFig = ff.create_distplot([modelData["posteriorPrimaryOutcome"]], ['Primary Outcome'], bin_size=.05, show_rug=False)
    distributionFig.add_trace(go.Scatter(y=kde, x=[prob], marker={'size':40, 'color':'red'}, name="Entered Risk Parameters"))
    distributionFig.update_layout(width=700,     margin=dict(
        l=00,r=50,b=100,t=10,pad=4
    ),)
    return distributionFig

def weibull_surv(l, p, t):
    return np.exp(-1*(l*t)**p)

def getSurvivalFig(xb):
    alpha = 0.389
    times=np.linspace(0, 30, 200)
    outcomes = [weibull_surv(1/np.exp(xb/alpha), alpha, t) for t in times]

    survivalFig = go.Figure()
    survivalFig.add_trace(go.Scatter(mode='lines', y=outcomes, x=times, name='Entered Risk Parameters'))
    survivalFig.update_layout(title='Average Survival Free of Primary Outcome for Entered Parameters',
                    xaxis_title='Days from ED presentation', 
                    yaxis_title='Probability of Survival Free of Primary Outcome')
    return survivalFig


def getInputsForLabs():
    labs = icuCoeffs.loc[icuCoeffs.p50.notnull()]
    labs.sort_values(by='priority', axis='index',ascending=False, inplace=True)
    labInputs = []
    for i, labRow in labs.iterrows():
        labName = labRow['name']
        if (labName in ['hr', 'rr', 'temp', 'map', 'sat', 'comorbiditycount']):
            continue
        label = html.Label(labelsForLabs[labName])
        input = dcc.Input(type='number', value=f'{labRow.p50:.1f}', id=labName + "Input", min=0)
        labInputs.append(html.Div(children=[label, input], id=labName + "Panel"))
    return labInputs

def getRiskPredictorChildren():
    children = []
    children.append(html.H4('Demographics'))
    children.append(html.Div(children=[html.Label('Age'), dcc.Input(type='number', value=65, id='ageInput', min=0)], id="agePanel"))
    children.append(html.Div(children=[html.Label('Comorbidity Count'), dcc.Input(type='number', value=icuCoeffs.loc[icuCoeffs.name=='comorbiditycount']['p50'].values[0], id='comorbidityInput', min=0)], id="comorbidityPanel"))
    children.append(html.Div(children=[dcc.Checklist(options=[{'label': 'Female', 'value': 1}], value=[1], id="femaleInput")], id='femalePanel'))
    children.append(html.Br())
    children.append(html.H4('Vital Signs'))
    children.append(html.Div(children=[html.Label('Oxygen Saturation'), dcc.Input(type='number', value=100, id='o2SatInput', min=0)], id="o2satPanel"))
    children.append(html.Div(children=[html.Label('Respiratory Rate'), dcc.Input(type='number', value=icuCoeffs.loc[icuCoeffs.name=='rr']['p50'].values[0], id='rrInput', min=0)], id="rrPanel"))
    children.append(html.Div(children=[html.Label('Heart Rate'), dcc.Input(type='number', value=icuCoeffs.loc[icuCoeffs.name=='hr']['p50'].values[0], id='hrInput', min=0)], id="hrPanel"))
    children.append(html.Div(children=[html.Label('Temperature'), dcc.Input(type='number', value=icuCoeffs.loc[icuCoeffs.name=='temp']['p50'].values[0], id='tempInput', min=0)], id="tempPanel"))
    children.append(html.Div(children=[html.Label('Mean Arterial Pressure (mmHg)'), dcc.Input(type='number', value=f"{icuCoeffs.loc[icuCoeffs.name=='map']['p50'].values[0]:.1f}", id='mapInput', min=0)], id="mapPanel")), 
    children.append(html.Br())
    children.append(html.H4('Biomarkers'))
    children.extend(getInputsForLabs())
    return children

app.layout = html.Div(children=[
    html.H1(children='ED Covid risk predictor'),

    html.Div(children=[
        html.Div(style={'width': '22%'}, className='column', children=[
            dcc.Tabs(className='column', children=[
                dcc.Tab(label='Model Inputs', id='modelInputTab', children=[
                    html.Div(children=getRiskPredictorChildren(), className='column', id="inputPanel", style={'width': '100%'})
                ]),
                dcc.Tab(label="About", id='about-tab', children=[
                    html.Label('This calculator is based on a model fit to Emergency Department data at the University of Michigan and, thus calibrated to this setting. It uses Bayesian logistic regression, incorporating prior informaiton from the published literature. There are two separate models. The first model estimates the probability that a patient will meet our primary outcome (death, intubation or shock). The second model estimate the probability that a pateint will be admitted to the ICU. Both models use initial ED/triage demographics, biomarkers and SOFA score as covariates. Comorbidities are not currently included in the model as they are not predictive of either outcome.'),
                    html.Br(),
                    html.H4("Regression Coefficients for Primary Outcome Model"),
                    dash_table.DataTable(id='primaryRegressionCoefficients', columns=[{'name':'name', 'id':'name'}, {'name':'beta', 'id':'beta'}, {'name':'sdBeta', 'id':'sdBeta'}, {'name':'priority', 'id':'priority'}],
                                        data=primaryCoeffsForDisplay.to_dict('records')),
                    html.H4("Regression Coefficients for ICU Model"),
                    dash_table.DataTable(id='icuRegressionCoefficients', columns=[{'name':'name', 'id':'name'}, {'name':'beta', 'id':'beta'}, {'name':'sdBeta', 'id':'sdBeta'}, {'name':'priority', 'id':'priority'}],
                                        data=icuCoeffsForDisplay.to_dict('records')),
                    html.Br(),
                    html.H4('Model Performance'),
                    html.Label(f"Primary Outcome c-statistic: {icuROC:0.2f}"),
                    html.Label(f"ICU c-statistic: {primaryROC:0.2f}"),
                    html.Br(),
                    html.Label("Primary Model Calibration plot"),
                    html.Img(src='/static/primaryOutcomeCalibration2020-04-17.jpg'),
                    html.Label("ICU Calibration plot"),
                    html.Img(src='/static/icuCalibration2020-04-17.jpg')
                ])
            ])
        ]),
        html.Div(children=[html.H3('Death, Intubation, Shock Probability'), html.H5(id='primProb'), html.H5(
            id='primCI'), html.Br(), html.H3('ICU Probability'), html.H5(id='icuProb'), html.H5(
            id='icuCI')], className='column', id="outcomeRisk", style={'width': '15%'}),
        html.Div(children=[html.H4("Distribution of Primary Outcome Risk"), dcc.Graph(figure=getDistributionFig(0.2), id='distributionGraph')], className='column', id='distributionPanel', style={'width': '55%'}),
        html.Div(children=[dcc.Graph(figure=getSurvivalFig(2), id='survivalGraph')], className='column', id='survivalPanel', style={'width': '55%'}),
    ], className='row', id='inputOutcomePanel'),
])


@app.callback(
    [Output(component_id='icuProb', component_property='children'),
     Output(component_id='icuCI', component_property='children'),
     Output(component_id='primProb', component_property='children'),
     Output(component_id='primCI', component_property='children'),
     Output(component_id='distributionGraph', component_property='figure'),
     Output(component_id='survivalGraph', component_property='figure')],
    [Input(component_id='ageInput', component_property='value'),
     Input(component_id='comorbidityInput', component_property='value'),
     Input(component_id='ddimerInput', component_property='value'),
     Input(component_id='ferritinInput', component_property='value'),
     Input(component_id='crpInput', component_property='value'),
     Input(component_id='lymphInput', component_property='value'),
     Input(component_id='o2SatInput', component_property='value'),
     Input(component_id='mapInput', component_property='value'),
     Input(component_id='plateletsInput', component_property='value'),
     Input(component_id='tbiliInput', component_property='value'),
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
def update_risks(age, comorbidityCount, dDimer, ferritin, crp, lymph, o2Sat, map, platelets,  bili, creatinine, meanArtPressure, female,
                hgb, ldh, lac, albumin, hstrop, hr, rr, temp):

    icuXB = getXB(age, comorbidityCount, dDimer, ferritin, crp, lymph, o2Sat, platelets,  bili, creatinine, meanArtPressure, female,
                hgb, ldh, lac, albumin, hstrop, hr, rr, temp, icuCoeffs)
    icuProb = invlogit(icuXB.nominal_value)
    icuUci = invlogit(icuXB.nominal_value + 1.96*icuXB.std_dev)
    icuLci = invlogit(icuXB.nominal_value - 1.96*icuXB.std_dev)

    icuString = f"{icuProb*100:.0f}%"
    ciString = f"95% CI [{icuLci*100:.0f}% - {icuUci*100:.0f}%]"

    primXB = getXB(age, comorbidityCount, dDimer, ferritin, crp, lymph, o2Sat, platelets,  bili, creatinine, meanArtPressure, female,
                hgb, ldh, lac, albumin, hstrop, hr, rr, temp, primaryCoeffs)
    primProb = invlogit(primXB.nominal_value)
    primUCI = invlogit(primXB.nominal_value + 1.96*primXB.std_dev)
    primLCI = invlogit(primXB.nominal_value - 1.96*primXB.std_dev)

    primString = f"{primProb*100:.0f}%"
    primCIString = f"95% CI [{primLCI*100:.0f}% - {primUCI*100:.0f}%]"

    survXB = getXB(age, comorbidityCount, dDimer, ferritin, crp, lymph, o2Sat, platelets,  bili, creatinine, meanArtPressure, female,
                hgb, ldh, lac, albumin, hstrop, hr, rr, temp, survivalCoeffs, interceptName='intercept')

    return icuString, ciString, primString, primCIString, getDistributionFig(primProb), getSurvivalFig(survXB.nominal_value)

def invlogit(x):
    return np.e**x/(1+np.e**x)



def getXB(age, comorbidityCount, dDimer, ferritin, crp, lymph, o2Sat, platelets,  bili, creatinine, meanArtPressure, female,
                hgb, ldh, lac, albumin, hstrop, hr, rr, temp, coeffs, interceptName='alpha'):
    xb = getCoeff('alpha', coeffs)
    xb += getCoeff('betaAge', coeffs) * age
    xb += getCoeff('betaComorbiditycount', coeffs) * comorbidityCount
    xb += getCoeff('betaDdimer', coeffs) * float(dDimer)
    xb += getCoeff('betaFerritin', coeffs) * float(ferritin)
    xb += getCoeff('betaCrp', coeffs) * float(crp)
    xb += getCoeff('betaLymph', coeffs) * float(lymph)
    xb += getCoeff('betaSat', coeffs) * float(o2Sat)
    xb += getCoeff('betaHr', coeffs) * float(hr)
    xb += getCoeff('betaRr', coeffs) * float(rr)
    xb += getCoeff('betaTemp', coeffs) * float(temp)
    xb += getCoeff('betaMap', coeffs) * float(meanArtPressure)

    xb += getCoeff('betaHgb', coeffs) * float(hgb)
    xb += getCoeff('betaLdh', coeffs) * float(ldh)
    xb += getCoeff('betaLac', coeffs) * float(lac)
    xb += getCoeff('betaAlbumin', coeffs) * float(albumin)
    xb += getCoeff('betaHstrop', coeffs) * float(hstrop)
    xb += getCoeff('betaPlatelets', coeffs) * float(platelets)
    xb += getCoeff('betaTbili', coeffs) * float(bili)
    xb += getCoeff('betaCreatinine', coeffs) * float(creatinine)

    xb += getCoeff('betaFemale', coeffs) * len(female)
    return xb


def getCoeff(coeffName, coeffFile):
    return ufloat(coeffFile.loc[coeffName]['beta'], coeffFile.loc[coeffName]['sdBeta'])


def calcSofa(paO2, fiO2, platelets, gcs, bili, creatinine, meanArtPressure):
    o2Product = paO2 / fiO2
    sofa = 4 - pd.cut([o2Product], bins=[0, 100, 200, 300, 400, 1000]).codes[0]
    sofa += 4- pd.cut([platelets], bins=[0, 20, 50, 100, 150, 1000]).codes[0]
    sofa += 4 - pd.cut([gcs], bins=[0, 6, 9, 12, 14, 15]).codes[0]
    sofa +=  pd.cut([bili], bins=[0, 1.2, 1.9, 5.9, 11.0, 1000]).codes[0]
    sofa +=  pd.cut([creatinine], bins=[0, 1.2, 1.9, 3.4, 4.9, 1000]).codes[0]
    sofa +=  int(meanArtPressure)
    return sofa

if __name__ == '__main__':
    app.run_server(debug=True)

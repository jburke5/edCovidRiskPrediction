import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import pandas as pd
from uncertainties import ufloat



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

mortalityDF = pd.read_csv('mortalityByAge.csv')
mortalityDF.index=mortalityDF.ageCat
mortalityDF = mortalityDF.drop(labels=mortalityDF.columns[0], axis='columns')

app.layout = html.Div(children=[
    html.H1(children='ED Covid Risk Predictor'),

    html.Div(children=[
    	html.Div(children=[
	    	html.Div(children=[html.Label('Age'), dcc.Input(type='number', value=65, id='ageInput')], id="agePanel"),
    		html.Div(children=[html.Label('D-Dimer'), dcc.Input(type='number', value=0.0, id='dDimerInput')], id="dDimerPanel"),
    		html.Div(children=[html.Label('IL-6'), dcc.Input(type='number', value=0.0, id='il6Input')], id="il6Panel"),
		    html.Div(children=[html.Label('Ferritin'), dcc.Input(type='number', value=0.0, id='ferritinInput')], id="ferritinPanel"),
		], className='column', id="inputPanel", style={'width' : '15%'}),
		html.Div(children=[html.Label('Mortality'), html.H3(id='MeanMortality'), html.H3(id='MortalityCI')], className='column', id="outcomeRisk", style={'width' : '25%'}),
	], className='row', id='inputOutputContainer'),
], id="outermost")


@app.callback(
    [Output(component_id='MeanMortality', component_property='children'),
    Output(component_id='MortalityCI', component_property='children')],
    [Input(component_id='ageInput', component_property='value'),
    Input(component_id='dDimerInput', component_property='value'),
    Input(component_id='il6Input', component_property='value'),
    Input(component_id='ferritinInput', component_property='value')]
)
def update_risks(age, dDimer, il6, ferritin):
	cat = pd.cut(x=[age], bins=[0, 9, 19, 29, 39, 49, 59, 69, 79, 120])
	ageMean = mortalityDF.iloc[cat.codes[0], 0]
	ageSE = mortalityDF.iloc[cat.codes[0], 1]
	ageMortality = ufloat(ageMean, ageSE)

	ddimerCat = pd.cut(x=[dDimer], bins=[0, 0.5, 1, 1000])
	ddimerCoeffs = [ufloat(1, 0), ufloat(1.96,0.73), ufloat(20.04,6.89) ]
	ddimerOR = ddimerCoeffs[ddimerCat.codes[0]]
	
	ferritinCat = pd.cut(x=[ferritin], bins=[0, 300, 10000])
	ferritinCoeffs = [ufloat(1, 1), ufloat(9.1, 3.6) ]
	ferritinOR = ferritinCoeffs[ferritinCat.codes[0]]
	
	il6OR = il6 * ufloat(1.12, 0.046)
	totalBiomarkerOR = ddimerOR * ferritinOR * il6OR
	combinedOdds = ageMortality/(1-ageMortality)*totalBiomarkerOR
	combinedProb = combinedOdds/(combinedOdds+1)
	return f"{combinedProb.nominal_value*100:.0f}%", f"95% CI [{(combinedProb.nominal_value-combinedProb.std_dev*1.96)*100:.0f}% - {(combinedProb.nominal_value+combinedProb.std_dev*1.96)*100:.0f}%]"

if __name__ == '__main__':
    app.run_server(debug=True)
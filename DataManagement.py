import pandas as pd
import numpy as np
import statsmodels.imputation.mice as mice


caseAbstractionDate = "5-5-20"


def loadFiles():
    caseAbstractionsFileName = f"baseData/caseAbstractions-{caseAbstractionDate}.dta"
    labDataFileName = 'baseData/ED_COVID_Data4_17_2020.csv'
    caseAbstractions = pd.read_stata(caseAbstractionsFileName)

    # incredibly  annoyingly the redcap time stamps appear to be in miliseocnds starting in 1980, not 1970...
    caseAbstractions['intubation_date'] = caseAbstractions['intubation_date'] - 10*365.25*24*60*60*1000
    caseAbstractions['shock_date'] = caseAbstractions['shock_date'] - 10*365.25*24*60*60*1000
    caseAbstractions['ed_arrival_date'] = caseAbstractions['ed_arrival_dttm'] - 10*365.25*24*60*60*1000

    caseAbstractions['intubation_date']= pd.to_datetime(caseAbstractions['intubation_date'], unit='ms')
    caseAbstractions['shock_date'] = pd.to_datetime(caseAbstractions['shock_date'], unit='ms')
    caseAbstractions['ed_arrival_date'] = pd.to_datetime(caseAbstractions['ed_arrival_date'], unit='ms')

    caseAbstractions = caseAbstractions.drop(caseAbstractions[caseAbstractions.outcome_reviewer.isnull()].index, axis='index')
    caseAbstractions = caseAbstractions[['pat_enc_csn_id', 'mrn', 'hypertension', 'diabetes', 'asthma',
        'copd', 'chronic_lung', 'home_o2', 'osa', 'immunocompromised', 'pregnant', 'intubation', 'intubation_date',
                                        'shock', 'shock_date', 'dni_dnar', 'death', 'death_date', 'ed_arrival_date']]
    caseAbstractions['primaryOutcome'] = (caseAbstractions['intubation'] == 'Intubated') | (caseAbstractions['shock'] == 'Yes') | (caseAbstractions['death'] == 'Yes')
    caseAbstractions['primaryOutcomeDate'] = caseAbstractions[['intubation_date', 'shock_date', 'death_date']].min(axis='columns')

    caseAbstractions.loc[caseAbstractions.primaryOutcomeDate.notnull(), 'lastTime'] = caseAbstractions.primaryOutcomeDate-caseAbstractions.ed_arrival_date
    caseAbstractions.loc[caseAbstractions.primaryOutcomeDate.isnull(), 'lastTime'] = pd.to_datetime(caseAbstractionDate)-caseAbstractions.ed_arrival_date

    for var in ['dni_dnar', 'hypertension', 'diabetes', 'asthma', 'copd', 'chronic_lung', 'home_o2', 'osa', 'immunocompromised', 'pregnant']:
        caseAbstractions[var] = caseAbstractions[var] == "Yes"


    rawData = pd.read_csv(labDataFileName)
    # identify covid cases
    rawData['covid'] = rawData.COVID19_POSTIVE=="Y"
    rawData = rawData.loc[rawData.covid]

    # clean outcomes
    rawData.loc[(rawData.ED_PM_EXPIRED_IN_ED_YN=="Y"), 'ED_ADMIT_TO_ICU_YN'] = 1
    rawData['icu'] = rawData.ED_ADMIT_TO_ICU_YN=="Y"
    rawData['edOrHospitalDischarge'] = ((rawData.ED_DISPOSITION_NAME == 'Discharge') | (rawData.HOSP_DISPOSITION_NAME == '11 Home or Self Care'))

    rawData.rename(columns={'AGE_AT_VISIT_YRS' : 'age', 'TRIAGE_SBP' : 'sbp', 'TRIAGE_DBP' : 'dbp',
                            'TRIAGE_HR' : 'hr', 'TRIAGE_TEMP' : 'temp', 'ED_LAB_CRP' : 'crp', 
                            'ED_LAB_DDIMER' : 'dDimer', 'ED_LAB_FERRITIN' : 'ferritin',
                            'ED_CBC_PLT' : 'platelets', 'ED_LAB_CMP_CR' : 'creatinine',  
                            'ED_LAB_CMP_TBILI' : 'tbili', 'ED_HSTROP0' : 'hsTrop', 
                            'ED_LAB_IL6' : 'il6', 'ED_CBC_LYM' : 'lymph',
                            'ED_CBC_HGB': 'hgb', 'ED_VBG_LAC':'lac', 'ED_LDH':'ldh',
                            'ED_LAB_CMP_ALB': 'albumin', 'TRIAGE_HR':'hr',
                            'TRIAGE_RR':'rr', 'TRIAGE_TEMP':'temp', 'ED_LAB_CMP_ALT' : 'alt', 
                            'ED_HSTROP2' : 'hsTrop2', 'TRIAGE_SPO2' : 'o2Sat'}, inplace=True)

    # truncate high low lab values and convert to floats
    rawData.crp.replace('<0.2', 0.1, inplace=True)

    rawData.dDimer.replace('<0.17', 0.085, inplace=True)
    rawData.dDimer.replace('>35.00', 40, inplace=True)

    rawData.ferritin.replace('>16500.0', 17000, inplace=True)
    rawData.ferritin.replace('>1650.0', 17000, inplace=True)

    rawData.il6.replace('>3670.0', 4100, inplace=True)
    rawData.il6.replace('>4060.0', 4100, inplace=True)
    rawData.il6.replace('<4.0', 2, inplace=True)


    rawData.alt.replace('<8', 4, inplace=True)

    rawData.hsTrop.replace('<6', 3, inplace=True)
    rawData.hsTrop2.replace('<6', 3, inplace=True)

    rawData.platelets.replace('<2', 1, inplace=True)
    rawData.creatinine.replace('SEE BELOW', np.nan, inplace=True)
    rawData.creatinine.replace('<0.10', 0.005, inplace=True)

    rawData.hgb.replace('SEE BELOW', np.nan, inplace=True)
    rawData.lac.replace('SEE BELOW', np.nan, inplace=True)

    rawData.crp = rawData.crp.astype('float')
    rawData.dDimer = rawData.dDimer.astype('float')
    rawData.ferritin = rawData.ferritin.astype('float')
    rawData.il6 = rawData.il6.astype('float')
    rawData.alt = rawData.alt.astype('float')
    rawData.hsTrop = rawData.hsTrop.astype('float')
    rawData.hsTrop2 = rawData.hsTrop2.astype('float')
    rawData.platelets = rawData.platelets.astype('float')
    rawData.creatinine = rawData.creatinine.astype('float')
    rawData.hgb =  rawData.hgb.astype('float')
    rawData.lac =  rawData.lac.astype('float')
    rawData.ldh =  rawData.ldh.astype('float')
    rawData.albumin =  rawData.albumin.astype('float')
    rawData.hr = rawData.hr.astype('float')
    rawData.rr = rawData.rr.astype('float')

    rawData.tbili = rawData.tbili.astype('float')

    rawData['female'] = rawData.GENDER=="F"
    rawData.female = rawData.female.astype('int')

    rawData['highFi02'] = rawData.TRIAGE_FIO2 > 50
    rawData['highFi02'] = rawData['highFi02'].astype('int')

    rawData = rawData[['age', 'female', 'sbp', 'dbp', 'hr', 'rr',
                    'temp', 'highFi02', 'crp', 'dDimer', 'ferritin', 
                    'platelets', 'lymph', 'creatinine', 'tbili', 
                    'hsTrop', 'il6', 'covid', 'icu', 'hgb', 'lac', 
                    'ldh', 'albumin', 'MRN', 'PAT_ENC_CSN_ID', 'edOrHospitalDischarge', 'o2Sat']] 

    caseAbstractions = caseAbstractions.rename(columns={'mrn' : 'MRN', 'pat_enc_csn_id' : 'PAT_ENC_CSN_ID' })
    caseAbstractions = caseAbstractions.drop(labels=['intubation', 'shock', 'death', 'intubation_date', 'shock_date', 'death_date'], axis='columns')
    rawData = rawData.merge(caseAbstractions, on=['MRN', 'PAT_ENC_CSN_ID'])

    rawData.lastTime = rawData.lastTime.apply(lambda x: x.days)

    rawData = rawData.drop(labels=['MRN', 'PAT_ENC_CSN_ID'], axis='columns')

    rawData.loc[rawData.edOrHospitalDischarge, 'lastTime'] = rawData.lastTime.max()
    rawData.loc[rawData.lastTime <= 0, 'lastTime'] = 0.1

    rawData.to_stata('rawData.dta')

    rawData['totalMissing'] = rawData.isnull().sum(axis=1)
    for col in rawData.columns:
        if col in ['hr', 'rr', 'sbp', 'dbp', 'temp', 'crp', 'dDimer', 'ferritin', 'platelets', 
                'lymph', 'creatinine', 'tbili', 'hsTrop', 'il6', 'hgb', 'lac', 'ldh', 'albumin', 'o2Sat']:
            rawData[str(col)+"Missing"] = rawData[col].isnull()

    return caseAbstractions, rawData



def ols_formula(df, dependent_var):
    df_columns = list(df.columns.values)
    df_columns.remove(dependent_var)
    fml = ''
    for col in df_columns:
        fml = fml + ' + ' + col
    return fml


def impute(rawData):
    # impute missing lab and vitals values

    shortData = rawData[['age', 'female', 'sbp', 'dbp', 'crp', 'dDimer',  'ferritin', 'platelets', 
                        'creatinine', 'tbili', 'hsTrop', 'il6', 'lymph', 'hgb', 'lac', 'ldh', 'albumin',
                        'hr', 'rr',  'temp', 'icu', 'hypertension', 'diabetes', 'asthma', 'copd', 
                        'chronic_lung', 'home_o2', 'osa', 'immunocompromised', 'pregnant', 'primaryOutcome', 
                        'highFi02', 'lastTime', 'o2Sat']]

    imputedData = mice.MICEData(shortData)

    for var in ['age', 'female', 'sbp', 'dbp', 'crp', 'dDimer', 'ferritin', 'platelets', 'creatinine', 
                'tbili', 'hsTrop', 'il6', 'lymph', 'hgb', 'lac', 'ldh', 'albumin', 'hr', 'rr',  'temp']:
        imputedData.set_imputer(var, formula=ols_formula(shortData, var))

    imputedData.update_all(20)
    return imputedData.data, imputedData

def calcSofa(cleanedData):

    # crude sofa score on imputed dataset
    # https://www.mdcalc.com/sequential-organ-failure-assessment-sofa-score#evidence

    # pao2/fi02
    cleanedData['sofa'] = 0 # for the PaO2/fio2 ratio — looks like almost all our peopel are on room air, and we don't have pa02 on many 
    cleanedData.loc[cleanedData.highFi02, 'sofa'] = 2 # crudely give elevated points for high Fi01, 

    # platelets
    sofaPlateletPoints = {0 : 4, 1 : 3, 2: 2, 3: 1, 4: 0}
    cleanedData['plateletCat'] = pd.cut(cleanedData.platelets, [0, 20, 49, 99, 149, 10000]).values.codes
    cleanedData['plateletPoints'] = [sofaPlateletPoints[cat] for cat in cleanedData.plateletCat]
    cleanedData['sofa'] = cleanedData.sofa + cleanedData.plateletPoints

    #gcs - missing...will just impute 0.2 points for eerybody...most are going to be very low
    cleanedData['sofa'] = cleanedData.sofa + 0.2 

    # t bili
    cleanedData['biliCat'] = pd.cut(cleanedData.tbili, [0, 1.2, 1.99, 5.99, 11.99, 100]).values.codes
    cleanedData['sofa'] = cleanedData.sofa + cleanedData.biliCat

    # blood pressure — no pressor data for now...
    cleanedData['map'] = cleanedData.sbp * 1/3 + cleanedData.dbp * 2/3
    cleanedData.loc[cleanedData.map < 70, 'sofa'] = cleanedData.sofa + 1

    # creatinine
    cleanedData['creatCat'] = pd.cut(cleanedData.creatinine, [0, 1.19, 1.99, 3.49, 4.99, 100]).values.codes
    cleanedData['sofa'] = cleanedData.sofa + cleanedData.creatCat
    return cleanedData

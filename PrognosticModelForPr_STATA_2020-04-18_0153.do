version 13
clear

import delimited record_id pat_enc_csn_id mrn ed_arrival_dttm close_contact healthcare nursing_home homeless prisoner tobacco marijuana alcohol priorhospital sxs_onset date_documented exposure_reviewer exposure_risk_factors_complete hypertension diabetes asthma copd chronic_lung home_o2 osa immunocompromised pregnant pmh_reviewer past_medical_history_complete ace_arb anticoagulation immunosuppresant ibuprofen med_reviewer medications_complete day30 intubation intubation_date high_flow nasal_canula shock shock_date dni_dnar discharge_date death death_date readmit ed_revisit comment outcome_reviewer outcomes_complete using "PrognosticModelForPr_DATA_NOHDRS_2020-04-18_0153.csv", varnames(nonames)

label data "PrognosticModelForPr_DATA_NOHDRS_2020-04-18_0153.csv"

label define close_contact_ 1 "Yes" 0 "No" 
label define healthcare_ 1 "Yes" 0 "No" 
label define nursing_home_ 1 "Yes" 0 "No" 
label define homeless_ 1 "Yes" 0 "No" 
label define prisoner_ 1 "Yes" 0 "No" 
label define tobacco_ 1 "Yes" 0 "No" 
label define marijuana_ 1 "Yes" 0 "No" 
label define alcohol_ 1 "Yes" 0 "No" 
label define priorhospital_ 1 "Yes" 0 "No" 
label define date_documented_ 1 "Documented and clear" 2 "Documented but vague" 3 "Not Documented" 
label define exposure_reviewer_ 1 "E. Bisco" 2 "Z. Chopra" 3 "A. Holmes" 4 "J. Nelson" 5 "S. Perkins" 6 "J. Hirschl" 
label define exposure_risk_factors_complete_ 0 "Incomplete" 1 "Unverified" 2 "Complete" 
label define hypertension_ 1 "Yes" 0 "No" 
label define diabetes_ 1 "Yes" 0 "No" 
label define asthma_ 1 "Yes" 0 "No" 
label define copd_ 1 "Yes" 0 "No" 
label define chronic_lung_ 1 "Yes" 0 "No" 
label define home_o2_ 1 "Yes" 0 "No" 
label define osa_ 1 "Yes" 0 "No" 
label define immunocompromised_ 1 "Yes" 0 "No" 
label define pregnant_ 1 "Yes" 0 "No" 
label define pmh_reviewer_ 1 "E. Bisco" 2 "Z. Chopra" 3 "A. Holmes" 4 "J. Nelson" 5 "S. Perkins" 6 "J. Hirschl" 
label define past_medical_history_complete_ 0 "Incomplete" 1 "Unverified" 2 "Complete" 
label define ace_arb_ 1 "Yes" 0 "No" 
label define anticoagulation_ 1 "Yes" 0 "No" 
label define immunosuppresant_ 1 "Yes" 0 "No" 
label define ibuprofen_ 1 "Yes" 0 "No" 
label define med_reviewer_ 1 "E. Bisco" 2 "Z. Chopra" 3 "A. Holmes" 4 "J. Nelson" 5 "S. Perkins" 6 "J. Hirschl" 
label define medications_complete_ 0 "Incomplete" 1 "Unverified" 2 "Complete" 
label define day30_ 1 "Yes" 0 "No" 
label define intubation_ 1 "Intubated" 2 "Not intubated but required non-invasive ventilation or high flow nasal cannula" 3 "Required supplemental oxygen via nasal canula" 4 "Did not require supplemental oxygen" 
label define shock_ 1 "Yes" 0 "No" 
label define dni_dnar_ 1 "Yes" 0 "No" 
label define death_ 1 "Yes" 0 "No" 
label define outcome_reviewer_ 1 "E. Bisco" 2 "Z. Chopra" 3 "A. Holmes" 4 "J. Nelson" 5 "S. Perkins" 6 "J. Hirschl" 
label define outcomes_complete_ 0 "Incomplete" 1 "Unverified" 2 "Complete" 

label values close_contact close_contact_
label values healthcare healthcare_
label values nursing_home nursing_home_
label values homeless homeless_
label values prisoner prisoner_
label values tobacco tobacco_
label values marijuana marijuana_
label values alcohol alcohol_
label values priorhospital priorhospital_
label values date_documented date_documented_
label values exposure_reviewer exposure_reviewer_
label values exposure_risk_factors_complete exposure_risk_factors_complete_
label values hypertension hypertension_
label values diabetes diabetes_
label values asthma asthma_
label values copd copd_
label values chronic_lung chronic_lung_
label values home_o2 home_o2_
label values osa osa_
label values immunocompromised immunocompromised_
label values pregnant pregnant_
label values pmh_reviewer pmh_reviewer_
label values past_medical_history_complete past_medical_history_complete_
label values ace_arb ace_arb_
label values anticoagulation anticoagulation_
label values immunosuppresant immunosuppresant_
label values ibuprofen ibuprofen_
label values med_reviewer med_reviewer_
label values medications_complete medications_complete_
label values day30 day30_
label values intubation intubation_
label values shock shock_
label values dni_dnar dni_dnar_
label values death death_
label values outcome_reviewer outcome_reviewer_
label values outcomes_complete outcomes_complete_



tostring ed_arrival_dttm, replace
gen double _temp_ = Clock(ed_arrival_dttm,"YMDhm")
drop ed_arrival_dttm
rename _temp_ ed_arrival_dttm
format ed_arrival_dttm %tCMonth_dd,_CCYY_HH:MM

tostring sxs_onset, replace
gen _date_ = date(sxs_onset,"YMD")
drop sxs_onset
rename _date_ sxs_onset
format sxs_onset %dM_d,_CY

tostring intubation_date, replace
gen double _temp_ = Clock(intubation_date,"YMDhm")
drop intubation_date
rename _temp_ intubation_date
format intubation_date %tCMonth_dd,_CCYY_HH:MM

tostring high_flow, replace
gen double _temp_ = Clock(high_flow,"YMDhm")
drop high_flow
rename _temp_ high_flow
format high_flow %tCMonth_dd,_CCYY_HH:MM

tostring nasal_canula, replace
gen double _temp_ = Clock(nasal_canula,"YMDhm")
drop nasal_canula
rename _temp_ nasal_canula
format nasal_canula %tCMonth_dd,_CCYY_HH:MM

tostring shock_date, replace
gen double _temp_ = Clock(shock_date,"YMDhm")
drop shock_date
rename _temp_ shock_date
format shock_date %tCMonth_dd,_CCYY_HH:MM

tostring discharge_date, replace
gen _date_ = date(discharge_date,"YMD")
drop discharge_date
rename _date_ discharge_date
format discharge_date %dM_d,_CY

tostring death_date, replace
gen _date_ = date(death_date,"YMD")
drop death_date
rename _date_ death_date
format death_date %dM_d,_CY

tostring readmit, replace
gen _date_ = date(readmit,"YMD")
drop readmit
rename _date_ readmit
format readmit %dM_d,_CY

tostring ed_revisit, replace
gen _date_ = date(ed_revisit,"YMD")
drop ed_revisit
rename _date_ ed_revisit
format ed_revisit %dM_d,_CY

label variable record_id "Record ID"
label variable pat_enc_csn_id "Pat_enc_csn_id "
label variable mrn "mrn "
label variable ed_arrival_dttm "ED arrival date/time"
label variable close_contact "Close contact with confirmed COVID-19?"
label variable healthcare "Healthcare/public safety worker?"
label variable nursing_home "Live in nursing home/group home/SNF/ECF  "
label variable homeless "Homeless/Shelter"
label variable prisoner "Prisoner"
label variable tobacco "Current tobacco use"
label variable marijuana "Current marijuana use"
label variable alcohol "Daily alcohol use"
label variable priorhospital "Hospital admission within the past 2 weeks (prior to current ED visit)"
label variable sxs_onset "Date of Illness Onset"
label variable date_documented "Date of onset clearly documented?"
label variable exposure_reviewer "Exposure Reviewer"
label variable exposure_risk_factors_complete "Complete?"
label variable hypertension "Hypertension"
label variable diabetes "Diabetes"
label variable asthma "Asthma"
label variable copd "COPD"
label variable chronic_lung "Other Chronic Lung Disease"
label variable home_o2 "Requires home oxygen at least some of the time?"
label variable osa "Obstructive Sleep Apnea"
label variable immunocompromised "Immunocompromised state (eg. HIV, active cancer, etc)"
label variable pregnant "Pregnant"
label variable pmh_reviewer "PMH Reviewer"
label variable past_medical_history_complete "Complete?"
label variable ace_arb "ACE-I or ARB"
label variable anticoagulation "Anticoagulation/anti-platelet"
label variable immunosuppresant "Immunosuppresant"
label variable ibuprofen "Anti-inflammatory medication"
label variable med_reviewer "Medication Reviewer"
label variable medications_complete "Complete?"
label variable day30 "Has it been 28 days since initial  presentation to the ED?"
label variable intubation "Respiratory status"
label variable intubation_date "If intubated, intubation Date and time"
label variable high_flow "If non-invasive ventilation or high flow nasal canula, date and time it was started"
label variable nasal_canula "If nasal canula only, date and time it was started"
label variable shock "Shock requiring a vasopressor "
label variable shock_date "Start date and time of vasopressor"
label variable dni_dnar "Do Not Intubate (DNI) or Do not attempt resuscitation (DNAR)"
label variable discharge_date "Hospital Discharge Date"
label variable death "Death within 28 days of presentation"
label variable death_date "Death Date"
label variable readmit "Date of first hospital admission that occurred within 28 days of initial discharge: "
label variable ed_revisit "Date of first ED visit that occurred within 28 days of initial discharge:"
label variable comment "Comments regarding bounce-backs:"
label variable outcome_reviewer "Outcome Reviewer"
label variable outcomes_complete "Complete?"

order record_id pat_enc_csn_id mrn ed_arrival_dttm close_contact healthcare nursing_home homeless prisoner tobacco marijuana alcohol priorhospital sxs_onset date_documented exposure_reviewer exposure_risk_factors_complete hypertension diabetes asthma copd chronic_lung home_o2 osa immunocompromised pregnant pmh_reviewer past_medical_history_complete ace_arb anticoagulation immunosuppresant ibuprofen med_reviewer medications_complete day30 intubation intubation_date high_flow nasal_canula shock shock_date dni_dnar discharge_date death death_date readmit ed_revisit comment outcome_reviewer outcomes_complete 
set more off
describe

library(gdata)
library(meta)

# dropped the 2 studies that don't have an effect size
cleanedData = read.xls("/Users/burke/Documents/research/edCovid/systematicReview/papersVariablesCoefficients.xlsx")



cleanedData$effect <- as.numeric(as.character(cleanedData$effectSize))
cleanedData$se <- as.numeric(as.character(cleanedData$se))
cleanedData$n <- as.numeric(as.character(cleanedData$n))

ageData <-subset(cleanedData, cleanedData$Parameterization=='Continuous')
ageData <- subset(ageData, ageData$Factor=='Age')

lymphData <-subset(cleanedData, cleanedData$Parameterization=='Continuous')
lymphData <- subset(lymphData, lymphData$Factor=='Lymphocyte')

femaleData <-subset(cleanedData, cleanedData$Parameterization=='Dichotomous')
femaleData <- subset(femaleData, femaleData$Factor=='Male Sex')

crpData <-subset(cleanedData, cleanedData$Parameterization=='Continuous')
crpData <- subset(crpData, crpData$Factor=='CRP')


overallMeta <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=cleanedData)



cleanedData <- subset(cleanedData, cleanedData$include==1)

cleanedData$multiFactorIntervention = 0
cleanedData$multiFactorIntervention <- ifelse(cleanedData$ems == 1 & cleanedData$publicEd == 1, 1, cleanedData$multiFactorIntervention)
cleanedData$multiFactorIntervention <- ifelse(cleanedData$ems == 1 & cleanedData$telestroke == 1, 1,cleanedData$multiFactorIntervention)
cleanedData$multiFactorIntervention <- ifelse(cleanedData$publicEd == 1 & cleanedData$telestroke == 1, 1, cleanedData$multiFactorIntervention)

ischemicOnly <- subset(cleanedData, cleanedData$restrictedToIschemic==1)
ischemicOnly$id <- row.names(ischemicOnly) 
cleanedData$id <- row.names(cleanedData) 
cleanedMinusTargetStroke <- subset(cleanedData, cleanedData$id != 20)
ischemicMinusTargetStroke <- subset(ischemicOnly, ischemicOnly$id != 20)


overallMeta <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=cleanedData)
forest(overallMeta)
funnel(overallMeta)

overallMetaExcludeTargetStroke <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=cleanedMinusTargetStroke)
forest(overallMetaExcludeTargetStroke)

ischemicOnlyMeta <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=ischemicOnly)
forest(ischemicOnlyMeta)
funnel(ischemicOnlyMeta)

ischemicOnlyMinusTargetStrokeMeta <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=ischemicMinusTargetStroke)
forest(ischemicOnlyMinusTargetStrokeMeta)

multiFactorMeta <-  metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=ischemicOnly, subset=which(ischemicOnly$multiFactorIntervention==1))
forest(multiFactorMeta)

singleLocationMeta <-  metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=ischemicOnly, subset=which(ischemicOnly$singleLocation==1))
forest(singleLocationMeta)


emsMeta <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=ischemicOnly, subset=which(ischemicOnly$ems==1))
forest(emsMeta)

emsMetaMinusTargetStroke <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=ischemicOnly, subset=which(ischemicMinusTargetStroke$ems==1))
forest(emsMetaMinusTargetStroke)


educationMeta <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=cleanedData, subset=which(cleanedData$publicEd==1))
forest(educationMeta)

telemedicineMeta <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=ischemicOnly, subset=which(ischemicOnly$telestroke==1))
forest(telemedicineMeta)



prePostMeta <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=ischemicOnly, subset=which(ischemicOnly$prePost==1))
forest(prePostMeta)

rctMeta <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=ischemicOnly, subset=which(cleanedData$rct==1))
forest(rctMeta)

# exclude one study at a time.
ids <- as.numeric(ischemicOnly$id)

effectSizes = vector()
for(studyCount in 1:length(ids)){
    ischemicOnly$excludeOneAtATime =0 
    ischemicOnly$excludeOneAtATime <- ifelse(studyCount==ischemicOnly$id, 1, 0)
    excludeMeta <- metabin(treatmentCount, numTreatment, controlCount, numControl, studlab=author, data=ischemicOnly, subset=which(ischemicOnly$excludeOneAtATime==0))
    effectSizes[studyCount] = exp(excludeMeta$TE.fixed)
}



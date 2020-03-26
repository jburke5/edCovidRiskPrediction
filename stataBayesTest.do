sysuse auto
set seed 4534523

quietly: sum mpg
local meanMPG = `r(mean)'
local sdMPG = `r(sd)'

quietly: sum length
local meanLength = `r(mean)'
local sdLength = `r(sd)'

quietly: sum displacement
local meanDisplacement = `r(mean)'
local sdDisplacement = `r(sd)'

quietly: sum displacement
local meanDisplacement = `r(mean)'
local sdDisplacement = `r(sd)'

quietly: sum trunk
local meanTrunk = `r(mean)'
local sdTrunk = `r(sd)'

gen standardMGP = (mpg-`meanMPG')/`sdMPG'
gen standardLength = (length-`meanLength')/`sdLength'
gen standardDisplacement = (displacement-`meanDisplacement')/`sdDisplacement'
gen standardTrunk = (trunk-`meanTrunk')/`sdTrunk'


gen discontinueNoIntercept = -3*standardMGP + 2*standardLength + 2*standardDisplacement - 1*standardTrunk

quietly: sum discontinueNoIntercept
local discontinueMean = `r(mean)'
local discontinueSD = `r(sd)'

gen discontinueIntercept = rnormal(`discontinueMean'*-1, `discontinueSD'*0.65)

gen discontinueXB = discontinueNoIntercept + discontinueIntercept

gen discontinue = rbinomial(1, invlogit(discontinueXB))

logit discontinue standardMGP standardLength standardDisplacement standardTrunk 
bayes: logit discontinue standardMGP standardLength standardDisplacement standardTrunk 

//short version is that it seesm that its pretty easy to fit a regression model with priors in stata!

bayes, prior({discontinue:standardMGP}, normal(-2,.1)) : logistic discontinue standardMGP standardLength standardDisplacement standardTrunk



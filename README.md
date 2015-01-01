pyActuarialValue
================

pyActuarialValue is an open source implementation of the [Actuarial Value calculator](http://www.cms.gov/CCIIO/Resources/Regulations-and-Guidance/Downloads/2015-av-calculator-final.xlsm)
developed the Department of Health and Human Services (HHS) for determining the 
relative amount of claims paid a health plan.

pyActuarialValue is in early stages of development. The current master branch 
reflects development toward the draft [2016 calculator.](http://www.cms.gov/CCIIO/Resources/Regulations-and-Guidance/Downloads/Draft-2016-AVC-Methodology-MASTER-for-112114.pdf)  
Many plan types are not supported but the goal is to support the complete 
calculator and offer additional support for alternate actuarial value 
statements.

## Install
Before running the calculator run ``seed_data`` to load the actuarial value(AV) 
data.

## Usage

The core actuarial value function takes a representation of the health plan. 
This representation can be created using directly from code or through a JSON 
representation. Details of the JSON representation can be found in the [wiki 
for this repo](https://github.com/jpbarela/pyActuarialValue/wiki/JSON-Health-Plan-Representations).

It is also possible to run the calculator directly from the command line. To 
run the calculator from the command line simply type ``av {health_plan_json}``.

## Contributing

The calculator is built in an incremental fashion to be used as quickly as 
possible. If you would like a specific set of benefits to be included in the 
calculator or have found an error in the calculator please open an issue.

If you are planning on implementing a set of benefits in the calculator, please 
open an issue as well so that other developers know that those sets of benefits 
will be implemented.

Please rebase and squash all commits into a single commit before submitting a 
pull request.
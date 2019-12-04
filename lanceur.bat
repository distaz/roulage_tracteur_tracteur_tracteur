if not exist ".inst" python -m pip install -r requirements.txt
if not exist ".inst" echo "INSTALL_DONE" > .inst
if exist ".inst" attrib +H .inst

python TTFLMatrix.py

R CMD BATCH algo_hongrois.R

if exist .RData del .RData
if exist .Rhistory del .Rhistory
if exist algo_hongrois.Rout del algo_hongrois.Rout
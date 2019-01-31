python -m pip install -r requirements.txt

python TTFL_matrix.py

R CMD BATCH algo_hongrois.R

if exist .RData del .RData
if exist .Rhistory del .Rhistory
if exist algo_hongrois.Rout del algo_hongrois.Rout
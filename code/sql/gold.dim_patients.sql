CREATE OR ALTER VIEW gold.dim_patients AS
select
ROW_NUMBER() OVER (ORDER BY px.PK_psPersonalData) as patients_key,
px.PK_psPersonalData as patient_id,
px.firstname as first_name,
px.gender,
px.religion,
px.nationality
from silver.psPersonaldata as px
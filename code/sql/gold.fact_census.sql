
CREATE VIEW gold.fact_census AS
select
reg.PK_psPatRegisters as patient_tracing,
reg.FK_emdPatients as patient_id,
reg.registrydate as registry_date,
reg.dischdate as discharge_date,
reg.pattrantype as transction_type,
reg.registrystatus as registry_status,
reg.cancelflag as cancel_flag,
case	
	when px.PK_psPersonalData is null then reg.FK_emdPatients
	else px.PK_psPersonalData
end as new_patient_id,
case
	when px.firstname is null then 'cash transaction'
	else px.firstname
end as new_firstname,
case
	when px.gender is null then 'n/a'
	else px.gender
end as new_gender,
case
	when px.religion is null then 'n/a'
	else px.religion
end as new_religion,
case
	when px.nationality is null then 'n/a'
	else px.nationality
end as new_nationality
from silver.psPatRegisters as reg
left join silver.psPersonaldata as px on px.PK_psPersonalData = reg.FK_emdPatients


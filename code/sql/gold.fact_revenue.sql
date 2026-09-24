CREATE OR ALTER VIEW gold.fact_revenue AS
select
ROW_NUMBER() OVER (ORDER BY item.PK_psPatitem) as item_key,
item.PK_psPatitem as item_id,
item.FK_psPatRegisters as patient_tracing,
item.FK_emdPatients as patient_id,
item.FK_mscWarehouse as warehouse_id,
item.FK_iwItemsREN as item_rendered,
item.renqty as rendered_quantity,
item.renprice as rendered_price,
item.rendate as rendered_date,
item.renqty * item.renprice as amount,
warehouse.description as warehouse,
case
	when personal.PK_psPersonalData is null then 0
	else personal.PK_psPersonalData
end as new_personal_data_id,
case
	when personal.firstname is null then 'n/a'
	else personal.firstname
end as new_first_name,
case
	when personal.gender is null then 'n/a'
	else personal.gender
end as new_gender,
case
	when personal.religion is null then 'n/a'
	else personal.religion
end as new_religion,
case
	when personal.nationality is null then 'n/a'
	else personal.nationality
end as new_nationality
from silver.psPatitem as item
left join silver.mscWarehouse as warehouse on warehouse.PK_mscWarehouse = item.FK_mscWarehouse
left join silver.psPersonaldata as personal on personal.PK_psPersonalData = item.FK_emdPatients

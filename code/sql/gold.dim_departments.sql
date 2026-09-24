CREATE OR ALTER VIEW gold.dim_departments AS
select 
ROW_NUMBER() OVER (ORDER BY w.PK_mscWarehouse) as departments_key,
w.PK_mscWarehouse as warehouse_id,
w.description as warehouse_description
from silver.mscWarehouse as w
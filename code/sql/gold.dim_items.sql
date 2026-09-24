CREATE OR ALTER VIEW gold.dim_items AS
select
ROW_NUMBER() OVER (ORDER BY i.PK_iwItems) as item_key,
i.PK_iwItems as item_id,
i.itemdesc as item_description,
i.itemgroup as item_group
from silver.iwItems as i
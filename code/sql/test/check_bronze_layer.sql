/*
==================
DATA CLEANSING
==================
*/

--check duplicate primary key
select 
PK_psPatRegisters,
count(PK_psPatRegisters) as counts
From bronze.psPatRegisters
group by PK_psPatRegisters
having count(PK_psPatRegisters) > 1

--check if there's null
select
*
from bronze.psPatRegisters
where FK_emdPatients is null


--check if the registry date and discharge date is greater than the current date
-- expectation: it should be lower or equal to current date
select 
*
from bronze.psPatRegisters
where registrydate > GETDATE() and dischdate > GETDATE()

--Data standardization
select
DISTINCT pattrantype
from bronze.psPatRegisters

select
DISTINCT registrystatus
from bronze.psPatRegisters

select
DISTINCT cancelflag
from bronze.psPatRegisters

----------------------

select 
DISTINCT itemgroup
From bronze.iwItems


-- Check if there is a null value
select 
*
From bronze.iwItems
where PK_iwItems is null 
or barcodeid is null 
or barcodeid = ''
or itemdesc is null
or itemgroup is null

-- Check if there is a duplicate value
select 
PK_iwItems,
count(PK_iwItems) as counts
from bronze.iwItems
group by PK_iwItems
having count(PK_iwItems) > 1

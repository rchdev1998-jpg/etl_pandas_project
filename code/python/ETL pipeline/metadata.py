
def tables_configuration():
    return {
        "iwItems": {
            "column_type": "nvarchar",
            "column_key": "PK_iwItems",
            "target_query": "select PK_iwItems, barcodeid, itemdesc, itemgroup from dbo.iwItems order by PK_iwItems",
            "bronze_query": "select PK_iwItems, barcodeid, itemdesc, itemgroup from bronze.iwItems order by PK_iwItems"
        },
        "mscWarehouse": {
            "column_type": "int",
            "column_key": "PK_mscWarehouse",
            "target_query": "select PK_mscWarehouse, description from dbo.mscWarehouse order by PK_mscWarehouse",
            "bronze_query": "select PK_mscWarehouse, description from bronze.mscWarehouse order by PK_mscWarehouse"
        },
        "psPatitem": {
            "column_type": "int",
            "column_key": "PK_psPatitem",
            "target_query": "select PK_psPatitem, FK_psPatRegisters, FK_emdPatients, FK_mscWarehouse, FK_iwItemsREN, renqty, renprice, rendate from dbo.psPatitem where rendate > '2020-01-01' and rendate < '2021-01-01' order by PK_psPatitem",
            "bronze_query": "select PK_psPatitem, FK_psPatRegisters, FK_emdPatients, FK_mscWarehouse, FK_iwItemsREN, renqty, renprice, rendate from bronze.psPatitem order by PK_psPatitem"
        },
        "psPatRegisters": {
            "column_type": "int",
            "column_key": "PK_psPatRegisters",
            "target_query": "select PK_psPatRegisters, FK_emdPatients, registrydate, dischdate, pattrantype, registrystatus, cancelflag from dbo.psPatRegisters where registrydate > '2020-01-01' and registrydate < '2021-01-01' order by PK_psPatRegisters",
            "bronze_query": "select PK_psPatRegisters, FK_emdPatients, registrydate, dischdate, pattrantype, registrystatus, cancelflag from bronze.psPatRegisters order by PK_psPatRegisters"
        },
        "psPersonaldata": {
            "column_type": "int",
            "column_key": "PK_psPersonalData",
            "target_query": "select PK_psPersonalData, firstname, gender, religion, nationality from dbo.psPersonaldata order by PK_psPersonalData",
            "bronze_query": "select PK_psPersonalData, firstname, gender, religion, nationality from bronze.psPersonaldata order by PK_psPersonalData"
        }
    }

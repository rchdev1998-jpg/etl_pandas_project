/*
=========================
CREATE DATABASE
=========================
*/

USE master
GO
CREATE DATABASE DATA_WAREHOUSE
GO

USE DATA_WAREHOUSE
go


/*
=========================
CREATE SCHEMA
=========================
*/
CREATE SCHEMA bronze
go

CREATE SCHEMA silver
go

CREATE SCHEMA gold
go


/*
=========================
CREATE DATABASE TABLES
=========================
*/
USE DATA_WAREHOUSE;
GO

IF OBJECT_ID('silver.psPatRegisters', 'U') IS NOT NULL
    DROP TABLE silver.psPatRegisters ;
GO

CREATE TABLE bronze.psPatRegisters (
	PK_psPatRegisters INT,
	FK_emdPatients INT,
	registrydate DATETIME,
	dischdate DATETIME,
	pattrantype NVARCHAR(50),
	registrystatus NVARCHAR(50),
	cancelflag BIT
);
GO

IF OBJECT_ID('silver.psPersonaldata', 'U') IS NOT NULL
    DROP TABLE silver.psPersonaldata ;
GO


CREATE TABLE bronze.psPersonaldata (
	PK_psPersonalData INT,
	firstname NVARCHAR(max),
	gender NVARCHAR(50),
	religion NVARCHAR(50),
	nationality NVARCHAR(50)
);
GO

IF OBJECT_ID('silver.psPatitem', 'U') IS NOT NULL
    DROP TABLE silver.psPatitem ;
GO

CREATE TABLE bronze.psPatitem (
	PK_psPatitem INT,
	FK_psPatRegisters INT,
	FK_emdPatients INT,
	FK_mscWarehouse INT,
	FK_iwItemsREN INT,
	renqty INT,
	renprice FLOAT,
	rendate DATETIME
);
GO

IF OBJECT_ID('silver.mscWarehouse', 'U') IS NOT NULL
    DROP TABLE silver.mscWarehouse ;
GO

CREATE TABLE bronze.mscWarehouse (
	PK_mscWarehouse INT,
	description NVARCHAR(max)
);
GO

IF OBJECT_ID('silver.iwItems', 'U') IS NOT NULL
    DROP TABLE silver.iwItems ;
GO

CREATE TABLE silver.iwItems (
	PK_iwItems NVARCHAR(50),
	itemdesc NVARCHAR(MAX),
	itemgroup NVARCHAR(50)
);
GO

--LOAD THE SILVER LAYER
USE DATA_WAREHOUSE;
GO

IF OBJECT_ID('silver.psPatRegisters', 'U') IS NOT NULL
    DROP TABLE silver.psPatRegisters ;
GO

CREATE TABLE silver.psPatRegisters (
	PK_psPatRegisters INT,
	FK_emdPatients INT,
	registrydate DATETIME,
	dischdate DATETIME,
	pattrantype NVARCHAR(50),
	registrystatus NVARCHAR(50),
	cancelflag BIT,
	dwh_date_created DATETIME2 DEFAULT GETDATE()
);
GO

IF OBJECT_ID('silver.psPersonaldata', 'U') IS NOT NULL
    DROP TABLE silver.psPersonaldata ;
GO

CREATE TABLE silver.psPersonaldata (
	PK_psPersonalData INT,
	firstname NVARCHAR(max),
	gender NVARCHAR(50),
	religion NVARCHAR(50),
	nationality NVARCHAR(50),
	dwh_date_created DATETIME2 DEFAULT GETDATE()
);
GO

IF OBJECT_ID('silver.psPatitem', 'U') IS NOT NULL
    DROP TABLE silver.psPatitem ;
GO

CREATE TABLE silver.psPatitem (
	PK_psPatitem INT,
	FK_psPatRegisters INT,
	FK_emdPatients INT,
	FK_mscWarehouse INT,
	FK_iwItemsREN INT,
	renqty INT,
	renprice FLOAT,
	rendate DATETIME,
	dwh_date_created DATETIME2 DEFAULT GETDATE()
);
GO

IF OBJECT_ID('silver.mscWarehouse', 'U') IS NOT NULL
    DROP TABLE silver.mscWarehouse ;
GO

CREATE TABLE silver.mscWarehouse (
	PK_mscWarehouse INT,
	description NVARCHAR(max),
	dwh_date_created DATETIME2 DEFAULT GETDATE()
);
GO

IF OBJECT_ID('silver.iwItems', 'U') IS NOT NULL
    DROP TABLE silver.iwItems ;
GO

CREATE TABLE silver.iwItems (
	PK_iwItems NVARCHAR(50),
	barcodeid NVARCHAR(50),
	itemdesc NVARCHAR(MAX),
	itemgroup NVARCHAR(10),
	dwh_date_created DATETIME2 DEFAULT GETDATE()
);
GO

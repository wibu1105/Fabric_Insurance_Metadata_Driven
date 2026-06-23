CREATE TABLE [audit].[audit_invalid_record] (

	[invalid_record_id] varchar(100) NULL, 
	[audit_table_session_id] varchar(100) NULL, 
	[layer_name] varchar(100) NULL, 
	[table_name] varchar(255) NULL, 
	[invalid_column] varchar(255) NULL, 
	[invalid_reason] varchar(1000) NULL, 
	[invalid_record_count] int NULL, 
	[record_payload] varchar(max) NULL, 
	[rejected_timestamp] datetime2(0) NULL
);
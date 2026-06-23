CREATE TABLE [audit].[audit_table_session_log] (

	[audit_table_session_id] varchar(100) NULL, 
	[audit_session_id] varchar(100) NULL, 
	[table_id] int NULL, 
	[layer_name] varchar(100) NULL, 
	[load_type] varchar(50) NULL, 
	[status] varchar(50) NULL, 
	[start_time] datetime2(0) NULL, 
	[end_time] datetime2(0) NULL, 
	[processed_rows] int NULL, 
	[created_at] datetime2(0) NULL, 
	[updated_at] datetime2(0) NULL
);
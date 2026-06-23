CREATE TABLE [audit].[audit_batch_log] (

	[audit_batch_id] varchar(100) NULL, 
	[batch_name] varchar(255) NULL, 
	[triggered_by] varchar(255) NULL, 
	[batch_status] varchar(50) NULL, 
	[session_start] datetime2(0) NULL, 
	[session_end] datetime2(0) NULL
);
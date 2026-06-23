CREATE TABLE [audit].[audit_error_log] (

	[audit_error_id] varchar(100) NULL, 
	[audit_table_session_id] varchar(100) NULL, 
	[step_name] varchar(255) NULL, 
	[error_code] varchar(100) NULL, 
	[error_name] varchar(max) NULL, 
	[error_time] datetime2(0) NULL
);
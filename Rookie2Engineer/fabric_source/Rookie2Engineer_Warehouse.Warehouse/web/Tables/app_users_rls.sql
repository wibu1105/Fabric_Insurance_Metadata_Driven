CREATE TABLE [web].[app_users_rls] (

	[user_mail] varchar(50) NOT NULL, 
	[password] varchar(100) NOT NULL, 
	[rls_level] int NOT NULL, 
	[access_value] varchar(50) NULL
);
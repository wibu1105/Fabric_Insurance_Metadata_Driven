CREATE TABLE [dbo].[customers] (
    [customer_id]  VARCHAR (20)   NOT NULL,
    [full_name]    NVARCHAR (200) NULL,
    [gender]       VARCHAR (10)   NULL,
    [dob]          DATE           NULL,
    [phone_number] VARCHAR (20)   NULL,
    [email]        VARCHAR (200)  NULL,
    [city]         NVARCHAR (100) NULL,
    [district]     NVARCHAR (100) NULL,
    [created_date] DATETIME       NULL,
    PRIMARY KEY CLUSTERED ([customer_id] ASC)
);


GO


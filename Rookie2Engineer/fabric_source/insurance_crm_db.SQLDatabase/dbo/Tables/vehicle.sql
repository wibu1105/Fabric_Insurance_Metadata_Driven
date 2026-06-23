CREATE TABLE [dbo].[vehicle] (
    [vehicle_id]       VARCHAR (20)    NOT NULL,
    [customer_id]      VARCHAR (20)    NULL,
    [plate_number]     VARCHAR (20)    NULL,
    [vehicle_brand]    NVARCHAR (100)  NULL,
    [vehicle_model]    NVARCHAR (100)  NULL,
    [manufacture_year] INT             NULL,
    [vehicle_value]    DECIMAL (18, 2) NULL,
    PRIMARY KEY CLUSTERED ([vehicle_id] ASC),
    CONSTRAINT [fk_vehicle_customer] FOREIGN KEY ([customer_id]) REFERENCES [dbo].[customers] ([customer_id])
);


GO


CREATE TABLE [dbo].[quotation_item] (
    [quotation_item_id] VARCHAR (20)    NOT NULL,
    [quotation_id]      VARCHAR (20)    NULL,
    [coverage_type]     NVARCHAR (100)  NULL,
    [coverage_amount]   DECIMAL (18, 2) NULL,
    [deductible_amount] DECIMAL (18, 2) NULL,
    PRIMARY KEY CLUSTERED ([quotation_item_id] ASC),
    CONSTRAINT [fk_quotation_item] FOREIGN KEY ([quotation_id]) REFERENCES [dbo].[quotation] ([quotation_id])
);


GO


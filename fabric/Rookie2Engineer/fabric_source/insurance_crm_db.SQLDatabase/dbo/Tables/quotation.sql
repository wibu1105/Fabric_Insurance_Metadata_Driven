CREATE TABLE [dbo].[quotation] (
    [quotation_id]          VARCHAR (20)    NOT NULL,
    [customer_id]           VARCHAR (20)    NULL,
    [agent_id]              VARCHAR (20)    NULL,
    [provider_code]         VARCHAR (20)    NULL,
    [quotation_date]        DATETIME        NULL,
    [quotation_status]      VARCHAR (50)    NULL,
    [package_code]          VARCHAR (50)    NULL,
    [premium_amount]        DECIMAL (18, 2) NULL,
    [quotation_expiry_date] DATETIME        NULL,
    PRIMARY KEY CLUSTERED ([quotation_id] ASC),
    CONSTRAINT [fk_quotation_agent] FOREIGN KEY ([agent_id]) REFERENCES [dbo].[agents] ([agent_id]),
    CONSTRAINT [fk_quotation_customer] FOREIGN KEY ([customer_id]) REFERENCES [dbo].[customers] ([customer_id]),
    CONSTRAINT [fk_quotation_provider] FOREIGN KEY ([provider_code]) REFERENCES [dbo].[insurance_providers] ([provider_code])
);


GO


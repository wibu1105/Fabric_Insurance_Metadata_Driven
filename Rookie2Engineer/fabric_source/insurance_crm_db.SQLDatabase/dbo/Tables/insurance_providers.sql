CREATE TABLE [dbo].[insurance_providers] (
    [provider_code]  VARCHAR (20)   NOT NULL,
    [provider_name]  NVARCHAR (200) NULL,
    [provider_group] NVARCHAR (100) NULL,
    [active_flag]    INT            NULL,
    PRIMARY KEY CLUSTERED ([provider_code] ASC)
);


GO


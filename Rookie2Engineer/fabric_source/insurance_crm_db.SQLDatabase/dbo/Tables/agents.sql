CREATE TABLE [dbo].[agents] (
    [agent_id]     VARCHAR (20)   NOT NULL,
    [agent_name]   NVARCHAR (200) NULL,
    [region]       NVARCHAR (100) NULL,
    [branch]       NVARCHAR (100) NULL,
    [manager_name] NVARCHAR (200) NULL,
    [created_date] DATETIME       NULL,
    PRIMARY KEY CLUSTERED ([agent_id] ASC)
);


GO


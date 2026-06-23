CREATE DATABASE insurance_crm_db;
GO

USE insurance_crm_db;
GO
-- =========================================
-- CUSTOMERS
-- =========================================
CREATE TABLE customers (
    customer_id         VARCHAR(20) PRIMARY KEY,
    full_name           NVARCHAR(200),
    gender              VARCHAR(10),
    dob                 DATE,
    phone_number        VARCHAR(20),
    email               VARCHAR(200),
    city                NVARCHAR(100),
    district            NVARCHAR(100),
    created_date        DATETIME
);
-- =========================================
-- AGENTS
-- =========================================
CREATE TABLE agents (
    agent_id            VARCHAR(20) PRIMARY KEY,
    agent_name          NVARCHAR(200),
    region              NVARCHAR(100),
    branch              NVARCHAR(100),
    manager_name        NVARCHAR(200),
    created_date        DATETIME
);

-- =========================================
-- INSURANCE PROVIDERS
-- =========================================
CREATE TABLE insurance_providers (
    provider_code       VARCHAR(20) PRIMARY KEY,
    provider_name       NVARCHAR(200),
    provider_group      NVARCHAR(100),
    active_flag         INT
);

-- =========================================
-- VEHICLE
-- =========================================
CREATE TABLE vehicle (
    vehicle_id          VARCHAR(20) PRIMARY KEY,
    customer_id         VARCHAR(20),
    plate_number        VARCHAR(20),
    vehicle_brand       NVARCHAR(100),
    vehicle_model       NVARCHAR(100),
    manufacture_year    INT,
    vehicle_value       DECIMAL(18,2),

    CONSTRAINT fk_vehicle_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id)
);

-- =========================================
-- QUOTATION
-- =========================================
CREATE TABLE quotation (
    quotation_id            VARCHAR(20) PRIMARY KEY,
    customer_id             VARCHAR(20),
    agent_id                VARCHAR(20),
    provider_code           VARCHAR(20),
    quotation_date          DATETIME,
    quotation_status        VARCHAR(50),
    package_code            VARCHAR(50),
    premium_amount          DECIMAL(18,2),
    quotation_expiry_date   DATETIME,

    CONSTRAINT fk_quotation_customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(customer_id),

    CONSTRAINT fk_quotation_agent
        FOREIGN KEY (agent_id)
        REFERENCES agents(agent_id),

    CONSTRAINT fk_quotation_provider
        FOREIGN KEY (provider_code)
        REFERENCES insurance_providers(provider_code)
);

-- =========================================
-- QUOTATION ITEM
-- =========================================
CREATE TABLE quotation_item (
    quotation_item_id       VARCHAR(20) PRIMARY KEY,
    quotation_id            VARCHAR(20),
    coverage_type           NVARCHAR(100),
    coverage_amount         DECIMAL(18,2),
    deductible_amount       DECIMAL(18,2),

    CONSTRAINT fk_quotation_item
        FOREIGN KEY (quotation_id)
        REFERENCES quotation(quotation_id)
);

USE insurance_crm_db;
GO

-- =========================================
-- INSURANCE PROVIDERS
-- =========================================
INSERT INTO insurance_providers VALUES
('BV', 'Bao Viet', 'Domestic', 1),
('PVI', 'PVI Insurance', 'Domestic', 1),
('PTI', 'PTI Insurance', 'Domestic', 1),
('MIC', 'MIC Insurance', 'Domestic', 1),
('LIB', 'Liberty Insurance', 'International', 1),
('BIC', 'BIC Insurance', 'Domestic', 1);

-- =========================================
-- AGENTS
-- =========================================
INSERT INTO agents VALUES
('AG001', 'Nguyen Van An', 'North', 'Ha Noi', 'Tran Minh', GETDATE()),
('AG002', 'Tran Thi Hoa', 'South', 'HCM', 'Le Anh', GETDATE()),
('AG003', 'Pham Minh Duc', 'Central', 'Da Nang', 'Nguyen Long', GETDATE()),
('AG004', 'Le Thi Mai', 'South', 'Can Tho', 'Le Anh', GETDATE());

-- Generate Initial Data for 3 Years
USE insurance_crm_db;
GO

DECLARE @i INT = 1;

WHILE @i <= 1000
BEGIN

    INSERT INTO customers
    VALUES (
        CONCAT('CUS', RIGHT('0000' + CAST(@i AS VARCHAR), 4)),
        CONCAT('Customer ', @i),
        CASE WHEN @i % 2 = 0 THEN 'Male' ELSE 'Female' END,
        DATEADD(DAY, -(@i * 30), '1995-01-01'),
        CONCAT('090', RIGHT('0000000' + CAST(@i AS VARCHAR), 7)),
        CONCAT('customer', @i, '@mail.com'),
        CASE WHEN @i % 3 = 0 THEN 'Ha Noi'
             WHEN @i % 3 = 1 THEN 'Ho Chi Minh'
             ELSE 'Da Nang' END,
        'District 1',
        DATEADD(DAY, -@i, GETDATE())
    );

    INSERT INTO vehicle
    VALUES (
        CONCAT('VEH', RIGHT('0000' + CAST(@i AS VARCHAR), 4)),
        CONCAT('CUS', RIGHT('0000' + CAST(@i AS VARCHAR), 4)),
        CONCAT('51A-', RIGHT('00000' + CAST(@i AS VARCHAR), 5)),
        CASE WHEN @i % 4 = 0 THEN 'Toyota'
             WHEN @i % 4 = 1 THEN 'Hyundai'
             WHEN @i % 4 = 2 THEN 'Mazda'
             ELSE 'VinFast' END,
        'Model X',
        2020 + (@i % 5),
        500000000 + (@i * 100000)
    );

    INSERT INTO quotation
    VALUES (
        CONCAT('QUO', RIGHT('00000' + CAST(@i AS VARCHAR), 5)),
        CONCAT('CUS', RIGHT('0000' + CAST(@i AS VARCHAR), 4)),
        CASE WHEN @i % 4 = 0 THEN 'AG001'
             WHEN @i % 4 = 1 THEN 'AG002'
             WHEN @i % 4 = 2 THEN 'AG003'
             ELSE 'AG004' END,
        CASE WHEN @i % 5 = 0 THEN 'BV'
             WHEN @i % 5 = 1 THEN 'PVI'
             WHEN @i % 5 = 2 THEN 'PTI'
             WHEN @i % 5 = 3 THEN 'MIC'
             ELSE 'LIB' END,
        DATEADD(DAY, -(@i % 1095), GETDATE()),
        CASE WHEN @i % 5 = 0 THEN 'CONVERTED'
             WHEN @i % 5 = 1 THEN 'ACCEPTED'
             WHEN @i % 5 = 2 THEN 'REJECTED'
             WHEN @i % 5 = 3 THEN 'EXPIRED'
             ELSE 'QUOTED' END,
        CASE WHEN @i % 4 = 0 THEN 'BASIC'
             WHEN @i % 4 = 1 THEN 'STANDARD'
             WHEN @i % 4 = 2 THEN 'PREMIUM'
             ELSE 'VIP' END,
        5000000 + (@i * 10000),
        DATEADD(DAY, 30, GETDATE())
    );

    INSERT INTO quotation_item
    VALUES (
        CONCAT('QI', RIGHT('00000' + CAST(@i AS VARCHAR), 5)),
        CONCAT('QUO', RIGHT('00000' + CAST(@i AS VARCHAR), 5)),
        'Physical Damage',
        100000000,
        1000000
    );

    SET @i = @i + 1;
END;


CREATE DATABASE insurance_policy_db;
GO

USE insurance_policy_db;
GO

-- =========================================
-- POLICY
-- =========================================
CREATE TABLE policy_info (
    policy_id               VARCHAR(20) PRIMARY KEY,
    quotation_id            VARCHAR(20),
    customer_id             VARCHAR(20),
    provider_code           VARCHAR(20),
    policy_number           VARCHAR(50),
    policy_start_date       DATE,
    policy_end_date         DATE,
    policy_status           VARCHAR(50),
    premium_amount          DECIMAL(18,2),
    issued_date             DATETIME
);

-- =========================================
-- PAYMENT
-- =========================================
CREATE TABLE payment (
    payment_id              VARCHAR(20) PRIMARY KEY,
    policy_id               VARCHAR(20),
    payment_date            DATETIME,
    payment_method          VARCHAR(50),
    payment_status          VARCHAR(50),
    payment_amount          DECIMAL(18,2),
    transaction_reference   VARCHAR(100),

    CONSTRAINT fk_payment_policy
        FOREIGN KEY (policy_id)
        REFERENCES policy_info(policy_id)
);

-- =========================================
-- CANCELLATION
-- =========================================
CREATE TABLE cancellation (
    cancellation_id         VARCHAR(20) PRIMARY KEY,
    policy_id               VARCHAR(20),
    cancellation_date       DATETIME,
    cancellation_reason     NVARCHAR(200),
    refund_amount           DECIMAL(18,2),

    CONSTRAINT fk_cancel_policy
        FOREIGN KEY (policy_id)
        REFERENCES policy_info(policy_id)
);

USE insurance_policy_db;
GO

DECLARE @i INT = 1;

WHILE @i <= 600
BEGIN

    INSERT INTO policy_info
    VALUES (
        CONCAT('POL', RIGHT('00000' + CAST(@i AS VARCHAR), 5)),
        CONCAT('QUO', RIGHT('00000' + CAST(@i AS VARCHAR), 5)),
        CONCAT('CUS', RIGHT('0000' + CAST(@i AS VARCHAR), 4)),
        CASE WHEN @i % 5 = 0 THEN 'BV'
             WHEN @i % 5 = 1 THEN 'PVI'
             WHEN @i % 5 = 2 THEN 'PTI'
             WHEN @i % 5 = 3 THEN 'MIC'
             ELSE 'LIB' END,
        CONCAT('POLNO-', @i),
        DATEADD(DAY, -(@i % 1095), GETDATE()),
        DATEADD(YEAR, 1, DATEADD(DAY, -(@i % 1095), GETDATE())),
        CASE WHEN @i % 4 = 0 THEN 'ACTIVE'
             WHEN @i % 4 = 1 THEN 'EXPIRED'
             WHEN @i % 4 = 2 THEN 'CANCELLED'
             ELSE 'ISSUED' END,
        6000000 + (@i * 15000),
        DATEADD(DAY, -(@i % 1095), GETDATE())
    );

    INSERT INTO payment
    VALUES (
        CONCAT('PAY', RIGHT('00000' + CAST(@i AS VARCHAR), 5)),
        CONCAT('POL', RIGHT('00000' + CAST(@i AS VARCHAR), 5)),
        DATEADD(DAY, -(@i % 1095), GETDATE()),
        CASE WHEN @i % 3 = 0 THEN 'Bank Transfer'
             WHEN @i % 3 = 1 THEN 'Credit Card'
             ELSE 'E-wallet' END,
        CASE WHEN @i % 4 = 0 THEN 'PAID'
             WHEN @i % 4 = 1 THEN 'FAILED'
             WHEN @i % 4 = 2 THEN 'PENDING'
             ELSE 'REFUNDED' END,
        6000000 + (@i * 15000),
        CONCAT('TXN', @i)
    );

    IF @i % 10 = 0
    BEGIN
        INSERT INTO cancellation
        VALUES (
            CONCAT('CAN', RIGHT('00000' + CAST(@i AS VARCHAR), 5)),
            CONCAT('POL', RIGHT('00000' + CAST(@i AS VARCHAR), 5)),
            GETDATE(),
            'Customer Request',
            1000000
        );
    END

    SET @i = @i + 1;
END;
-- =========================================
-- Contract Tool - Azure SQL Tables
-- =========================================

-- 1) CREATED
IF OBJECT_ID('dbo.CreatedContracts', 'U') IS NOT NULL
  DROP TABLE dbo.CreatedContracts;
GO

CREATE TABLE dbo.CreatedContracts (
  Id               INT IDENTITY(1,1) PRIMARY KEY,
  ContractId       UNIQUEIDENTIFIER NOT NULL,
  ProcessInstanceId NVARCHAR(64) NULL,
  BusinessKey      NVARCHAR(255) NULL,

  ContractTitle    NVARCHAR(255) NULL,
  ContractType     NVARCHAR(255) NULL,
  Roles            NVARCHAR(MAX) NULL,
  Skills           NVARCHAR(MAX) NULL,
  RequestType      NVARCHAR(255) NULL,
  Budget           FLOAT NULL,
  ContractStartDate NVARCHAR(50) NULL,
  ContractEndDate   NVARCHAR(50) NULL,
  Description      NVARCHAR(MAX) NULL,

  CreatedAt        DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE UNIQUE INDEX UX_CreatedContracts_ContractId ON dbo.CreatedContracts(ContractId);
GO


-- 2) APPROVED
IF OBJECT_ID('dbo.ApprovedContracts', 'U') IS NOT NULL
  DROP TABLE dbo.ApprovedContracts;
GO

CREATE TABLE dbo.ApprovedContracts (
  Id               INT IDENTITY(1,1) PRIMARY KEY,
  ContractId       UNIQUEIDENTIFIER NOT NULL,
  ProcessInstanceId NVARCHAR(64) NULL,
  BusinessKey      NVARCHAR(255) NULL,

  ContractTitle    NVARCHAR(255) NULL,
  ContractType     NVARCHAR(255) NULL,

  StorageLocation  NVARCHAR(255) NULL,
  VersionNumber    NVARCHAR(100) NULL,
  SignedDate       NVARCHAR(50) NULL,

  ApprovedAt       DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE UNIQUE INDEX UX_ApprovedContracts_ContractId ON dbo.ApprovedContracts(ContractId);
GO


-- 3) REJECTED
IF OBJECT_ID('dbo.RejectedContracts', 'U') IS NOT NULL
  DROP TABLE dbo.RejectedContracts;
GO

CREATE TABLE dbo.RejectedContracts (
  Id               INT IDENTITY(1,1) PRIMARY KEY,
  ContractId       UNIQUEIDENTIFIER NOT NULL,
  ProcessInstanceId NVARCHAR(64) NULL,
  BusinessKey      NVARCHAR(255) NULL,

  ContractTitle    NVARCHAR(255) NULL,
  LegalComment     NVARCHAR(MAX) NULL,
  ApprovalDecision NVARCHAR(50) NULL,

  RejectedAt       DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE UNIQUE INDEX UX_RejectedContracts_ContractId ON dbo.RejectedContracts(ContractId);
GO

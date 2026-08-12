-- Create database and sample tables matching the nested GridView scenario
IF DB_ID(N'AspGridDemo') IS NULL
BEGIN
    CREATE DATABASE AspGridDemo;
END
GO

USE AspGridDemo;
GO

IF OBJECT_ID(N'dbo.Loans', 'U') IS NOT NULL DROP TABLE dbo.Loans;
IF OBJECT_ID(N'dbo.Trusts', 'U') IS NOT NULL DROP TABLE dbo.Trusts;
GO

CREATE TABLE dbo.Trusts
(
    Id INT IDENTITY(1,1) PRIMARY KEY,
    EntryType NVARCHAR(50) NOT NULL,
    GLAcct NVARCHAR(50) NOT NULL
);

CREATE TABLE dbo.Loans
(
    Id INT IDENTITY(1,1) PRIMARY KEY,
    TrustId INT NOT NULL,
    CheckNo NVARCHAR(50) NOT NULL,
    CheckMemo NVARCHAR(100) NULL,
    LoanCode NVARCHAR(50) NOT NULL,
    GLAcct NVARCHAR(50) NOT NULL,
    Amount DECIMAL(18,2) NOT NULL CONSTRAINT DF_Loans_Amount DEFAULT(0),
    CONSTRAINT FK_Loans_Trusts FOREIGN KEY(TrustId) REFERENCES dbo.Trusts(Id)
);

-- Seed parent Trusts
INSERT INTO dbo.Trusts(EntryType, GLAcct) VALUES
(N'Credit', N'1000-A'),
(N'Debit',  N'2000-B'),
(N'Credit', N'3000-C');

-- Seed some child Loans
INSERT INTO dbo.Loans(TrustId, CheckNo, CheckMemo, LoanCode, GLAcct, Amount) VALUES
(1, N'CHK10001', N'Office Supplies', N'LN101', N'1000-A', 120.00),
(1, N'CHK10002', N'IT Hardware',     N'LN102', N'1000-A', 350.50),
(2, N'CHK20001', N'Transport',       N'LN201', N'2000-B', 95.75);

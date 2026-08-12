# ASP.NET WebForms — Nested GridView Insert (No Full Page Refresh)

Matches the ASPSnippets requirement: parent GridView with nested (child) GridView where you can **insert a child row without full page refresh** (uses UpdatePanel for async postback). Includes **sample SQL** and **ready-to-run WebForms** page.

**Keyword:** asp.netexperthere

## What’s inside
- `Default.aspx` / `Default.aspx.cs` — parent `gvTrust` + child `gvLoan` with expand/collapse and footer **Add**.
- `App_Code/Db.cs` — tiny ADO.NET helper.
- `Web.config` — connection strings for **LocalDB** (default) and **Azure SQL** (commented).
- `SQL/create_db.sql` — creates `AspGridDemo` DB with `Trusts` (parent) and `Loans` (child) + seed data.
- `images/plus.png`, `images/minus.png` — icons for expand/collapse.

## Run (Visual Studio 2019/2022, IIS Express)
1. Execute `SQL/create_db.sql` on your SQL Server or Azure SQL.
2. Open this folder as a **Web Site** in Visual Studio: `File → Open → Web Site...`
3. Update `Web.config` → `DefaultConnection` (LocalDB by default). For Azure, replace with your server / user / password.
4. Right-click `Default.aspx` → **Set as Start Page** → press **F5**.
5. Click **+** to expand a Trust and see its Loans. Use the footer to add a Loan → only the child grid updates (no full refresh).

## Azure connection string sample
```
<add name="DefaultConnection"
     connectionString="Server=tcp:yourserver.database.windows.net,1433;
     Initial Catalog=AspGridDemo;
     Persist Security Info=False;
     User ID=youruser;
     Password=yourpassword;
     MultipleActiveResultSets=False;
     Encrypt=True;
     TrustServerCertificate=False;
     Connection Timeout=30;"
     providerName="System.Data.SqlClient" />
```

## Notes
- Target Framework: .NET Framework 4.7.2+ (works on 4.5–4.8).
- No third-party packages; pure WebForms + ASP.NET AJAX (UpdatePanel).
- If you prefer to avoid UpdatePanel, you can switch to a `PageMethods` / WebMethod + jQuery AJAX — ask and I’ll add that variant.

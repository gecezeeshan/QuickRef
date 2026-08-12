using System;
using System.Data;
using System.Data.SqlClient;
using System.Globalization;
using System.Web.UI;
using System.Web.UI.WebControls;

public partial class _Default : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {
        if (!IsPostBack)
        {
            BindTrusts();
        }
    }

    private void BindTrusts()
    {
        string sql = "SELECT Id, EntryType, GLAcct FROM Trusts ORDER BY Id";
        gvTrust.DataSource = Db.Query(sql);
        gvTrust.DataBind();
    }

    protected void gvTrust_RowDataBound(object sender, GridViewRowEventArgs e)
    {
        if (e.Row.RowType == DataControlRowType.DataRow)
        {
            DataRowView drv = (DataRowView)e.Row.DataItem;
            int trustId = Convert.ToInt32(drv["Id"]);

            // Find the child grid inside the UpdatePanel content
            var gvLoan = (GridView)e.Row.FindControl("gvLoan");
            if (gvLoan != null)
            {
                BindLoansGrid(gvLoan, trustId);
            }
        }
    }

    private void BindLoansGrid(GridView gvLoan, int trustId)
    {
        string sql = @"SELECT Id, TrustId, CheckNo, CheckMemo, LoanCode, GLAcct, Amount
                       FROM Loans WHERE TrustId=@tid ORDER BY Id";
        gvLoan.DataSource = Db.Query(sql, new SqlParameter("@tid", trustId));
        gvLoan.DataBind();
    }

    protected void gvLoan_RowCommand(object sender, GridViewCommandEventArgs e)
    {
        if (e.CommandName == "AddLoan")
        {
            var gvLoan = (GridView)sender;
            var container = (Control)gvLoan.NamingContainer;

            // Get parent TrustId from hidden field
            var hf = (HiddenField)container.FindControl("hfTrustId");
            int trustId = int.Parse(hf.Value);

            // Footer controls
            var footer = gvLoan.FooterRow;
            var txtCheckMemo = (TextBox)footer.FindControl("txtCheckMemo");
            var txtGLAcct = (TextBox)footer.FindControl("txtGLAcct");
            var txtAmount = (TextBox)footer.FindControl("txtAmount");

            // Minimal validation
            string checkMemo = (txtCheckMemo.Text ?? "").Trim();
            string glAcct = (txtGLAcct.Text ?? "").Trim();
            decimal amount = 0m;
            decimal.TryParse((txtAmount.Text ?? "0").Trim(), NumberStyles.Any, CultureInfo.InvariantCulture, out amount);

            // Insert new row
            string insert = @"INSERT INTO Loans(TrustId, CheckNo, CheckMemo, LoanCode, GLAcct, Amount)
                              VALUES(@tid, @checkNo, @checkMemo, @loanCode, @gl, @amt);";
            Db.Execute(insert,
                new SqlParameter("@tid", trustId),
                new SqlParameter("@checkNo", Guid.NewGuid().ToString("N").Substring(0, 8)), // sample
                new SqlParameter("@checkMemo", checkMemo),
                new SqlParameter("@loanCode", "LN" + DateTime.UtcNow.Ticks % 1000),
                new SqlParameter("@gl", glAcct),
                new SqlParameter("@amt", amount));

            // Rebind only this child grid
            BindLoansGrid(gvLoan, trustId);
        }
    }
}

<%@ Page Language="C#" AutoEventWireup="true" CodeFile="Default.aspx.cs" Inherits="_Default" %>
<!DOCTYPE html>
<html>
<head runat="server">
    <title>Nested GridView Insert without Full Page Refresh</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 24px; }
        .tbl { width: 98%; margin: 0 auto; }
        .child-wrap { margin: 12px 0 24px 24px; }
        .footer-input { width: 160px; }
        .toggle { cursor: pointer; vertical-align: middle; margin-right: 6px; }
        .note { color: #666; font-size: 12px; }
    </style>
    <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
    <script type="text/javascript">
        // Expand / Collapse cloned child grid within a new row (like ASPSnippets pattern)
        $(document).on("click", "img.toggle", function () {
            var $img = $(this);
            if ($img.attr("src").indexOf("plus.png") >= 0) {
                var $panel = $img.closest("tr").find("div[data-child='panel']").first();
                $img.closest("tr").after("<tr class='child-row'><td></td><td colspan='999'>" + $panel.html() + "</td></tr>");
                $img.attr("src", "images/minus.png");
            } else {
                $img.attr("src", "images/plus.png");
                $img.closest("tr").next(".child-row").remove();
            }
        });
    </script>
</head>
<body>
    <form id="form1" runat="server">
        <asp:ScriptManager ID="ScriptManager1" runat="server" />
        <h2>Trusts → Loans</h2>
        <p class="note">
            Insert into the child GridView footer. Only the child UpdatePanel refreshes (no full page reload).<br />
            Keyword for bid: <strong>asp.netexperthere</strong>
        </p>

        <asp:GridView ID="gvTrust" runat="server" CssClass="tbl" AutoGenerateColumns="false" OnRowDataBound="gvTrust_RowDataBound">
            <Columns>
                <asp:TemplateField>
                    <ItemTemplate>
                        <img class="toggle" alt="toggle" src="images/plus.png" />
                        <div data-child="panel" style="display:none">
                            <!-- Child Grid lives inside an UpdatePanel so only it refreshes on insert -->
                            <asp:UpdatePanel ID="upChild" runat="server" UpdateMode="Conditional">
                                <ContentTemplate>
                                    <div class="child-wrap">
                                        <asp:GridView ID="gvLoan" runat="server" AutoGenerateColumns="false" ShowFooter="true"
                                            CssClass="tbl"
                                            OnRowCommand="gvLoan_RowCommand">
                                            <Columns>
                                                <asp:BoundField DataField="Id" HeaderText="Loan ID" />
                                                <asp:BoundField DataField="CheckNo" HeaderText="Check No" />
                                                <asp:TemplateField HeaderText="Check Memo">
                                                    <ItemTemplate>
                                                        <asp:Label ID="lblCheckMemo" runat="server" Text='<%# Eval("CheckMemo") %>'></asp:Label>
                                                    </ItemTemplate>
                                                    <FooterTemplate>
                                                        <asp:TextBox ID="txtCheckMemo" runat="server" CssClass="footer-input" Placeholder="Check Memo"></asp:TextBox>
                                                    </FooterTemplate>
                                                </asp:TemplateField>
                                                <asp:BoundField DataField="LoanCode" HeaderText="Loan Code" />
                                                <asp:TemplateField HeaderText="GL Account">
                                                    <ItemTemplate>
                                                        <asp:Label ID="lblGLAcct" runat="server" Text='<%# Eval("GLAcct") %>'></asp:Label>
                                                    </ItemTemplate>
                                                    <FooterTemplate>
                                                        <asp:TextBox ID="txtGLAcct" runat="server" CssClass="footer-input" Placeholder="GL Acct"></asp:TextBox>
                                                    </FooterTemplate>
                                                </asp:TemplateField>
                                                <asp:TemplateField HeaderText="Amount">
                                                    <ItemTemplate>
                                                        <asp:Label ID="lblAmount" runat="server" Text='<%# String.Format("{0:N2}", Eval("Amount")) %>'></asp:Label>
                                                    </ItemTemplate>
                                                    <FooterTemplate>
                                                        <asp:TextBox ID="txtAmount" runat="server" CssClass="footer-input" Placeholder="Amount"></asp:TextBox>
                                                    </FooterTemplate>
                                                </asp:TemplateField>
                                                <asp:TemplateField HeaderText="">
                                                    <FooterTemplate>
                                                        <asp:Button ID="btnAdd" runat="server" Text="Add" CommandName="AddLoan" />
                                                    </FooterTemplate>
                                                </asp:TemplateField>
                                            </Columns>
                                        </asp:GridView>
                                        <!-- Holds parent TrustId for this child instance -->
                                        <asp:HiddenField ID="hfTrustId" runat="server" Value='<%# Eval("Id") %>' />
                                    </div>
                                </ContentTemplate>
                                <Triggers>
                                    <asp:AsyncPostBackTrigger ControlID="gvLoan" EventName="RowCommand" />
                                </Triggers>
                            </asp:UpdatePanel>
                        </div>
                    </ItemTemplate>
                </asp:TemplateField>
                <asp:BoundField DataField="Id" HeaderText="Trust ID" />
                <asp:BoundField DataField="EntryType" HeaderText="Entry Type" />
                <asp:BoundField DataField="GLAcct" HeaderText="GL Account" />
            </Columns>
        </asp:GridView>
    </form>
</body>
</html>

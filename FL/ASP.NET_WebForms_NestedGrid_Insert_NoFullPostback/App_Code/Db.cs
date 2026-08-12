using System;
using System.Configuration;
using System.Data;
using System.Data.SqlClient;

public static class Db
{
    private static string ConnStr => ConfigurationManager.ConnectionStrings["DefaultConnection"].ConnectionString;

    public static DataTable Query(string sql, params SqlParameter[] parameters)
    {
        using (var con = new SqlConnection(ConnStr))
        using (var cmd = new SqlCommand(sql, con))
        using (var da = new SqlDataAdapter(cmd))
        {
            if (parameters != null && parameters.Length > 0)
                cmd.Parameters.AddRange(parameters);
            var dt = new DataTable();
            con.Open();
            da.Fill(dt);
            return dt;
        }
    }

    public static int Execute(string sql, params SqlParameter[] parameters)
    {
        using (var con = new SqlConnection(ConnStr))
        using (var cmd = new SqlCommand(sql, con))
        {
            if (parameters != null && parameters.Length > 0)
                cmd.Parameters.AddRange(parameters);
            con.Open();
            return cmd.ExecuteNonQuery();
        }
    }
}

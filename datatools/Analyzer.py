db_con = DatabaseConnector(scope="deezer.com")

df = pd.read_sql_table("url_input_table" , db_con.dbe)

hash_df = df["url"].str.extract(r'([0-9a-f]{5,})').fillna(0)
df["hashes"] = hash_df
df["hashes_len"] = df["hashes"].str.len()


for x in df["hashes_len"].value_counts().iteritems():
    if (df_size/x[1])/df_size < 0.0001:
        df[f"hash_start"] = df[df["hashes_len"] == x[0]].apply(lambda row: row["url"].find(row["hashes"]), axis=1)
        df[f"hash_end"] = df[df["hashes_len"] == x[0]].apply(lambda row: (row[f"hash_start"] + row["hashes_len"]) if row[f"hash_start"] else None, axis=1)

for x in df["hash_start"].value_counts().index[1:]:
    df["url_cut"] = df[df["hash_start"] == x].apply(lambda x: 
            "".join([x["url"][:int(x["hash_start"])],x["url"][int(x["hash_end"]):]]), axis=1)
    df = df[(~df['url_cut'].duplicated()) | (df['url_cut'].isnull())]
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns

# Style plus agréable visuellement
sns.set_style("whitegrid")

# Connexion à SQL Server 
engine = create_engine(
    "mssql+pyodbc://@DESKTOP-K7F98AH/AdventureWorksDW2016_EXT?"
    "driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)

print("Connexion OK")

#  SELECT * FROM DimProduct
df_produits = pd.read_sql("SELECT * FROM DimProduct", engine)

print(df_produits.head())        # affiche les 5 premières lignes     
print(df_produits.shape)         # (nombre de lignes, nombre de colonnes)

# SELECT EnglishProductName, ListPrice, Color FROM DimProduct WHERE Color = 'Red'
df_rouge = pd.read_sql(
    "SELECT EnglishProductName, ListPrice, Color FROM DimProduct WHERE Color = 'Red'",
    engine
)
print(df_rouge)

# Compter combien de valeurs manquantes il y a par colonne
print(df_rouge.isna().sum())

# Retirer les lignes où ListPrice est NaN
df_rouge_sans_nan = df_rouge.dropna(subset=["ListPrice"])

# Ou remplacer les NaN par 0 (à utiliser avec prudence, ça peut fausser des moyennes)
df_rouge_rempli = df_rouge.fillna({"ListPrice": 0})

# Charge la table des ventes
df_ventes = pd.read_sql("SELECT * FROM FactInternetSales", engine)

# JOIN entre ventes et produits
df_join = df_ventes.merge(
    df_produits[["ProductKey", "EnglishProductName"]],
    on="ProductKey",
    how="inner"
)

# GROUP BY : total des ventes par produit
df_grouped = df_join.groupby("EnglishProductName").agg(
    TotalVentes=("SalesAmount", "sum"),
    NbCommandes=("SalesAmount", "count")
).reset_index().sort_values("TotalVentes", ascending=False)

print(df_grouped.head(10))

# Reprend df_grouped calculé précédemment (total des ventes par produit)
top10 = df_grouped.head(10)

plt.figure(figsize=(10, 6))
sns.barplot(data=top10, x="TotalVentes", y="EnglishProductName", palette="Blues_d")
plt.title("Top 10 des produits par montant total des ventes")
plt.xlabel("Total des ventes ($)")
plt.ylabel("Produit")
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 5))
sns.histplot(df_produits["ListPrice"].dropna(), bins=30, kde=True)
plt.title("Distribution des prix des produits")
plt.xlabel("Prix")
plt.show()

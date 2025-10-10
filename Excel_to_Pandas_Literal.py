import pandas as pd

def EXCEL_TO_PANDAS_LITERAL( df:pd.DataFrame ) -> pd.DataFrame:
    n_row, n_col = df.shape
    columns = df.columns
    L = len(columns)

    print('DF = pd.DataFrame({')
    for index, col in enumerate(columns):
        if index == (L-1):
            values = df[col].astype(str).apply(repr).tolist()
            print(f"    '{col}': [{', '.join(values)}]")
        else:
            values = df[col].astype(str).apply(repr).tolist()
            print(f"    '{col}': [{', '.join(values)}],")
    print('})')


DF = pd.DataFrame({
    'country': ['US', 'Spain', 'US', 'US', 'France'],
    'province': ['California', 'Northern Spain', 'California', 'Oregon', 'Provence'],
    'points': ['96', '96', '96', '96', '95'],
    'price': ['235.0', '110.0', '90.0', '65.0', '66.0'],
    'variety': ['Cabernet Sauvignon', 'Tinta de Toro', 'Sauvignon Blanc', 'Pinot Noir', 'Provence red blend']
})

EXCEL_TO_PANDAS_LITERAL( DF )

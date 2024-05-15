'''
The airPLS and WhittakerSmooth are a translation in python of the R source code of airPLS version 2.0
by Yizeng Liang and Zhang Zhimin - https://code.google.com/p/airpls
Reference:
Z.-M. Zhang, S. Chen, and Y.-Z. Liang, Baseline correction using adaptive iteratively reweighted penalized least squares. Analyst 135 (5), 1138-1146 (2010).
'''

import sqlite3
import pandas as pd
import os
from scipy.sparse import csc_matrix, eye, diags
from scipy.sparse.linalg import spsolve
import numpy as np


def WhittakerSmooth(x: list[float], w: np.ndarray[float], lambda_: int, differences: int = 1) -> np.ndarray:
    '''
    Penalized least squares algorithm for background fitting
    
    input
        x: input data (i.e. chromatogram of spectrum)
        w: binary masks (value of the mask is zero if a point belongs to peaks and one otherwise)
        lambda_: parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background
        differences: integer indicating the order of the difference of penalties
    
    output
        the fitted background vector
    '''
    X=np.matrix(x)
    m=X.size
    E=eye(m,format='csc')
    for i in range(differences):
        E=E[1:]-E[:-1] # numpy.diff() does not work with sparse matrix. This is a workaround.
    W=diags(w,0,shape=(m,m))
    A=csc_matrix(W+(lambda_*E.T*E))
    B=csc_matrix(W*X.T)
    background=spsolve(A,B)
    return np.array(background)


def airPLS(x: list[float], lambda_: int = 100, porder: int = 1, itermax: int = 15) -> np.ndarray:
    '''
    Adaptive iteratively reweighted penalized least squares for baseline fitting
    
    input
        x: input data (i.e. chromatogram of spectrum)
        lambda_: parameter that can be adjusted by user. The larger lambda is,  the smoother the resulting background, z
        porder: adaptive iteratively reweighted penalized least squares for baseline fitting
    
    output
        the fitted background vector
    '''
    m=x.shape[0]
    w=np.ones(m)
    for i in range(1,itermax+1):
        z=WhittakerSmooth(x,w,lambda_, porder)
        d=x-z
        dssn=np.abs(d[d<0].sum())
        if(dssn<0.001*(abs(x)).sum() or i==itermax):
            if(i==itermax): print('WARNING max iteration reached!')
            break
        w[d>=0]=0 # d>0 means that this point is part of a peak, so its weight is set to 0 in order to ignore it
        w[d<0]=np.exp(i*np.abs(d[d<0])/dssn)
        w[0]=np.exp(i*(d[d<0]).max()/dssn) 
        w[-1]=w[0]
    return z


def get_csv_data(csv_data_path: str) -> dict[str, pd.DataFrame]:
    df_dict: dict[str, pd.DataFrame] = {}
    for files in os.listdir(csv_data_path):
        spectra = pd.read_csv(os.path.join(csv_data_path, files), sep=';')
        spectra['y'] = (spectra['y'] * -1) + 100
        c1=np.array(spectra['y'].tolist())-airPLS(np.array(spectra['y'].tolist()))
        c1 = (c1 * -1) + 100
        spectra['y'] = c1.tolist()
        df_dict[files[:-4]] = spectra
    return df_dict


def save_to_database(database_path: str, df_dict: dict[str, pd.DataFrame]) -> None:
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS SpectraNames (
                        id INTEGER PRIMARY KEY,
                        name TEXT UNIQUE
                    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS SpectraData (
                        id INTEGER PRIMARY KEY,
                        name_id INTEGER,
                        wavelength REAL,
                        intensity REAL,
                        FOREIGN KEY (name_id) REFERENCES SpectraNames(id)
                    )''')

    for name, df in df_dict.items():
        cursor.execute('INSERT OR IGNORE INTO SpectraNames (name) VALUES (?)', (name,))
        conn.commit()

        cursor.execute('SELECT id FROM SpectraNames WHERE name=?', (name,))
        name_id = cursor.fetchone()[0]

        df['name_id'] = name_id
        df.rename(columns={'x': 'wavelength', 'y': 'intensity'}, inplace=True)
        df[['name_id', 'wavelength', 'intensity']].apply(
            lambda row: cursor.execute(
                'INSERT INTO SpectraData (name_id, wavelength, intensity) VALUES (?, ?, ?)',
                (row['name_id'], row['wavelength'], row['intensity'])
            ), axis=1
        )
        conn.commit()


def create_database(database_path: str, csv_data_path: str) -> None:
    df_dict = get_csv_data(csv_data_path)
    save_to_database(database_path, df_dict)
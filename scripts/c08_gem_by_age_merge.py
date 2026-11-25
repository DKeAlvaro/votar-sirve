"""Merge data/interim/c08_gem_age_<year>.csv -> data/clean/c08_gem_by_age.csv"""
import pandas as pd,glob
d=pd.concat([pd.read_csv(f) for f in sorted(glob.glob('data/interim/c08_gem_age_*.csv'))])
d.to_csv('data/clean/c08_gem_by_age.csv',index=False); print(len(d),sorted(d.date.unique()))

## Python Utils

Common functions for data cleaning, and plotting. 

```python
lm_plot(df, xvar, yvar, xtitle, ytitle, ALPHA = 1) 
```

- df = Pandas Data Frame
- xvar = name of x variable
- yvar = name of y variable
- xtitle = title for x axis
- ytitle = title for y axis
- ALPHA = changes the Transparency of dots. 

```python
# example
lm_plot(sample_df, 'X', 'Y', 'x-axis', 'y-axis', ALPHA = 1)
```

![plot](https://raw.githubusercontent.com/Riley25/python_utils/main/plots/Figure_1.png)


```python
def box_hist(df, x_var_name, n_bins, xlim):
```

- df = Pandas Data Frame
- x_var_name = variable to be plotted
- n_bins = how many bin? 
- xlim = list to define the x limit


```python
# boxplot
box_hist(sample_df, 'W', 4, [3 , 6.5])
```

![plot](https://raw.githubusercontent.com/Riley25/python_utils/main/plots/Figure_2.png)





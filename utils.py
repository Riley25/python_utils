
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

os.chdir(r'D:\Documents\Stevens\Python\utils')
print(os.getcwd())

def d_dict(df0):
    n_row, n_col = df0.shape
    r_total = "{:,}".format(n_row)
    print("ROW TOTAL = " + str(r_total) + " COLUMNS = " + str(n_col))

    summary = pd.DataFrame(df0.dtypes)

    percent_missing = list(df0.isnull().sum() * 100 / len(df0))
    summary.insert(1, '%_Blank', percent_missing)
    summary = summary.reset_index()
    summary.columns = ['Variable_Name', 'Variable_Type', '%_Blank']

    sum_stats = df0.describe().T
    sum_stats = sum_stats.reset_index()

    final_summary = pd.merge(summary, sum_stats, how = 'left', left_on = 'Variable_Name', right_on = 'index')
    final_summary = final_summary.reset_index()
    final_summary = final_summary.iloc[:, 1:] # drop the firt column
    del final_summary['index']
    return(final_summary)

sample_df = pd.DataFrame({'X':[1, 2, 3, 4, 5, 6, 7, 8, 9],
                          'Y':[np.nan, 0,2,4,4,5,5, np.nan, np.nan], 
                          'Z':[np.nan, np.nan, np.nan,4,4,5,5, np.nan, np.nan] ,
                          'W': [4, 5 , 4.1, 5.1, 3.2, 4.2, 5.2, 6.2, 5.1]})

print(sample_df.head())
sum = d_dict(sample_df)
print(sum)


def lm_plot(df, xvar, yvar, xtitle, ytitle, ALPHA = 1):
    from sklearn.linear_model import LinearRegression
    plot_mdf3 = df[[xvar, yvar]]
    plot_mdf3 = plot_mdf3[plot_mdf3[xvar].notnull()]
    plot_mdf3 = plot_mdf3[plot_mdf3[yvar].notnull()]

    x = np.array(plot_mdf3[xvar]).reshape((-1,1))
    y = np.array(plot_mdf3[yvar])

    # BUILD THE MODEL
    model = LinearRegression()
    model.fit(x,y)

    #model = LinearRegression.fit().( x , y)
    r_sq = model.score(x,y); print(r_sq)

    y_pred = model.predict(x)
    y_pred = model.intercept_ + model.coef_ * x

    r2 = round(r_sq,2)
    m = round(float(model.coef_), 3)
    b = round(float(model.intercept_) , 2)

    file_name = xvar + '_' + yvar + '.jpg'
    label_name = 'Y = ' + str(m) + '*X + ' + str(b) + ' , (R^2 = ' + str(r2) + ')'

    with plt.style.context('seaborn-whitegrid'):
        fig, ax1 = plt.subplots(figsize = (5.15, 4.85))

        plt.xticks(fontsize = 14) ; plt.yticks(fontsize = 14)
        plt.scatter(plot_mdf3[xvar], plot_mdf3[yvar], alpha = ALPHA)
        plt.plot(x, y_pred, color = 'red', linewidth = 2, label = label_name)

        plt.ylabel(ytitle, fontsize = 15, labelpad = 15)
        plt.xlabel(xtitle, fontsize = 15)

        plt.legend(loc = 'upper center', bbox_to_anchor=(.5,1.15), fancybox = True, shadow = True, frameon  = True, ncol = 1, fontsize = 13)
        plt.tight_layout()
        plt.show()


lm_plot(sample_df, 'X', 'Y', 'x-axis', 'y-axis', ALPHA = 1)



def box_hist(df, x_var_name, n_bins, xlim):
    import seaborn as sns
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    import matplotlib

    n_row, n_col = df.shape
    var = list(df[x_var_name])
    new_var = [x for x in var if str(x)!='nan']

    l = len(new_var)
    percent_blank = round(((n_row - l)/n_row)*100, ndigits = 2)

    colors = ['#0E4D92']

    sns.set(font_scale = 1.2)
    sns.set_style('whitegrid')
    f, (a0, a1) = plt.subplots(2, 1, gridspec_kw = {'height_ratios':[1,3]}, sharex = True, figsize = (7.5 ,6.5))

    # calculate stuff
    avg = round(np.mean(new_var), ndigits = 2)
    median = round(np.median(new_var), ndigits = 2)
    sd = round(np.std(new_var), ndigits = 2)
    upper_quartile = round(np.percentile(new_var, 75), ndigits = 2)
    lower_quartile = round(np.percentile(new_var, 25), ndigits = 2)

    iqr = upper_quartile - lower_quartile
    upper_whisker = upper_quartile+(1.5*iqr)
    lower_whisker = lower_quartile-(1.5*iqr)

    bp = a0.boxplot(new_var, vert = False, patch_artist = True, showmeans = True)
    a0.axes.get_yaxis().set_visible(False)

    for path, color in zip(bp['boxes'], colors):
        path.set_facecolor(color)

    a1.hist(new_var, color = colors[0], bins = n_bins)
    a1.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x,p: format(int(x), ',')))
    plt.ylabel('Count', fontsize  = 14, labelpad = 25)
    plt.xlabel(x_var_name)
    plt.title('Histogram')
    plt.xlim(xlim[0], xlim[1])
    f.tight_layout()

    sum_stats = pd.DataFrame({'25th_p':[lower_quartile], 
                              'median':[median], 
                              '75th_p':[upper_quartile],
                              'mean':[avg],
                              'Standard_deviation':[sd], 
                              'N':[l],
                              'p_blank':[percent_blank] })

    plt.show()
    print(sum_stats)


box_hist(sample_df, 'W', 4, [3 , 6.5])






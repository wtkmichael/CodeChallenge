# CodeChallenge

In this challenge, CSV files of crime data of police force were used to detect the correlation between each LSOA area and associated crime and the detected correlation would be displayed in an interactive webpage. This document will describe the steps taken to perform this task.

### Design/Software implementation
#### 1. Software requirement
This solution consists of two python 2.7 scripts which require library of pandas, numpy, re for data scrapping from the javascript file and bokeh for generating interactive graphs. 

#### 2. Correlation Detection & Ranking
The time series correlations were calculated using numpy.correlate function. Due to its high computational cost, only time series of having similar county or crime are calculated. The highest non-NAN values of correlation were selected as best correlation between the series. For each county and crimes, all correlation calculated (both cross & autocorrelation) are ranked based on its absolute calculated values (Ranked_correlation.csv).

#### 3. GeoJSON scrapping for LSOA coordinates
As the geoJSON file provided is in js format, re library were used to extract LSOA longitude and latitude. These information were then merged into calculatated correlation dataframe and saved into csv file (Corr_with_coord.csv) for plotting. 

#### 4. Display of Heatmap (Bokeh)
Instead of javascript, bokeh was used to generate the interactive graph. Bokeh was selected as it is able to support google map api via GMapPlot. The calculated correlation are plotted above the map based on its intensity. The plot can be updated based on LSOA and crime type selections.

![alt text](https://github.com/wtkmichael/CodeChallenge/blob/master/HeatMap.png)


### Running Code
The first script (corr_calc.py) can be ran as per normal, while the script (plot_bokeh.py) to generate bokeh plot need to be ran at bokeh server to enable its interactivity. 

### Improvement Ideas/Future Plan
1. Instead using numpy.correlate which is computationally expensive, Fast Fourier Transform can be used to speed up correlation calculation.
2. The comparison between time series should be expand to include nearby LSOA
3. Tableau can be used for interactive data visualisation.

# star-rotation
Developed to find rotation periods of stars during SURF 2019

This set of modules can be used to find rotation periods of stars given a
timeseries of relevant data (flux, s-values, h-alpha values, etc), and 
generate a nice plot with periodograms and phased and unphased data.

plot.py contains the functions relating to the periodogram and the plot.
bandpass.py contains the filter.
tools.py contains other important functions used to process the data, 
as well as some smaller helper functions.

Example of how to use them are found in flux_plot.py, cahk_plot.py, and
h_alpha_plot.py. These programs read in a csv file and use the modules to
find rotation periods. Adapting these files to fit your own use should 
be straightforward. 

If your data comes from multiple instruments, take a look at cahk_plot.py 
and h_alpha_plot.py. Otherwise, flux_plot.py is a good place to start.

If you wish to use the example files as is, their usage is as follows:
python3 path/to/flux_plot.py path/to/data_file

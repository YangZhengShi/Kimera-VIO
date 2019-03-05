#!/usr/bin/env python

import os
import sys
import argparse
import argcomplete
import yaml
import csv
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt

def _set_boxplot_colors(boxplot_object, color):
    setp(boxplot_object['boxes'][0], color=color)
    setp(boxplot_object['caps'][0], color=color)
    setp(boxplot_object['caps'][1], color=color)
    setp(boxplot_object['whiskers'][0], color=color)
    setp(boxplot_object['whiskers'][1], color=color)
    #setp(boxplot_object['fliers'], color=color)
    setp(boxplot_object['medians'][0], color=color)

def draw_boxplot(axis, stats, position, idx_experiment):
    """
        bxpstats : list of dicts
          A list of dictionaries containing stats for each boxplot.
          Required keys are:
              - ``med``: The median (scalar float).

              - ``q1``: The first quartile (25th percentile) (scalar
                float).

              - ``q3``: The third quartile (75th percentile) (scalar
                float).

              - ``whislo``: Lower bound of the lower whisker (scalar
                float).

              - ``whishi``: Upper bound of the upper whisker (scalar
                float).

          Optional keys are:
              - ``mean``: The mean (scalar float). Needed if
                ``showmeans=True``.

              - ``fliers``: Data beyond the whiskers (sequence of floats).
                Needed if ``showfliers=True``.

              - ``cilo`` & ``cihi``: Lower and upper confidence intervals
                about the median. Needed if ``shownotches=True``.

              - ``label``: Name of the dataset (string). If available,
                this will be used a tick label for the boxplot

            positions : array-like, default = [1, 2, ..., n]
          Sets the positions of the boxes. The ticks and limits
          are automatically set to match the positions.
    """
    colors = get_colors()
    bxpstats = []
    bxpstats_a = dict()
    bxpstats_a['med'] = stats['median']
    bxpstats_a['q1'] = stats['q1']
    bxpstats_a['q3'] = stats['q3']
    bxpstats_a['whislo'] = stats['min']
    bxpstats_a['whishi'] = stats['max']
    bxpstats.append(bxpstats_a)
    pb = axis.bxp(bxpstats,
                  positions=position,
                  widths=0.8, vert=True,
                  showcaps=True, showbox=True, showfliers=False, )
    _set_boxplot_colors(pb, colors[idx_experiment])

def plot_statistics_vio(statistics, output_boxplot_path):
    len_statistics = len(statistics.items())
    names = []
    maxes = []
    mins = []
    means = []
    samples = []
    stddevs = []
    for key, value in statistics.items():
        print('Reading statistic: %s' % str(key))
        assert 'Timing [ms]' in str(key), "Is this timing information in ms? Otw you are mixing potatoes with apples."
        names.append(str(key[:-11]))
        for key, value in value.items():
            if key == 'max':
                maxes.append(value)
            if key == 'min':
                mins.append(value)
            if key == 'samples':
                samples.append(value)
            if key == 'mean':
                means.append(value)
            if key == 'stddev':
                stddevs.append(value)
    # Create stacked errorbars:
    #plt.errorbar(np.arange(len_statistics), np.asarray(means), np.asarray(stddevs), fmt='ok', lw=3)
    plt.errorbar(np.arange(len_statistics), np.asarray(means), [np.asarray(means) - np.asarray(mins), np.asarray(maxes) - np.asarray(means)],
                 fmt='xk', ecolor='blue', lw=2, capsize=5, capthick=3, mfc='red', mec='green', ms=10, mew=4)

    # Formatting
    bar_width = 0.35
    opacity = 0.8

    locs, labels = plt.xticks()
    plt.xticks(range(len_statistics), names)  # Set locations and labels
    plt.title("Mean VIO timing per module (& max/min).")
    plt.ylabel('Time [ms]')
    plt.xlabel('VIO Module', labelpad=10)
    plt.show()

def parser():
    basic_desc = "Plot timing statistics for VIO pipeline."
    main_parser = argparse.ArgumentParser(description="{}".format(basic_desc))
    input_options = main_parser.add_argument_group("input options")
    input_options.add_argument(
        "statistics_vio_path", help="Path to the **YAML** file containing the VIO statistics.",
        default="./results/V1_01_easy/S/StatisticsVIO.yaml")
    input_options.add_argument(
        "output_boxplot_path", help="Path where to save boxplot file containing the VIO statistics.",
        default="./results/V1_01_easy/S/StatisitcsVIOboxplots.eps")
    return main_parser

def main(statistics_vio_path, output_boxplot_path):
    # Read vio statistics yaml file.
    print("Reading VIO statistics from: %s" % statistics_vio_path)
    if os.path.exists(statistics_vio_path):
        with open(statistics_vio_path,'r') as input:
            statistics = yaml.load(input)
            plot_statistics_vio(statistics, output_boxplot_path)

if __name__ == "__main__":
    parser = parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    main(args.statistics_vio_path, args.output_boxplot_path)
    sys.exit(os.EX_OK)

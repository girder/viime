# Metaboanalyst Test Data

The CSV files in this directory are used to test that VIIME generates the same analysis results as Metaboanalyst.

## metaboanalyst_original.csv

Metabolite concentrations of 77 urine samples from cancer patients measured by 1H NMR (Eisner R, et al.). Group 1- cachexic; group 2 - control
This is a sample dataset from Metaboanalyst.
This other files in this directory are generated using this dataset.
Tests will load this file into VIIME, perform the same transformations, and compare the resulting CSVs.
This dataset should have no missing values, so no data interpolation is required.

## metaboanalyst_normalization_sum.csv

1. Skip Data Integrity check
2. Sample Normalization -> Normalization by sum
3. Download `data_normalized.csv`

## metaboanalyst_transformation_log.csv

1. Skip Data Integrity check
2. Sample Transformation -> Log transformation
3. Download `data_normalized.csv`

## metaboanalyst_transformation_cube_root.csv

1. Skip Data Integrity check
2. Sample Transformation -> Cube root transformation
3. Download `data_normalized.csv`

## metaboanalyst_scaling_auto.csv

1. Skip Data Integrity check
2. Data scaling -> Auto scaling
3. Download `data_normalized.csv`

## metaboanalyst_scaling_pareto.csv

1. Skip Data Integrity check
2. Data scaling -> Pareto scaling
3. Download `data_normalized.csv`

## metaboanalyst_scaling_range.csv

1. Skip Data Integrity check
2. Data scaling -> Range scaling
3. Download `data_normalized.csv`
---
title: 'Viime: Visualization and Integration of Metabolomics Experiments'
tags:
  - metabolomics
  - visualization
  - web application
authors:
  - name: Thomas O'Connell
    affiliation: 1
  - name: Lilian Golzarri Arroyo
    affiliation: 1
  - name: Jun Wan
    affiliation: 1
  - name: Daniel Raftery
    affiliation: 2
  - name: Jon Beezley
    affiliation: 3
  - name: Brandon Davis
    affiliation: 3
  - name: Roni Choudhury
    affiliation: 3
  - name: Samuel Gratzl
    affiliation: 3
  - name: Jeff Baumes
    affiliation: 3
  - name: Jared Tomeck
    affiliation: 3
affiliations:
  - name: Indiana University
    index: 1
  - name: University of Washington
    index: 2
  - name: Kitware Inc.
    index: 3
date: 11 March 2020
bibliography: paper.bib

---

# Summary

Metabolomics involves the comprehensive measurement of metabolites from a
biological system. The resulting metabolite profiles are influenced by genetics,
lifestyle, diet and environment and therefore provides a more holistic
biological readout of the pathological condition of the organism [@beger:2016;
@wishart:2016]. The challenge for metabolomics is that no single analytical
platform can provide a truly comprehensive coverage of the metabolome. The most
commonly used platforms are based on mass-spectrometry (MS) and nuclear magnetic
resonance (NMR) methods. Investigators are increasingly using both methods to
increase the metabolite coverage. The challenge for this type of multi-platform
approach is that the data structure may be very different in these two
platforms. For example, NMR data may be reported as a list of spectral features
e.g. bins or peaks with arbitrary intensity units or more directly with named
metabolites reported in concentration units ranging from micromolar to
millimolar. Some MS approaches can also provide data in the form of identified
metabolite concentrations, but given the superior sensitivity of MS, the
concentrations can be several orders of magnitude lower than for NMR. Other MS
approaches yield data in the form of arbitrary response units where the dynamic
range can be more than 6 orders of magnitude. Given the diversity of data
structures (i.e. magnitude and dynamic range) integrating the data from multiple
platforms can be challenging.  This often leads investigators to analyze the
datasets separately which prevents the observation of potentially interesting
correlations between metabolites detected on different platforms.  Viime is an
open-source, web-based application designed to integrate metabolomics data from
multiple platforms. The workflow of Viime for data ingestion, pretreatment, data
fusion and visualization is shown in Figure 1.

TODO: create and insert Figure 1 (showing cleanup steps)

# User Interface

# Backend Processing

VIIME’s processing backend is implemented as a RESTful API using the Flask web
framework. Data persistence is provided through normalized CSV files stored on a
filesystem and associated data in a SQLite database through SQLAlchemy’s ORM.
Files stored internally are linked with rows in the database using custom fields
provided by File Depot [@filedepot:web]. The backend leverages Pandas for raw
file parsing and normalization. Data processing is done by a combination of
Scikit-learn for common statistical algorithms and R packages for specialized
algorithms. The R-python integration is provided by a secondary REST service
exposed internally via OpenCPU.

Upon uploading a new dataset from an Excel or raw CSV file, the server begins by
constructing a Pandas dataframe. Any parsing errors due to malformed files
immediately result in an error response from the server. The Pandas object is
used to populate a new row in the primary data table with associated metadata
and processing defaults. Every row and column from the parsed dataset is also
added to related tables including header information, detected data type, and an
initial table structure determining properties such as which rows and columns
contain metadata, group information, or raw metabolite values.

The cleanup phase of the workflow allows users to override the initial table
structure for example by marking specific columns as metadata or by "masking"
rows so they are ignored in the processing steps. Each time the user makes a
change to the table structure the dataset is processed by a validation function
that determines whether the dataset is ready for processing. This validation
checks many properties of the dataset including that all metabolite values are
numeric and metabolite names are unique. In addition, the validation will warn
the user of likely problems such as too many missing or "not a number" values
within a metabolite or group or columns containing an excessively low variance.

Once validated, the original dataset is broken down into three tables, one
containing the raw metabolite measurements and two containing metadata about
each row and column in the measurement table. The measurement table is then
processed through imputation which fills in missing data using a series of
user-configurable algorithms. A function defines which metabolites have missing
data according to the Missing Not at Random (MNAR) or Missing Completely At
Random (MCAR) models, depending on the percentage of missing values per group
per metabolite. For each type of missingness the user can choose different
imputation methods; MNAR allows users to impute using the Zero or Half Minimum
strategies while MCAR allows imputation via Random Forest, K-Nearest Neighbor,
Mean, or Median. Most of the imputation methods were implemented in R, while
Random Forest and K-Nearest Neighbor were implemented with the R packages
`missForest` and `impute`, respectively.

Before statistical analysis is performed, the imputed dataset is passed through
a series of optional, user-configurable preprocessing steps including
normalization (Min Max, Sum, Reference Sample, Weight/Volume), transformation
(Log10, Log2, Square Root, Cube Root), and scaling (Autoscaling, Pareto Scaling,
Range Scaling, Vast Scaling, Level Scaling). All preprocessing functions were
programmed in R. After preprocessing, the dataset is ready for input into the
analysis methods.

# Future Work

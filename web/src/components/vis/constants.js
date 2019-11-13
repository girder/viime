
export const correlation_methods = [
  {
    label: 'Pearson',
    value: 'pearson',
    helpText: 'is a measure of linear correlation between two variables, it can go from -1 to 1, where 1 means the two variables are positively correlated, 0 means no correlation and -1 negative correlation.',
  },
  {
    label: 'Kendall Tau',
    value: 'kendall',
    helpText: 'it is a non-parametric measure of statistical association based on the ranks of the data, it could take values from -1 to 1, where 1 means the observations in both variables have similar rank, and -1 when they have the opposite rank in both variables. (Better for smaller sample size)',
  },
  {
    label: 'Spearman rank',
    value: 'spearman',
    helpText: 'it is a non-parametric measure of statistical association based on the ranks of the data, it could take values from -1 to 1, where 1 means the observations in both variables have similar rank, and -1 when they have the opposite rank in both variables.  (Better for larger sample size)',
  },
];

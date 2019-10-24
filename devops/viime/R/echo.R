#' Echo
#'
#' This just returns the table passed without modification for testing.

echo <- function(table) {
  return (read.csv(table, row.names=1))
}

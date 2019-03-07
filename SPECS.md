# Prevalence predictor
Function to predict probability of infection (prevalence) using georeferenced binomial (number examined, numbers positive) data.

## Parameters

JSON object containing:

`region_definition` - a JSON containing the following fields:
  `lng` - array of longitudes of locations to predict to
  `lat` - array of latitudes of locations to predict to
  `id` - array of unique IDs of locations to predict to
  
`train_data` - a JSON containing the following fields:
  `lng` - array of longitudes of locations at which data are available
  `lat` - array of latitudes of locations at which data are available
  `n_trials` - array of number of individuals examined/tested at each location
  `n_positive` - array of number of individuals positive at each location

`request_parameters` - a JSON containing the following field:
  `threshold` - a single number (can be float) >0 and <1 representing the threshold prevalence used to define a hotspot. e.g. 0.2 if hotspots are areas where prevalence is >20%. 
  
  
## Constraints

- maximum size of..

## Response




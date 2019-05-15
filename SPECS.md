# Prevalence predictor
Function to predict probability of infection (prevalence) using georeferenced binomial (number examined, numbers positive) data.

## Parameters

A nested JSON object containing:

`region_definition` - Required. A JSON array containing objects with the following fields:
- `lng` - array of longitudes of locations to predict to
- `lat` - array of latitudes of locations to predict to
- `id` - array of unique IDs of locations to predict to
  
`train_data` - Required. A JSON array containing objects with the following fields:
- `lng` - array of longitudes of locations at which data are available
- `lat` - array of latitudes of locations at which data are available
- `n_trials` - array of number of individuals examined/tested at each location
- `n_positive` - array of number of individuals positive at each location

- `uncertainty_type` - {string} Either `exceedance_probability` or `95%_bci`
- `exceedance_threshold` - {Number} Optional. Required if `uncertainty_type` is `exceedance_probability`. Between 0 and 1.
  
  
## Constraints

- maximum size of..

## Response
JSON object containing

`estimates` - a JSON containing
- `exceedance_prob` - array of probabilities that prevlance exceeds the `threshold`
- `entropy` - entropy estimates
- `id` - array of unique IDs of prediction location
- `category` - hotspot category (1/0 classification where locations are classed as 1 if `exceedance_prob` >= 0.5)

`polygons` - coordinates of voronoi polygons associated with each point defined in `region_definition`


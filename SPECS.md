# Prevalence predictor

Give us a bunch of GeoJSON points with numbers examined and numbers positive, as well as a GeoJSON of prediction points, and we'll predict the probability of occurrence at each prediction point.

## Parameters

A nested JSON object containing:
- `point_data` - {GeoJSON FeatureCollection} Required. Features with following properties:
  - `n_trials` - {integer} Required. Number of individuals examined/tested at each location (‘null’ for points without observations)
  - `n_positive` - {integer} Required. Number of individuals positive at each location (‘null’ for points without observations)
  
- `uncertainty_type` - {string} Optional. Either ‘exceedance_probability’ or ‘95_perc_bci’. Defaults to `95_perc_bci`. Representing how uncertainty should be calculated. If  ‘exceedance_probability’ uncertainty estimates are calculated using exceedance probability uncertainty, i.e. the probability prevalence exceeds exceedance_threshold). If ‘95_perc_bci’, uncertainty is calculated as the 95% Bayesian credible interval. 
- `exceedance_threshold` - {numeric} Required if `uncertainty_type` is `exceedance_probability`. Defines the exceedance threshold used to calculate exceedance probabilities. Must be >0 and <1. 

- `layer_names` - {array of strings} Optional. Names relating to the covariate to use to model and predict. See [here](https://github.com/disarm-platform/fn-covariate-extractor/blob/master/SPECS.md) for options.


## Constraints

- maximum number of points/features
- maximum number of layers is XX
- can only include points within a single country

## Response

- `point_data` {GeoJSON FeatureCollection} With additional prediction field representing predicted probability of occurrence (0-1 scale). Uncertainty field added if `uncertainty_type` defined when fitting the model: named after `uncertainty_type`  

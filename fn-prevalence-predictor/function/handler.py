import sys

import numpy as np
import pandas as pd
import requests
import disarm_gears


def run_function(params: dict):
    #
    # 1. Handle input
    #

    # Set random seed
    np.random.seed(1000)

    # redirecting STDOUT to avoid over-chatty PyGAM
    original = sys.stdout
    sys.stdout = open('file', 'w')

    layer_names = params.get('layer_names')
    exceedance_threshold = params.get('exceedance_threshold')
    point_data = params.get('point_data')
    input_data = disarm_gears.util.geojson_decoder_1(point_data)

    #
    # 2. Process
    #

    # Drop NA coordinates
    input_data.dropna(axis=0, subset=['lng', 'lat'])

    # Find covariates
    if layer_names is not None:

        # Call fn-covariate-extractor
        open_faas_link = 'http://faas.srv.disarm.io/function/fn-covariate-extractor'
        covs_request = disarm_gears.util.geojson_encoder_1(input_data, layer_names=layer_names)
        covs_response = requests.post(open_faas_link, data=covs_request)
        #TODO? assert covs_response.json()['type'] == 'success'
        #TODO define how to handle NA entries in the covariates

        # Merge output into input_data
        covs_data = disarm_gears.util.geojson_decoder_1(covs_response.json()['result'])
        input_data = pd.merge(input_data, covs_data, how='left', left_on=['lng', 'lat'], right_on=['lng', 'lat'])

    # Define mgcv model
    gam_formula = "cbind(n_positive, n_trials - n_positive) ~ te(lng, lat, bs='gp', m=c(2), k=-1)"
    if layer_names is not None:
        gam_formula = [gam_formula] + ['s(%s)' %i for i in layer_names]
        gam_formula = '+'.join(gam_formula)

    # Fit model and make predictions/simulations
    train_data = input_data.dropna(axis=0)
    gam = disarm_gears.r_plugins.mgcv_fit(gam_formula, family='binomial', data=train_data)
    gam_pred = disarm_gears.r_plugins.mgcv_predict(gam, data=input_data, response_type='response')
    link_sims = disarm_gears.r_plugins.mgcv_posterior_samples(gam, data=input_data, n_samples=200,
                                                              response_type='inverse_link')

    # Credible interval
    bci = np.percentile(link_sims, q=[2.5, 97.5], axis=0)
    bci = 1. / (1. + np.exp(-bci))

    # Exceedance probability
    ex_prob = None
    if exceedance_threshold is not None:
        link_threshold = np.log(exceedance_threshold / (1 - exceedance_threshold))
        ex_prob = (link_sims > link_threshold).mean(axis=0)

    #
    # 3. Package output
    #

    input_data['prevalence'] = gam_pred
    input_data['lower'] = bci[0]
    input_data['upper'] = bci[1]
    input_data['exceedance_probability'] = ex_prob

    response = disarm_gears.util.geojson_encoder_2(dataframe=input_data,
                                                   fields=['prevalence', 'lower', 'upper', 'exceedance_probability'],
                                                   dumps=False)

    # Restore STDOUT
    sys.stdout = original

    return response.get('point_data')

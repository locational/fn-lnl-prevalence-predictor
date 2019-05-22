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

    # Add id column if it is not provided
    if 'id' not in input_data.columns:
        input_data['id'] = list(range(input_data.shape[0]))

    #
    # 2. Process
    #

    # Drop NA coordinates
    input_data.dropna(axis=0, subset=['lng', 'lat'])

    # Find covariates
    if layer_names is not None:
        # Call fn-covariate-extractor
        open_faas_link = 'http://faas.srv.disarm.io/function/fn-covariate-extractor'
        covs_request = disarm_gears.util.geojson_encoder_3(input_data, fields=['id'], layer_names=layer_names, dumps=True)
        covs_response = requests.post(open_faas_link, data=covs_request)
        # TODO? assert covs_response.json()['type'] == 'success'
        # TODO define how to handle NA entries in the covariates

        # Merge output into input_data
        covs_data = disarm_gears.util.geojson_decoder_1(covs_response.json()['result'])
        input_data = pd.merge(input_data, covs_data[['id'] + layer_names], how='left', left_on=['id'], right_on=['id'])
        #for li in layer_names:
        #    input_data[li] = covs_data[li]

    # Define mgcv model
    gam_formula = "cbind(n_positive, n_trials - n_positive) ~ te(lng, lat, bs='gp', m=c(2), k=-1)"
    if layer_names is not None:
        gam_formula = [gam_formula] + ['s(%s)' % i for i in layer_names]
        gam_formula = '+'.join(gam_formula)

    # Fit model and make predictions/simulations
    train_data = input_data.dropna(axis=0)
    gam = disarm_gears.r_plugins.mgcv_fit(gam_formula, family='binomial', data=train_data)
    gam_pred = disarm_gears.r_plugins.mgcv_predict(gam, data=input_data, response_type='response')
    link_sims = disarm_gears.r_plugins.mgcv_posterior_samples(gam, data=input_data, n_samples=200,
                                                              response_type='link')

    # Credible interval
    bci = np.percentile(link_sims, q=[2.5, 97.5], axis=0)
    bci = 1. / (1. + np.exp(-bci))

    # Exceedance probability
    ex_prob = None
    ex_uncert = None

    if exceedance_threshold is not None:
        link_threshold = np.log(exceedance_threshold / (1 - exceedance_threshold))
        ex_prob = (link_sims > link_threshold).mean(axis=0)
        ex_uncert = 0.5 - abs(ex_prob - 0.5)

    #
    # 3. Package output
    #
    input_data['prevalence_prediction'] = gam_pred
    input_data['prevalence_bci_width'] = bci[1] - bci[0]
    input_data['exceedance_probability'] = ex_prob
    input_data['exceedance_uncertainty'] = ex_uncert

    response = disarm_gears.util.geojson_encoder_2(dataframe=input_data,
                                                   fields=['id',
                                                           'prevalence_prediction',
                                                           'prevalence_bci_width',
                                                           'exceedance_probability',
                                                           'exceedance_uncertainty'],
                                                   dumps=False)

    # Restore STDOUT
    sys.stdout = original

    return response.get('point_data')

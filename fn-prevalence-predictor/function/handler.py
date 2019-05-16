import json
import sys

import disarm_gears
import pandas as pd
import requests
from disarm_gears.validators import *


def run_function(req: dict):
    #
    # 1. Handle input
    #

    # Set random seed
    np.random.seed(1000)

    # redirecting STDOUT
    original = sys.stdout
    sys.stdout = open('file', 'w')

    # Train and prediction datasets
    json_data = json.loads(req)
    train_data = pd.DataFrame(json_data['train_data'])
    region_data = pd.DataFrame(json_data['region_definition'])

    # TODO: ensure this extracts from a GeoJSON FeatureCollection, not arrays of values
    x_frame = np.array(region_data[['lng', 'lat']])
    x_id = np.array(region_data['id'])
    x_coords = np.array(train_data[['lng', 'lat']])
    n_trials = np.array(train_data['n_trials'])
    n_positive = np.array(train_data['n_positive'])
    layer_names = json_data['train_data']['layer_names']

    #
    # 2. Process
    #

    # Validate data inputs (some of these are redundant)
    validate_2d_array(x_frame, n_cols=2)
    frame_size = x_frame.shape[0]
    if x_id is None:
        x_id = np.arange(frame_size)
    else:
        validate_1d_array(x_id, size=frame_size)
    validate_2d_array(x_coords, n_cols=2)
    train_size = x_coords.shape[0]
    validate_1d_array(n_positive, size=train_size)
    validate_non_negative_array(n_positive)
    validate_integer_array(n_positive)
    validate_positive_array(n_trials)
    validate_integer_array(n_trials)
    validate_1d_array(n_trials, size=train_size)

    # TODO: Don't think we need `ts_export`
    ts_export = {idi: {'lng': xi[0], 'lat': xi[1]} for idi, xi in zip(x_id, x_frame)}

    # Find covariates
    if layer_names is not None:
        open_faas_link = 'http://faas.srv.disarm.io/function/fn-covariate-extractor'
        train_request = disarm_gears.util.geojson_encoder_1(train_data, layer_names=layer_names)
        frame_request = disarm_gears.util.geojson_encoder_1(region_data, layer_names=layer_names)
        train_response = requests.post(open_faas_link, data=train_request)
        frame_response = requests.post(open_faas_link, data=frame_request)
        cov_train = np.array(
            [[js['properties'][k] for k in layer_names] for js in train_response.json()['result']['features']])
        # TODO: Duplicated from above?
        cov_frame = np.array(
            [[js['properties'][k] for k in layer_names] for js in frame_response.json()['result']['features']])

        # TODO reshape cov_frame if it is one-dimensional
        df_train = pd.DataFrame(np.hstack([x_coords, cov_train, n_trials[:, None], n_positive[:, None]]),
                                columns=['lng', 'lat'] + layer_names + ['n_trials' 'n_positive'])
        df_frame = pd.DataFrame(np.hstack([x_frame, cov_frame]), columns=['lng', 'lat'] + layer_names)

        # MGCV model
        # TODO: what is `i` below?
        gam_formula = ["cbind(n_positive, n_trials - n_positive) ~ te(lng, lat, bs='gp', m=c(2), k=-1)"] + [
            's(%s)' % (i) in layer_names]
        gam_formula = '+'.join(gam_formula)

    else:
        # TODO: remove layer_names below - will always be of NoneType
        df_train = pd.DataFrame(np.hstack([x_coords, n_trials[:, None], n_positive[:, None]]),
                                columns=['lng', 'lat'] + layer_names + ['n_trials' 'n_positive'])
        df_frame = pd.DataFrame(x_frame, columns=['lng', 'lat'] + layer_names)

        # MGCV model
        gam_formula = "cbind(n_positive, n_trials - n_positive) ~ te(lng, lat, bs='gp', m=c(2), k=-1)"

    gam = disarm_gears.r_plugins.mgcv_fit(gam_formula, family='binomial', data=df_train)
    gam_pred = disarm_gears.r_plugins.mgcv_predict(gam, data=df_frame, response_type='response')
    link_sims = disarm_gears.r_plugins.mgcv_posterior_samples(gam, data=df_frame, n_samples=200,
                                                              response_type='inverse_link')

    # Uncertainty computation
    uncertainty_type = json_data['request_parameters']['uncertainty_type']
    # TODO: Check if logic below - is possible to be neither, and so `ut` will not be assigned
    if uncertainty_type == 'exceedance_probability':
        threshold = json_data['request_parameters']['threshold']
        link_threshold = np.log(threshold / (1 - threshold))
        # TODO: Syntax-error?
        ut = (link_sims > link_threshold).mean(0)
    elif uncertainty_type == '95_perc_bci':
        ut = np.percentile(link_sims, q=[2.5, 97.5], axis=0)
        ut = 1. / (1. + np.exp(-ut))

    m_export = {'id': x_id.tolist(), 'prevalence': gam_pred.tolist(), 'uncertainty': ut.tolist(),
                'uncertainty_type': uncertainty_type}

    #
    # 3. Package output
    #

    # TODO: reshape response object
    # TODO: polygons isn't polygons! The output should include
    #  the original points passed in, with additional prediction parameters
    response = {'polygons': ts_export, 'estimates': m_export}

    # Restore STDOUT
    sys.stdout = original

    # TODO: Don't want to print response here after we've restored STDOUT?
    print(response)

    # Return result
    print(json.dumps(response), end='')

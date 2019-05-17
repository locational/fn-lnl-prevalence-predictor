from preprocess_helpers import write_temp_from_url_or_base64, required_exists, is_type


def preprocess(params: dict):
    required_exists('point_data', params)

    if params.get('uncertainty_type'):
        is_type('uncertainty_type', params, str)

    #  TODO: JS - should be either exceedance_probability or 95_perc_bci
    # if params.get('uncertainty_type')

    if params.get('uncertainty_type') == 'exceedance_probability':
        required_exists('exceedance_threshold', params)

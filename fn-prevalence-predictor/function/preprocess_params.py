from preprocess_helpers import write_temp_from_url_or_base64, required_exists


def preprocess(params: dict):
    type(params['request_parameters']['threshold']) in [float, int]

    required_exists('train_data', params)

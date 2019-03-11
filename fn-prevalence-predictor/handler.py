import sys
import pandas as pd
import numpy as np
from disarm_gears.chain_drives.prototypes import adaptive_prototype_0


def run_function(params):
    # Extract required params
    threshold = params['request_parameters']['threshold']
    region_definition = params['region_definition']
    train_data = params['train_data']

    # Create initial dataframes
    region_data = pd.DataFrame(region_definition)
    train_data = pd.DataFrame(train_data)

    #
    x_frame = np.array(region_data[['lng', 'lat']])
    x_id = np.array(region_data['id'])
    x_coords = np.array(train_data[['lng', 'lat']])
    n_trials = np.array(train_data['n_trials'])
    n_positive = np.array(train_data['n_positive'])

    # Start the hard bit
    sys.stderr.write("Starting heavy bit...")
    response = adaptive_prototype_0(x_frame=x_frame, x_id=x_id,
                                    x_coords=x_coords,
                                    n_positive=n_positive,
                                    n_trials=n_trials,
                                    threshold=threshold)  # , covariate_layers=None)
    return response

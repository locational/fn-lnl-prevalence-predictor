import json
import sys
import pandas as pd
import numpy as np
from disarmgears.chain_drives.prototypes import adaptive_prototype_0
from disarmgears.chain_drives.prototypes import sentinel

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    # redirecting sstdout 
    original = sys.stdout
    sys.stdout = open('file', 'w')

    json_data = json.loads(req)
    region_data = pd.DataFrame(json_data['region_definition'])
    train_data = pd.DataFrame(json_data['train_data'])

    x_frame = np.array(region_data[['lng', 'lat']])
    x_id = np.array(region_data['id'])
    x_coords = np.array(train_data[['lng', 'lat']])
    n_trials = np.array(train_data['n_trials'])
    n_positive = np.array(train_data['n_positive'])
    threshold = json_data['request_parameters']['threshold']

    response = adaptive_prototype_0(x_frame=x_frame, x_id=x_id,
				    x_coords=x_coords,
				    n_positive=n_positive,
				    n_trials=n_trials,
				    threshold=threshold,
				    covariate_layers=None)
    sys.stdout = original
    print(json.dumps(response), end='')
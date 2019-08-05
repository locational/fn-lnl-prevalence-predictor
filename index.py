import json
import shutil
import sys
from json import JSONDecodeError
from urllib.error import URLError

import config
from function import handler
from function import preprocess_params


def get_params_from_stdin() -> dict:
    buf = ""
    while True:
        line = sys.stdin.readline()
        buf += line
        if line == "":
            break
    return json.loads(buf)


def handle_error(error, message=None):
    # This will be sent back to caller/server
    start = "Error from function: "

    # This will be written to container logs
    sys.stderr.write(f'{start}: {str(error)}\n\n')

    if type(error) is ValueError:
        result = start + str(error)
    
    else:
        if message is None:
            # TODO: Send back more limited error message to user
            result = start + str(error)
        else:
            result = start + message
    
    print(json.dumps({"function_status": "error", "result": result}))


# Please give me content that JSON-dumpable:
#   e.g. a string, could be base64-encoded, or some JSON-like object
def handle_success(result):
    print(json.dumps({"function_status": "success",
                      "result": result}))


if __name__ == "__main__":

    # Setup server, listen for POST on port 8080

    try:
        # Get and parse params
        params = get_params_from_stdin()

        # Mutate the params to get them ready for use
        preprocess_params.preprocess(params)

        # Run!
        # redirect stdout to stderr (for logging)
        # print("Some log message") #--> STDOUT (redirected to STDERR)
        # eprint("Error of some kind") #--> STDERR
        function_response = handler.run_function(params)

        # Handle success
        handle_success(function_response)

    except JSONDecodeError as e:
        handle_error(e, "Request received by function is not valid JSON. Please check docs")

    except URLError as e:
        handle_error(e, "Problem downloading files. Please check URLs passed as parameters are "
                        "valid, are live and are publicly accessible.")

    # Bare exceptions are not recommended - see https://www.python.org/dev/peps/pep-0008/#programming-recommendations
    # We're using one to make sure that _any_ errors are packaged and returned to the calling server,
    # not just logged at the function gateway
    except Exception as err:
        handle_error(err)

    finally:
        shutil.rmtree(config.TEMP)

import pickle
import os
import pandas        as     pd
from flask           import Flask, request, Response

# healthinsurance is the directory, on the same tree directory level as handler.py
# HealthInsurance is the file (HealthInsurance.py) inside the directory
# -> healthinsurance.HealthInsurance
# HealthInsurance is the class inside HealthInsurance.py
# from: directory. import: class.
from healthinsurance.HealthInsurance import HealthInsurance

# set home path
path = '/home/gustavo/projects/pa004_health_insurance_cross_sell/pa004_gustavo_cunha/'

# load final model to API memory
with open( path + 'src/models/model_health_insurance.pkl', 'rb' ) as production_model:
    model = pickle.load( production_model )

# initialize API
app = Flask( __name__ )

# create url for request
# GET: ask for data
# POST: send data to receive data
@app.route( '/heathinsurance/predict', methods=['POST'] )
def health_insurance_predict(): # first function to run when receive a request
    # get json data on request
    test_json = request.get_json()

    # check if data was sent on request
    if test_json:
    # unique row given on the request made: json = dictionary
        if isinstance( test_json, dict ): 
            test_raw = pd.DataFrame( test_json, index=[0] )

        # multiple rows given on the request made
        else:
            test_raw = pd.DataFrame( test_json, columns=test_json[0].keys() )

        # create a copy of original data
        original_data = test_raw.copy()

        # Instantiate HealthInsurance class
        pipeline = HealthInsurance()

        # clean data
        df_dc_done = pipeline.data_cleaning( test_raw )

        # engineer data
        df_fe_done = pipeline.feature_engineering( df_dc_done )

        # prepare data
        df_dp_done = pipeline.data_preparation( df_fe_done )

        # predict
        df_response = pipeline.get_prediction( model, original_data, df_dp_done )

        # return data to API request
        return df_response

    # data was not sent on request
    else:
        # mimetype -> from a json application
        return Response( '{}', status = 200, mimetype = 'application/json' )

# when handler.py script is run, run flask
if __name__ == '__main__':
    port = os.environ.get('PORT', 5000)
    # '0.0.0.0' is the local host
    app.run( '0.0.0.0', debug = True )
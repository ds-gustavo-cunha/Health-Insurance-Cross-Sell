import pickle
import numpy  as np
import pandas as pd

class HealthInsurance:
    def __init__( self ): # class constructor
        # set home path
        self.home_path = '/home/gustavo/projects/pa004_health_insurance_cross_sell/pa004_gustavo_cunha/'

        # load scalers
        with open( self.home_path + 'src/features/annual_premium_rs.pkl', 'rb' ) as premium_scaler:
            self.annual_premium_scaler = pickle.load( premium_scaler )
        with open( self.home_path + 'src/features/age_mms.pkl', 'rb' ) as age_scaler:
            self.age_scaler = pickle.load( age_scaler )
        with open( self.home_path + 'src/features/vintage_mms.pkl', 'rb' ) as vintage_scaler:
            self.vintage_scaler = pickle.load( vintage_scaler )


    def data_cleaning( self, df_to_clean ):
        """df_to_clean is the data(frame) to be cleaned"""

        # lower case column names to avoid errors
        df_to_clean.columns = df_to_clean.columns.str.lower()

        # Data Cleaning is done -> df_dc_done
        df_dc_done = df_to_clean


        return df_dc_done


    def feature_engineering( self, df_to_fe ):
        """df_to_fe is the data(frame) to be engineered"""

        # convert region_code column to integer
        df_to_fe[ 'region_code' ] = df_to_fe[ 'region_code' ].astype( int );

        # convert region_code column to integer
        df_to_fe[ 'policy_sales_channel' ] = df_to_fe[ 'policy_sales_channel' ].astype( int );

        # convert region_code column to integer
        df_to_fe[ 'annual_premium' ] = df_to_fe[ 'annual_premium' ].astype( int );

        # convert damage column from Yes-No to True-False format
        df_to_fe['vehicle_damage'] = df_to_fe[ 'vehicle_damage' ].apply(
                                                                    lambda x: True if x == 'Yes'else False )

        # Feature Engineering is done -> df_fe_done
        df_fe_done = df_to_fe


        return df_fe_done


    def data_preparation( self, df_to_dp ):
        """df_to_dp is the data(frame) be (data) prepared"""

        # apply min-max scaler on age column of training dataset
        df_to_dp['age'] = self.age_scaler.transform( df_to_dp['age'].values.reshape(-1,1) )

        # apply min-max scaler on vintage column of training dataset
        df_to_dp['vintage'] = self.vintage_scaler.transform( df_to_dp['vintage'].values.reshape(-1,1) )

        # apply robust scaler on annual_premium column of training dataset
        df_to_dp['annual_premium'] = self.annual_premium_scaler.transform( df_to_dp['annual_premium'].values.reshape(-1,1) )

        # encode gender column -> convert to number
        df_to_dp[ 'gender' ] = df_to_dp[ 'gender' ].map( { 'Male': 1,
                                                           'Female': 0 } )

        # encode vehicle_damage column -> convert boolean to integers
        df_to_dp[ 'vehicle_damage'] = df_to_dp[ 'vehicle_damage'].astype( int )

        # encode vehicle_age column -> ordinal encoding
        df_to_dp[ 'vehicle_age' ] = df_to_dp[ 'vehicle_age' ].map( {'< 1 Year': 0  ,
                                                                    '1-2 Year': 1  ,
                                                                    '> 2 Years': 2   } )

        # encode policy_sales_channel -> frequency encoding
        df_to_dp['policy_sales_channel'] = df_to_dp.groupby( 'policy_sales_channel' ).size() / len( df_to_dp )
        df_to_dp['policy_sales_channel'] = df_to_dp['policy_sales_channel'].fillna( 0 )

        # encode region_code -> frequency encoding
        df_to_dp['region_code'] = df_to_dp.groupby( 'region_code' ).size() / len( df_to_dp )
        df_to_dp['region_code'] = df_to_dp['region_code'].fillna( 0 )

        # cols selection on feature selection
        cols_selected = [ 'vintage',
                          'annual_premium',
                          'age',
                          'vehicle_damage',
                          'previously_insured',
                          'vehicle_age']

        # Data Preparation (and feature selection) is is done -> df_dp_done
        df_dp_done = df_to_dp[ cols_selected ]


        return df_dp_done


    def get_prediction( self, model, original_data, test_data ):
        """
        Args:
            model: model trained
            original_data: original data sent on request
            test_data: transformed data, ready for prediction
        """

        # model prediction
        pred = model.predict_proba( test_data )

        # join prediction into original data
        original_data['score'] = pred[:, 1].tolist()

        # convert the result to json (API transferring format)
        df_prediction = original_data.to_json( orient = 'records', date_format = 'iso' )


        return df_prediction
// create a button 
function onOpen() {
  // map user interface
  var ui = SpreadsheetApp.getUi();
  // create a menu for Health Insurance
  ui.createMenu( 'Health Insurance Prediction' )
    // create 'Get Prediction' button on created menu
    // once clicked, button calls PredictAll function
    .addItem( 'Get Prediction', 'PredictAll')
    // add to user interface
    .addToUi();  
}

// production server (api endpoint)
host_production = 'health-insurance-cross-sell.herokuapp.com/heathinsurance'

// ----------------------------
// ----- Helper Function ------
// ----------------------------
// API Call
function ApiCall( data, endpoint ){
  var url = 'https://' + host_production + endpoint;
  // create json for api request
  var payload = JSON.stringify( data );

  // request headers
  var options = {'method': 'POST', 'contentType': 'application/json', 'payload': payload};

  Logger.log( url )
  Logger.log( options )

  // make request
  var response = UrlFetchApp.fetch( url, options );

  // get response
  var rc = response.getResponseCode();
  var responseText = response.getContentText();

  // if an error occur on request
  if ( rc !== 200 ){
    Logger.log( 'Response (%s) %s', rc, responseText );
  }
  // if request was successful
  else{
    prediction = JSON.parse( responseText );
  }
  return prediction
};

// Health Insurance Propensity Score Prediction
function PredictAll(){
  // select active sheet
  var ss = SpreadsheetApp.getActiveSheet();
  // get columns from active sheet
  var titleColumns = ss.getRange( 'A1:K1' ).getValues()[0];
  // get last row 
  var lastRow = ss.getLastRow();
  
  // get data inserted on sheet
  var data = ss.getRange( 'A2' + ':' + 'K' + lastRow ).getValues();

  // itereate over all rows in data
  for ( row in data ){
    // json data for the given row
    var json = new Object();

    // iterate over all columns in the given row
    for( var j=0; j < titleColumns.length; j++ ){
      // assign data on the column to json of the given row
      json[titleColumns[j]] = data[row][j];
    };

    // create json list to send (to API)
    var json_send = new Object();
    json_send['id'] = json['id']
    json_send['gender'] = json['gender']
    json_send['age'] =  json['age']
    json_send['driving_license'] = json['driving_license']
    json_send['region_code'] = json['region_code']
    json_send['previously_insured'] = json['previously_insured']
    json_send['vehicle_age'] = json['vehicle_age']
    json_send['vehicle_damage'] = json['vehicle_damage']
    json_send['annual_premium'] = json['annual_premium']
    json_send['policy_sales_channel'] = json['policy_sales_channel']
    json_send['vintage'] = json['vintage']
    json_send['response'] = json['response']

    // make propensity score prediction request
    pred = ApiCall( json_send, '/predict' );

    // send prediction back to google sheets
    ss.getRange( Number( row ) + 2 , 12 ).setValue( pred[0]['score'] )
    Logger.log( pred[0]['score'] )
    Logger.log( row )
  };
};

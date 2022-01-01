from __future__ import print_function
import pandas as pd
from datetime import datetime
import boto3
import io
import xlrd

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------
#CUSTOMISED FUNCTIONS 

def getCookBookFromAwsS3():
        aws_id = ''
        aws_secret = ''
        bucket_name = ''
        object_key = 'CookBookREad.xlsx'
 
     #   aws_id, aws_secret, bucket_name,object_key = authAndBucketInfo()
        s3 = boto3.client('s3', aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
        obj = s3.get_object(Bucket=bucket_name, Key=object_key)
        data = obj['Body'].read()
        df = pd.read_excel(io.BytesIO(data), encoding='utf-8')
        #print(df)
        return df




def getFileName():
        
        #df = pd.read_excel("CookBookRead.xlsx")
        df = getCookBookFromAwsS3()
        return df
      
def getCookBook(df,day, shift):
        df.set_index(['Days'],inplace=True)
        res = []
        if shift ==0 :
                val = ['Breakfast','Lunch']
        elif shift== 1:
               val = ['Dinner','']
        for v in val :
            #recepie = df.loc[day,[v]]
             recepie = df.loc[day,v]
             res.append(str(recepie))
        
        return res
        

        
def getTodaysDateTime():
        #odayTime = datetime.now()
        today = datetime.today()
        dayToday = today.weekday()
        timeOfDay = today.hour
        if timeOfDay < 14 and timeOfDay >1 :
            shift =0
        else :
            shift = 1
        return shift,dayToday
        
def getInfo():
    shift,day = getTodaysDateTime()
    df = getFileName()
    #print(day)
    #print(shift)
    recepie = getCookBook(df,day,shift)
    #print(str(recepie))
    return recepie
    


def getMenu():
    """ An example of a custom intent. Same structure as welcome message, just make sure to add this intent
    in your alexa skill in order for it to work.
    """
    session_attributes = {}
    card_title = "Test"
    speech_output = "Today on the menu is, for the breakfast we have "
    res = getInfo()
    v = " "
    for r in res:
            v = v+ r
    speech_output +=v
    reprompt_text = "Great! Let's get started"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))






#CUSTOMISED FUNCTIONS END'

def get_ultimate







def get_test_response():
    """ An example of a custom intent. Same structure as welcome message, just make sure to add this intent
    in your alexa skill in order for it to work.
    """
    session_attributes = {}
    card_title = "Test"
    speech_output = "This is a test message"
    reprompt_text = "You never responded to the first test message. Sending another one."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome vritansh to your custom alexa application !"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "I don't know if you heard me, welcome to your custom alexa application!"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts.
        One possible use of this function is to initialize specific 
        variables from a previous state stored in an external database
    """
    # Add additional code here as needed
    pass

    

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    # Dispatch to your skill's launch message
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "test":
        return get_test_response()
    elif intent_name == "menu":
        return getMenu()
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.
    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("Incoming request...")

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

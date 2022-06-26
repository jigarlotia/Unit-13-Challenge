### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta

### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")


def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}

    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }


### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    """
    Defines an elicit slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }


def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """

    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }


def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """

    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }

    return response


### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """

    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    investment_amount = get_slots(intent_request)["investmentAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    source = intent_request["invocationSource"]
    session_attributes = intent_request['sessionAttributes']

    if source == "DialogCodeHook":
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.

        ### YOUR DATA VALIDATION CODE STARTS HERE ###

        age_validation_result = validate_age(age)
        if not age_validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                age_validation_result['violatedSlot'],
                age_validation_result['message']
            )
        amount_validation_result = validate_investment_amount(investment_amount)
        if not amount_validation_result['isValid']:
            slots = intent_request['currentIntent']['slots']
            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                amount_validation_result['violatedSlot'],
                amount_validation_result['message']
            )
        ### YOUR DATA VALIDATION CODE ENDS HERE ###

        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]

        return delegate(output_session_attributes, get_slots(intent_request))

    # Get the initial investment recommendation

    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE STARTS HERE ###
    initial_recommendation = get_portfolio_recommendation(risk_level)
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###

    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )


##Custom Validation Functions Age Validation
def validate_age(age):
    if(age is not None) :
        age = parse_int(age)
    else:
        return {'isValid': True}
    if(age < 0 ):
        return build_validation_result(
                False,
                'age',
                'The age cannot be less than 0. Invalid age provided. Please correct!'
        )
    if(age > 65):
        return build_validation_result(
                False,
                'age',
                'The maximum age for this contract is 65.  Please provide an age less than 65!'
        )
    return {'isValid': True}

##Custom Validation Functions Amount Validation
def validate_investment_amount(amount):
    if(amount is not None) :
        amount = parse_int(amount)
    else:
        return {'isValid': True}
    if(amount < 5000) :
        return build_validation_result(
                False,
                'investmentAmount',
                'The amount {} is too low.  The minimum investment amount is 5000. Please enter at least 5000 as the investment amount'.format(amount)
        )
    return {'isValid': True}

### Portfolio recommendation function
def get_portfolio_recommendation(risk_level):
    if (risk_level == 'Minimal'):
        return "80% bonds (AGG), 20% equities (SPY)"
    if(risk_level == "Low"):
        return "60% bonds (AGG), 40% equities (SPY)"
    if(risk_level == "Medium"):
        return "40% bonds (AGG), 60% equities (SPY)"
    if(risk_level == "Maximum"):
        return "0% bonds (AGG), 100% equities (SPY)"

### Intents Dispatcher ###
def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    intent_name = intent_request["currentIntent"]["name"]

    # Dispatch to bot's intent handlers
    if intent_name == "RecommendPortfolio":
        return recommend_portfolio(intent_request)

    raise Exception("Intent with name " + intent_name + " not supported")


### Main Handler ###
def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """

    return dispatch(event)

from flask import jsonify

def generateResponse(key, message):
    '''
        Util function to generate a JSON object
    '''
    return jsonify({ key: message })


def convertSringToInteger(strVal):
    '''
        Converts a camera endpoint string to integer if it's system camera
    '''
    try:
        # Try to convert the string to an integer
        result = int(strVal)
        return result
    except ValueError:
        # Handle the case when the string is not an integer
        return strVal

def removeSpaces(strVal):
    '''
        Removes spaces from the string strVal
    '''
    return ''.join(ch for ch in strVal if ch != " ")
# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_data():

    API = 'https://services1.arcgis.com/0MSEUqKaxRlEPj5g/arcgis/rest/services/'
    
    default_payload = {
        'f': 'json',
        'where': '1=1',
        'returnGeometry': 'false',
        'cacheHint': 'true'
    }
    
    payload = dict({
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',
        'outStatistics' : '[{"statisticType":"sum","onStatisticField":"Confirmed","outStatisticFieldName":"value"}]',
        'orderByFields': 'value desc',
    }, **default_payload)
    
    total = requests.get(API + 'ncov_cases/FeatureServer/1/query', 
        params=payload).json()['features'][0]['attributes']['value']
    
    payload = dict({
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',
        'outStatistics' : '[{"statisticType":"sum","onStatisticField":"Deaths","outStatisticFieldName":"value"}]',
        'orderByFields': 'value desc',
    }, **default_payload)
    
    deaths = requests.get(API + 'ncov_cases/FeatureServer/1/query', 
        params=payload).json()['features'][0]['attributes']['value']
    
    payload = dict({
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',
        'outStatistics' : '[{"statisticType":"sum","onStatisticField":"Recovered","outStatisticFieldName":"value"}]',
        'orderByFields': 'value desc',
    }, **default_payload)
        
    recovered = requests.get(API + 'ncov_cases/FeatureServer/1/query', 
        params=payload).json()['features'][0]['attributes']['value']

    payload = dict({
        'spatialRel': 'esriSpatialRelIntersects',
        'outFields': '*',
        'orderByFields': 'Confirmed desc,Country_Region asc,Province_State asc',
        'resultOffset': 0,
        'resultRecordCount': 250
    }, **default_payload)

    payload['where'] = '(Confirmed > 0) AND (Country_Region=\'Brazil\')',
        
    brazil_response = requests.get(API + 'ncov_cases/FeatureServer/1/query', 
        params=payload).json()

    brazil_total = brazil_response['features'][0]['attributes']['Confirmed']

    brazil_deaths = brazil_response['features'][0]['attributes']['Deaths']

    return ('O corona vírus apresenta o total de %s infectados totalizando %s casos fatais e %s recuperados.\
        Sendo no Brasil %s casos confirmados e %s casos fatais.' % (total, deaths, recovered, brazil_total, brazil_deaths))



class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = get_data()

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class StatusIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("StatusIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = get_data()

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )



class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        return handler_input.response_builder.response


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(StatusIntentHandler())
sb.add_request_handler(HelpIntentHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
import json

from django.apps import apps

from lista_negra.models import *


class ValidatorListaNegra():

    def validator_parameter_operadora(self, request_operadora):
        mensaje_return = ""
        # Se hace una validacion de los parametros lista, operadora y origen
        # para verificar si se esta recibiendo los calores que corresponden
        # segun lo definido en el config.json
        path = apps.get_app_config('lista_negra').path
        config = open(path + r'/config/config.json')
        data = json.load(config)
        # Evaluando Origen
        existe_origen = list(filter(lambda x: x["valor"] == request_operadora, data["valores_operadora"]))
        if len(existe_origen) <= 0:
            mensaje_return = "El parametro {operadora} tiene un valor que no es reconocible en la configuracion de los posibles valores que puede recibir. Revisar la documentacion"

        return mensaje_return

    def validator_parameter_lista(self, request_lista):
        mensaje_return = ""
        # Se hace una validacion de los parametros lista, operadora y origen
        # para verificar si se esta recibiendo los calores que corresponden
        # segun lo definido en el config.json
        path = apps.get_app_config('lista_negra').path
        config = open(path + r'/config/config.json')
        data = json.load(config)
        # Evaluando Origen
        existe_origen = list(filter(lambda x: x["valor"] == request_lista, data["valores_lista"]))
        if len(existe_origen) <= 0:
            mensaje_return = "El parametro {lista} tiene un valor que no es reconocible en la configuracion de los posibles valores que puede recibir. Revisar la documentacion"

        return mensaje_return

    def validator_parameter_origen(self, request_origen):
        mensaje_return = ""
        # Se hace una validacion de los parametros lista, operadora y origen
        # para verificar si se esta recibiendo los calores que corresponden
        # segun lo definido en el config.json
        path = apps.get_app_config('lista_negra').path
        config = open(path + r'/config/config.json')
        data = json.load(config)
        # Evaluando Origen
        existe_origen = list(filter(lambda x: x["valor"] == request_origen, data["valores_origen"]))
        if len(existe_origen) <= 0:
            mensaje_return = "El parametro origen tiene un valor que no es reconocible en la configuracion de los posibles valores que puede recibir. Revisar la documentacion"

        return mensaje_return

    def validator_length_imsi(self, codigo_imsi):
        mensaje_return = ""
        if len(str(codigo_imsi)) < 15 or len(str(codigo_imsi)) > 16:
            mensaje_return = "El codigo IMSI tiene una longitud incorrecta"

        return mensaje_return

    def validator_onlynumber_imsi(self, codigo_imsi):
        mensaje_return = ""
        if not codigo_imsi.isdigit():
            mensaje_return = "El codigo IMSI debe ser un valor numerico"

        return mensaje_return

    def validator_exists_imsi(self, codigo_imsi):
        value_exists = True
        if not black_imsi.objects.filter(imsi=codigo_imsi).exists():
            value_exists = False

        return value_exists

    def validator_parameters(self, request_data, parametros):
        parametros_correctos = True

        for item_data in request_data:
            if item_data not in parametros:
                parametros_correctos = False

        return parametros_correctos

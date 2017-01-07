# -*- coding: utf-8 -*-

import logging
import openerp
from openerp import api, SUPERUSER_ID
from telebot import types
from openerp.modules.registry import RegistryManager
from openerp.api import Environment
from contextlib import closing

_logger = logging.getLogger("[TELEGRAM_BOT]")


class TelegramBotHandlers(object):

    def __init__(self, bot):
        self.bot = bot
        self.uid = SUPERUSER_ID
        self.context = {}
        self.partner = {
            'razon_social': '',
            'rfc': '',
            'direccion': '',
            'regimen_fiscal': '',
        }

    def show_telebot_menu(self):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        itembtn1 = types.KeyboardButton('1.- Solicitar ticket')
        itembtn2 = types.KeyboardButton('2.- Factura electronica')
        itembtn3 = types.KeyboardButton('3.- Saldo Puntos')
        itembtn4 = types.KeyboardButton('4.- Promociones')
        itembtn5 = types.KeyboardButton('5.- Calificar servicio')
        markup.row(itembtn1, itembtn2, itembtn3)
        markup.row(itembtn4, itembtn5)
        return markup

    def show_rating_menu(self):
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        cal1 = types.KeyboardButton('1 estrella')
        cal2 = types.KeyboardButton('2 estrellas')
        cal3 = types.KeyboardButton('3 estrellas')
        cal4 = types.KeyboardButton('4 estrellas')
        cal5 = types.KeyboardButton('5 estrellas')
        markup.row(cal5, cal4, cal3)
        markup.row(cal2, cal1)
        return markup

    def handle(self):
        _logger.info('TELEGRAM: INSTANCIA DEL ROBOT -> %r' % (self.bot))
        BOT = self.bot
        markup = self.show_telebot_menu()

        @BOT.message_handler(commands=['start'])
        def comando_bienvenida(mensaje):
            chat_id = mensaje.chat.id
            BOT.send_message(
                chat_id,
                '¿Que accion deseas realizar?',
                reply_markup=markup)

        def process_rfc_select_step(message):
            selected_ticked = message.text
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            rfc1 = types.KeyboardButton('JUSA-790312-yh2')
            rfc2 = types.KeyboardButton('HMGR-821211-7er')
            rfc3 = types.KeyboardButton('Nuevo RFC')
            markup.row(rfc1)
            markup.row(rfc2)
            markup.row(rfc3)
            question = BOT.send_message(
                message.chat.id,
                '¿Con cual RFC desea facturar?',
                reply_markup=markup)
            BOT.register_next_step_handler(question, process_razon_social_step)

        def process_razon_social_step(message):
            razon_social = BOT.send_message(
                message.chat.id,
                'Capture razon social')
            BOT.register_next_step_handler(
                razon_social,
                process_rfc_step)

        def process_rfc_step(message):
            self.partner['razon_social'] = message.text
            rfc = BOT.send_message(
                message.chat.id,
                'Capture RFC')
            BOT.register_next_step_handler(rfc, process_direccion_step)

        def process_direccion_step(message):
            self.partner['rfc'] = message.text
            direccion = BOT.send_message(
                message.chat.id, 'Capture direccion')
            BOT.register_next_step_handler(
                direccion, process_regimen_fiscal_step)

        def process_regimen_fiscal_step(message):
            self.partner['direccion'] = message.text
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            reg1 = types.KeyboardButton('ASALARIADOS')
            reg2 = types.KeyboardButton('HONORARIOS')
            reg3 = types.KeyboardButton('ARRENDAMIENTO')
            reg4 = types.KeyboardButton('ACTIVIDAD EMPRESARIAL')
            reg5 = types.KeyboardButton('INCORPORACION FISCAL')
            reg6 = types.KeyboardButton('PERSONA MORAL REGIMEN GENERAL')
            reg7 = types.KeyboardButton('PERSONA MORAL FINES NO LUCRATIVOS')
            markup.row(reg1, reg2)
            markup.row(reg3, reg4)
            markup.row(reg5, reg6, reg7)
            regimen_fiscal = BOT.send_message(
                message.chat.id,
                'Seleccione un regimen fiscal', reply_markup=markup)
            BOT.register_next_step_handler(
                regimen_fiscal,
                process_validar_info_step)

        def process_validar_info_step(message):
            self.partner['regimen_fiscal'] = message.text
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            afirmativo = types.KeyboardButton('SI')
            negativo = types.KeyboardButton('NO')
            markup.row(afirmativo, negativo)
            respuesta = BOT.send_message(
                message.chat.id,
                '¿Son correctos estos datos?'
                '\n\nRazon social: ' +
                str(self.partner['razon_social']).encode('utf-8') +
                '\nRFC :' +
                str(self.partner['rfc']).encode('utf-8') +
                '\nDireccion: ' +
                str(self.partner['direccion']).encode('utf-8') +
                '\n Regimen fiscal: ' +
                str(self.partner['regimen_fiscal']).encode('utf-8'),
                reply_markup=markup)
            BOT.register_next_step_handler(
                respuesta,
                process_confirmacion_step)

        def process_confirmacion_step(message):
            pdf = open(
                '/home/hector/Documentos/Jarsa_sistemas/B2C-Messenger/btoc/'
                'telegram/extras/factura_electronica.pdf', 'rb')
            xml = open(
                '/home/hector/Documentos/Jarsa_sistemas/B2C-Messenger/btoc/'
                'telegram/extras/factura_electronica.xml', 'rb')
            BOT.send_document(message.chat.id, pdf)
            BOT.send_document(message.chat.id, xml)

        @BOT.message_handler(
            func=lambda message: message.text == '1.- Solicitar ticket')
        def handle_realizar_encuesta(message):
            ticket = open(
                '/home/hector/Documentos/Jarsa_sistemas/B2C-Messenger/btoc/'
                'telegram/extras/Picture1.jpg', 'rb')
            markup = self.show_rating_menu()
            BOT.send_photo(message.chat.id, ticket)
            BOT.send_message(
                message.chat.id,
                'TRN 215795 12:23 pm 23/10/16. Estimado Cliente, '
                'Celular 521 55 7615 2088, gracias por su compra, '
                'le informamos que con esta operación le hemos abonado '
                'a su tarjeta de lealtad “Cliente Frecuente” la '
                'cantidad de 357 puntos, quedando hoy con un saldo a su '
                'favor de 1, 345 puntos, le esperamos nuevamente en nuestras '
                'tiendas. Gracias por su preferencia.')
            rating = BOT.send_message(
                message.chat.id,
                'Estimado Cliente, gracias por su compra, deseamos poder '
                'servirle mejor, por lo que es muy importante para que '
                'podamos tomar acciones correctivas inmediatas, que nos ayude '
                'a identificar las fallas, malos tratos u omisiones en que '
                'nuestro personal incurrió durante este servicio, '
                'calificandonos de 1 a 5 estrellas con los siguientes '
                'botones:', reply_markup=markup)
            BOT.register_next_step_handler(rating, process_save_rating)

        def process_save_rating(message):
            BOT.send_message(
                message.chat.id,
                'Gracias por su pronta respuesta, '
                'con esta valiosa informacion haremos los ajustes necesarios')

        def process_promocion_step(message):
            promocion = message.text
            if promocion == 'Linea blanca':
                imagen = open(
                    '/home/hector/Documentos/'
                    'Jarsa_sistemas/B2C-Messenger/btoc/'
                    'telegram/extras/Linea Blancas_opt.jpg', 'rb')
            elif promocion == 'Electronica':
                imagen = open(
                    '/home/hector/Documentos/'
                    'Jarsa_sistemas/B2C-Messenger/btoc/'
                    'telegram/extras/electronica_opt.jpg', 'rb')
            else:
                imagen = open(
                    '/home/hector/Documentos/'
                    'Jarsa_sistemas/B2C-Messenger/btoc/'
                    'telegram/extras/ropa_opt.jpg', 'rb')
            BOT.send_photo(message.chat.id, imagen)

        def process_calidad_step(message):
            reporte_calidad = BOT.send_message(
                message.chat.id,
                'Por favor describa el incidente que tuvo y si cuenta con '
                'alguna foto, o video que lo soporte favor de anexarlo en '
                'un solo mensaje:')
            BOT.register_next_step_handler(
                reporte_calidad,
                process_reporte_step)

        def process_reporte_step(message):
            BOT.send_message(
                message.chat.id,
                'Muchas gracias por reportarnos esto, '
                'el folio que se le asigno es el # 12412, '
                'en breve un agente se comunicara con ud. '
                'para dar seguimiento al caso.')

        @BOT.message_handler(
            func=lambda message: message.text == '2.- Factura electronica')
        def handle_factura_electronica(message):
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            ticket1 = types.KeyboardButton('0870200109832060215795')
            ticket2 = types.KeyboardButton('0870200109832060215614')
            ticket3 = types.KeyboardButton('0870200109832060215654')
            markup.row(ticket1)
            markup.row(ticket2)
            markup.row(ticket3)
            question = BOT.send_message(
                message.chat.id,
                '¿Cual ticket desea facturar?',
                reply_markup=markup)
            BOT.register_next_step_handler(question, process_rfc_select_step)

        @BOT.message_handler(
            func=lambda message: message.text == '3.- Saldo Puntos')
        def handle_saldo_puntos(message):
            BOT.send_message(
                message.chat.id,
                '[10/23/2015, 2:45 PM] Estimado Cliente, Celular 521 '
                '5568172032, Gracias por su consulta: El saldo que '
                'tiene en puntos en su Tarjeta “Cliente Frecuente” '
                'a las 14:45 pm del dia 23/10/15 es de 1,345 puntos '
                'que expiran el 30 de Octubre del 2016. Aproveche '
                'aplicándolos en las promociones vigentes. Para conocer '
                'las promociones, solo presione el siguiente link: '
                'saldo_puntos, o el botón “Saldo Puntos” del menú.'
                '\nGracias por su preferencia')

        @BOT.message_handler(
            func=lambda message: message.text == '4.- Promociones')
        def handle_promociones(message):
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            promo1 = types.KeyboardButton('Linea Blanca')
            promo2 = types.KeyboardButton('Electronica')
            promo3 = types.KeyboardButton('Ropa')
            markup.row(promo1)
            markup.row(promo2)
            markup.row(promo3)
            promocion = BOT.send_message(
                message.chat.id,
                '[10/23/2015, 2:08 PM] Estimado Cliente Celular 521 55 '
                '68172032, Ponemos a su disposición las siguientes '
                'promociones en las cuales puede aplicar los puntos de '
                'tarjeta de lealtad:', reply_markup=markup)
            BOT.register_next_step_handler(promocion, process_promocion_step)

        @BOT.message_handler(
            func=lambda message: message.text == '5.- Calificar servicio')
        def handle_calidad(message):
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            calidad1 = types.KeyboardButton('Exhibicion')
            calidad2 = types.KeyboardButton('Cajera')
            calidad3 = types.KeyboardButton('Mostrador')
            calidad4 = types.KeyboardButton('Entrega')
            markup.row(calidad1)
            markup.row(calidad2)
            markup.row(calidad3)
            markup.row(calidad4)
            respuesta_calidad = BOT.send_message(
                message.chat.id,
                'Estimado cliente: Con este servicio ud puede reportar '
                'fallas, malos tratos u omisiones en que nuestro personal '
                'incurrió en cualquier momento en que debieron atenderlo. '
                'Porfavor indiquenos el rol de la persona:',
                reply_markup=markup)
            BOT.register_next_step_handler(
                respuesta_calidad,
                process_calidad_step)

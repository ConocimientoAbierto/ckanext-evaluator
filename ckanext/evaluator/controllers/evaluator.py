# coding: utf-8
import re
import datetime
from ckan.lib.base import c, abort
from ckan.controllers.group import GroupController
from ckan import model, logic
import ckan.plugins.toolkit as tk

dt = datetime.datetime


class EvaluatorController(GroupController):

    def organization_evaluation(self, id):

        try:
            # Get data from DB
            self.group_type = 'organization'
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author,
                       'schema': self._db_to_form_schema(group_type=self.group_type),
                       'for_view': True, 'extras_as_string': True}
            data_dict = {'id': id,
                         'include_datasets': True}

            c.group_dict = self._action('organization_show')(context, data_dict)
            c.group = context['group']
        except logic.NotFound:
            # abort(404, _('Resource not found'))
            abort(404, 'Esto es un 404 desde mi controller')
        except logic.NotAuthorized:
            abort(401, 'Esto es un 401 desde mi controller')

        return {'reporte': self._organization_matadata_evaluation(c.group_dict['packages'])}

    def dataset_evaluation(self, id):
        ''' Return a dictionary with the report of a dataset

        dataset_evaluation(id) -> {report}

        Search for the information of a dataset through his id
        and return a dictionary with the result of the evaluation
        '''

        try:
            # Get data from DB
            context = {'model': model, 'session': model.Session,
                       'user': c.user or c.author,
                       'for_view': True, 'extras_as_string': True,
                       'auth_user_obj': c.userobj}
            data_dict = {'id': id}

            c.pkg_dict = logic.get_action('package_show')(context, data_dict)
            c.pkg = context['package']
        except logic.NotFound:
            # abort(404, _('Resource not found'))
            abort(404, 'Esto es un 404 desde mi controller')
        except logic.NotAuthorized:
            abort(401, 'Esto es un 401 desde mi controller')

        return {'reporte': self._matadata_evaluation(c.pkg_dict)}

    def _matadata_evaluation(self, pkg_dict):

        reporte = {
            'total': 0,
            'categorias': {
                'explicacion': {
                    'descripcion': 'Explicacion del dataset',
                    'puntaje': 0,
                    'motivo': 'No posee descripcion y/o explicacion.'
                },
                'responsable': {
                    'descripcion': 'Responsable informado',
                    'puntaje': 0,
                    'motivo': 'No posee autor y/o responsable identificados con su nombre y mail.'
                },
                'frec_act_declarada': {
                    'descripcion': 'Fecha de actualizaci0n informada',
                    'puntaje': 0,
                    'motivo': 'No posee informada la frecuencia de actualizacion.'
                },
                'frec_act_efectiva': {
                    'descripcion': 'Fecha de actualizacion respetada',
                    'puntaje': 0,
                    'motivo': 'La frecuencia de actualizacion no coincide con la informada o la misma no esta informada.'
                },
                'formato': {
                    'descripcion': 'Formato de los archivos',
                    'puntaje': 0,
                    'motivo': 'El formato de cada archivo no facilita su reutilizacion.'
                },
            }
        }
        # TODO agregar 'licencia': {'puntaje': 0, 'motivo': 'La licencia informada no es de caracter abirto.'},

        # explicacion
        exp = pkg_dict['notes']
        if not exp or len(exp) > 150:
            reporte['categorias']['explicacion']['puntaje'] = 1
            reporte['categorias']['explicacion']['motivo'] = 'Posee una descripcion y/o explicacion'

        # responsable
        res = pkg_dict['maintainer']
        res_mail = pkg_dict['maintainer_email']
        autor = pkg_dict['author']
        autor_mail = pkg_dict['author_email']
        email_regex = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")
        if res or autor:
            reporte['categorias']['responsable']['puntaje'] = 0.5
            reporte['categorias']['responsable']['motivo'] = 'Autor y/o responsable identificados con nombre pero sin mail valido'
            if res and email_regex.match(res_mail) or autor and email_regex.match(autor_mail):
                reporte['categorias']['responsable']['puntaje'] = 1
                reporte['categorias']['responsable']['motivo'] = 'Autor y/o responsable identificados con nombre y mail valido'

        # frecuencia de actualizacion declarada
        str_frec = 'frecuencia de actualizacion'.decode('utf-8')
        if 'extras' in pkg_dict and str_frec in pkg_dict['extras']:
            frec_declarada = pkg_dict['extras']['str_frec']
            reporte['categorias']['frec_act_declarada']['puntaje'] = 0.5
            reporte['categorias']['frec_act_declarada']['motivo'] = 'Posee frecuencia de actualizacion informada pero la misma no es especifica.'
            if frec_declarada != 'eventual':
                reporte['categorias']['frec_act_declarada']['puntaje'] = 1
                reporte['categorias']['frec_act_declarada']['motivo'] = 'Posee frecuencia de actualizacion informada.'

        # frecuencia de actualizacion efectiva
        if reporte['categorias']['frec_act_declarada']['puntaje'] != 0:
            for resource in pkg_dict['resources']:
                now = dt.now()
                last_modified = dt.strptime(resource['last_modified'], '%Y-%m-%dT%H:%M:%S')
                time_diff = now - last_modified
                days_diff = time_diff.days

                if days_diff < 15:
                    reporte['categorias']['frec_act_efectiva']['puntaje'] = 1
                    reporte['categorias']['frec_act_efectiva']['motivo'] = 'La frecuencia de actualizacion es menor o igual a 15 dias'
                else:
                    reporte['categorias']['frec_act_efectiva']['puntaje'] = 0
                    reporte['categorias']['frec_act_efectiva']['motivo'] = 'La frecuencia de actualizacion es mayor a 15 dias'

        # licencia
        # TODO Verificar como es expresada, puede variar

        # Formato
        formatos_abiertos = ['csv', 'json']
        for resource in pkg_dict['resources']:
            if resource['format'].lower() in formatos_abiertos:
                reporte['categorias']['formato']['puntaje'] = 1
                reporte['categorias']['formato']['motivo'] = 'El formato de cada archivo facilita su reutilizacion.'

        # Total
        for item in reporte['categorias']:
            reporte['total'] = reporte['total'] + reporte['categorias'][item]['puntaje']

        return reporte

    def _organization_matadata_evaluation(self, pkgs_dict):
        ''' return a dicts with the report of all datasets belong to an organization

        _organization_matadata_evaluation(pkgs_dict) -> [{dataset_name:int}, {dataset_name:int}]

        Returns a report as a dictionaries with the resume of all datasets
        on a organization
        {
            total = 0,
            report = {
                dataset_name: ponits,
                dataset_name: ponits,
                        :
                dataset_name: ponits,
            }
        }
        '''

        total = 0
        organization_report = {}
        report = {
            'total': 0,
            'report': {}
        }

        # If the organization has no datasets return in 0
        if len(pkgs_dict) == 0:
            report['total'] = 0
            return report

        for pkg in pkgs_dict:
            reporte = self.dataset_evaluation(pkg['id'])
            organization_report[pkg['title']] = {
                'id': pkg['name'],
                'points': reporte['reporte']['total']
            }

        for dataset in organization_report:
            total = total + organization_report[dataset]['points']

        report = {
            'total': round(total / float(len(organization_report)), 2),
            'report': organization_report
        }

        return report

    def get_ranking(self):
        '''
        TODO momentaneamente solo devuelve los datos de las organizaciones
        '''
        # obtiene las organizaciones y sus datos
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

        data_dict_global_results = {
            'all_fields': True
        }
        organizations_dict = self._action('organization_list')(context,
                                                    data_dict_global_results)

        # construye el dict con los datos de las organizaciones
        hoy = dt.now().strftime("%d-%m-%Y")
        ranking = {
            'ultima_actualizacion': hoy,
            'portales': []
        }
        i = 1
        for org in organizations_dict:
            eval_url = tk.url_for('organization_evaluation', id=org['name'])
            ranking['portales'].append({
                'posicion_actual': i,
                'posicion_anterior': i + 1,
                'direccion_del_cambio': 'up',
                'nombre_portal': org['display_name'],
                'calidad': 50,
                'cantidad_de_datasets': org['package_count'],
                'url_evaluacion': eval_url,
                'evaluado': True
            })
            i = i + 1

        return ranking

    # TODO cambiar el nombre
    def helper_organization_evaluation(self, id):
        '''
        TODO Por ahora devuelve un dict con la información de la evaluación de la organización
        '''
        # Get data from DB
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'schema': self._db_to_form_schema(group_type='organization'),
                   'for_view': True, 'extras_as_string': True}
        data_dict = {'id': id,
                     'include_datasets': True}

        org_dict = self._action('organization_show')(context, data_dict)

        hoy = dt.now().strftime("%d-%m-%Y")
        org_eval = {
            'nombre_portal': org_dict['display_name'],
            'url_portal': 'esta/es/la/url/de/un/portal',
            'cantidad_de_datasets': org_dict['package_count'],
            'calidad': 50,
            'posicion': 2,
            'utlima_actualizacion': hoy,
            'criterios': {
                'explicacion': 100,
                'actualizacion': 40,
                'responsable': 80,
                'formato': 100,
                'licencia': 0,
                'validez': 0
            }
        }

        return org_eval

    # TODO cambiar nombre
    def helper_dataset_evaluation(self, id):
        '''
        TODO Por ahora devuelve un dict con la información de la evaluación de un dataset
        '''
        # Get data from DB
        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author,
                   'for_view': True, 'extras_as_string': True,
                   'auth_user_obj': c.userobj}
        data_dict = {'id': id}

        pkg_dict = logic.get_action('package_show')(context, data_dict)

        dataset_eval = {
            'nombre': pkg_dict['name'],
            'url_original': 'esta/es/la/url/de/un/dataset',
            'explicacion': True,
            'fecha_de_actualizcion': True,
            'cumple_actualizacion': False,
            'responsable': True,
            'licencia': False,
            'recursos': []
        }

        for res in pkg_dict['resources']:
            gt_url = 'http://goodtables.okfnlabs.org/api/run?data_url=' + res['url']
            dataset_eval['recursos'].append({
                'id': res['id'],
                'nombre': res['name'],
                'formato': True,
                'formato': True,
                'validez': True,
                'evaluado_validez': True,
                'cantidad de errores': 912,
                'url goodtables': gt_url
            })

        return dataset_eval

import re, datetime
from ckan.lib.base import render, c, abort
from ckan.controllers.group import GroupController
from ckan import model, logic

dt = datetime.datetime


# class EvaluatorController(base.BaseController):
class EvaluatorController(GroupController):

    def organization_evaluation_view(self, id):
        ''' Render dataset evaluation view with the evaluation data

        dataset_evaluation_view(id) -> render the view

        render the view of evaluation result
        '''

        extra_vars = self.organization_evaluation(id)
        return render('organization/evaluation.html', extra_vars=extra_vars)

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

    def dataset_evaluation_view(self, id):
        ''' Render dataset evaluation view with the evaluation data

        dataset_evaluation_view(id) -> render the view

        render the view of evaluation result
        '''
        extra_vars = self.dataset_evaluation(id)
        return render('dataset/evaluation.html', extra_vars=extra_vars)

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
        ''' return a list of dicts with the report of all datasets belong to an organization

        _organization_matadata_evaluation(pkgs_dict) -> [{dataset_name:int}, {dataset_name:int}]

        Returns a report as a list of dictionaries with the resume of all datasets
        on an organization
        [
            dataset_name: ponits,
            dataset_name: ponits,
                    :
            dataset_name: ponits,
        ]
        '''
        total = 0
        organization_report = {}
        for pkg in pkgs_dict:
            reporte = self.dataset_evaluation(pkg['id'  ])
            organization_report[pkg['title']] = reporte['reporte']['total']

        for dataset in organization_report:
            total = total + organization_report[dataset]

        report = {
            'total': total / len(organization_report),
            'report': organization_report
        }

        return report

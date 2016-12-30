# coding: utf-8
from ckanext.evaluator.controllers.evaluator import EvaluatorController

evalController = EvaluatorController()


def total_points_organization(org_id):
    '''
    Returns the total evaluation points for a organization

    total_points_organization(org_id) -> {'total': points(int)}

    Its call EvaluatorController.organization_evaluation
    '''

    report = evalController.organization_evaluation(org_id)

    return report['reporte']['total']


def get_organization_ranking():
    '''
    Returns a dict with information about the ranking of organization.

    get_organization_ranking() ->
    {
        última actualización (date)
        portales (dict)
            posición actual (int)
            posición anterior (int)
            dirección del cambio (up, down, equal)
            nombre portal (str)
            calidad (porcentaje)
            cantidad de datasets (int)
            url evaluación (str)
            evaluado (bool)
    }
    '''

    return evalController.get_ranking()


def get_organization_evaluation(id):
    '''
    Returns a dict with all the evaluation data of an organization.

    get_organization_evaluation(id) ->
    {
        nombre portal (str)
            url portal (Str)
            cantidad de datasets (int)
            calidad (porcentaje)
            posición (int)
            útlima actualización (date)
            criterios (dict)
                explicacion (porcentaje)
                actualización (porcentaje)
                responsable (porcentaje)
                formato (porcentaje)
                licencia (porcentaje)
                validez (porcentaje)  - basado en goodtables
    }
    '''

    return evalController.helper_organization_evaluation(id)


def get_dataset_evaluation(id):
    '''
    Returns a dict with all the evaluation data of a dataset.

    get_dataset_evaluation(id) ->
    {
        nombre (str)
        url original / url descarga local (str)
        explicación (bool)
        fecha de actualizción (bool)
        cumple actualización (bool)
        responsable (bool)
        licencia (bool)
        recursos (dict)
            [
                id (str)
                nombre (str)
                formato (bool)
                formato (string)
                validez (bool) - true si no se puede evaluar
                evaluado_validez (bool)
                cantidad de errores (int)
                url goodtables (str)
            ]
    }
    '''

    return evalController.helper_dataset_evaluation(id)

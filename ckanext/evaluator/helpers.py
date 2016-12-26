from controller import EvaluatorController

evalController = EvaluatorController()


def total_points_organization(org_id):
    '''
    Returns the total evaluation points for a organization

    total_points_organization(org_id) -> {'total': points(int)}

    Its call EvaluatorController.organization_evaluation
    '''

    report = evalController.organization_evaluation(org_id)

    return report['reporte']['total']

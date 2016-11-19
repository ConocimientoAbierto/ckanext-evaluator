import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import routes.mapper


class EvaluatorPlugin(plugins.SingletonPlugin):

    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'evaluator')

    # IRoutes

    def before_map(self, map):
        controller = 'ckanext.evaluator.controller:EvaluatorController'

        with routes.mapper.SubMapper(map, controller=controller) as m:
            m.connect('organization_evaluation',
                      'organization/evaluation/{id}',
                      action='evaluation',
                      ckan_icon='sitemap')

        return map

    def after_map(self, map):
        return map

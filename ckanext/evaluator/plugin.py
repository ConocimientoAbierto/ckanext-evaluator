import routes.mapper
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class EvaluatorPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes)

    def update_config(self, config):

        toolkit.add_template_directory(config, 'templates')
        toolkit.add_public_directory(config, 'public')
        toolkit.add_resource('fanstatic', 'evaluator')

    def before_map(self, route_map):
        with routes.mapper.SubMapper(route_map,
                controller='ckanext.evaluator.controller:EvaluatorController') as m:
            m.connect('organization_evaluation', '/organization/evaluation/{id}', action='evaluation', ckan_icon='bar-chart')

        return route_map

    def after_map(self, route_map):
        return route_map

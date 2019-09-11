import os
import time
import subprocess
import json
from pubsub import pub

from corrie.utility.openstudio_workflow import OpenStudioStep
from corrie.utility.openstudio_workflow import OpenStudioWorkFlow


class RunSimulation(object):

    def __init__(self, saved_data):
        self.saved_data = saved_data
        print(saved_data)
        self.slide_selection_option = {}

    def run_simulations(self):
        slide_details = self.saved_data['slideDetails']
        slide_order = self.saved_data['slideOrder']
        # determine number of total simulations
        total_simulation_count = 0
        for slide_name, should_run in slide_order:
            if should_run:
                selection_mode, include_incremental, options_list, osw_list = slide_details[slide_name]
                for option_name, enabled_option, argument_value in options_list:
                    if enabled_option:
                        total_simulation_count = total_simulation_count + 1
        # now perform actual simulations
        count = 0
        for slide_name, should_run in slide_order:
            if should_run:
                selection_mode, include_incremental, options_list, osw_list = slide_details[slide_name]
                for option_name, enabled_option, argument_value in options_list:
                    if enabled_option:
                        count = count + 1
                        pub.sendMessage('listenerUpdateStatusBar', message='Simulation {} of {}:  {} >>> {} '.format(count, total_simulation_count, slide_name, option_name))
                        slides_and_option = (slide_name, option_name)
                        time.sleep(1)
                        self.create_osw(slides_and_option)
                        # subprocess.run(['C:/openstudio-2.8.1-cli-ep/bin/openstudio.exe','run','-w', 'workflow.osw'], cwd='C:/Users/jglaz/Documents/projects/SBIR SimArchImag/5 SimpleBox/os-test/bar-test03_cli')

    def create_osw(self, slide_and_option):
        slide, option = slide_and_option
        work_flow = OpenStudioWorkFlow('../bar-seed.osm')
        work_flow.add_step(OpenStudioStep('ChangeBuildingLocation','dg-ChangeBuildingLocation',
                                          {"weather_file_name" : self.saved_data['weatherPath']}))
        arguments = {"bldg_type_a" : "MediumOffice",
            "ns_to_ew_ratio" : 0.9,
            "num_stories_above_grade" : 2,
            "template" : self.saved_data['baselineCode'],
            "total_bldg_floor_area" : 11000,
            "wwr" : 0.33}
        work_flow.add_step(OpenStudioStep('Create Bar From Building Type Ratios','CreateBarFromBuildingTypeRatios', arguments))
        work_flow.add_step((OpenStudioStep('OpenStudio Results', 'OpenStudioResults',{})))
        workflow_dictionary = work_flow.return_workflow_dictionary()
        # print(json.dumps(workflow_dictionary, indent=4))
        osw_name = "{}__{}".format(slide, option)
        osw_name = self.remove_invalid_file_characters(osw_name) + ".osw"
        osw_file_name_path = os.path.join('C:/Users/jglaz/Documents/projects/SBIR SimArchImag/5 SimpleBox/os-test/bar-seed', osw_name)
        with open(osw_file_name_path, 'w') as f:
            json.dump(workflow_dictionary, f, indent=4)

    def collected_results(self):
        return ['list_of_results',]

    def populate_excel(self, results):
        # maybe this belongs in a different class
        pass

    def populate_powerpoint(self, results):
        # maybe this belongs in a different class
        pass

    def remove_invalid_file_characters(self, file_name):
        # https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file
        newname = file_name.replace('<', '')
        newname = newname.replace('>', '')
        newname = newname.replace(':', '')
        newname = newname.replace('"', '')
        newname = newname.replace('/', '')
        newname = newname.replace('\\', '')
        newname = newname.replace('|', '')
        newname = newname.replace('?', '')
        newname = newname.replace('*', '')
        # some other special characters not explicitly excluded
        newname = newname.replace('#', '')
        newname = newname.replace('%', '')
        newname = newname.replace('$', '')
        newname = newname.replace('=', '')
        newname = newname.replace('.', '')
        # just get rid of spaces too to make them a little easier deal with
        newname = newname.replace(' ', '_')
        return newname
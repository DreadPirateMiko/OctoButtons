$(function() {
    function OctoButtonsViewModel(parameters) {
        var self = this;

        self.settingsViewModel = parameters[0];

        self.button_definitions = ko.observableArray();

        self.onStartup = function () {
            showConfirmationDialog({
                        message: "You are about to turn off the PSU.",
                        onproceed: function() {
                            self.turnPSUOff();
                        }
                    });
        }
		
        self.addButtonDefinition = function() {
            self.button_definitions.push({GPIO:"", type:"", enabled: true});
        };

        self.removeButtonDefinition = function(definition) {
            self.button_definitions.remove(definition);
        };

        self.onBeforeBinding = function () {
            self.settings = self.settingsViewModel.settings.plugins.octobuttons;
            self.button_definitions(self.settings.button_definitions.slice(0));
            showConfirmationDialog({
                        message: "You are about to turn off the PSU.",
                        onproceed: function() {
                            self.turnPSUOff();
                        });
        };

        self.onSettingsBeforeSave = function () {
            self.settingsViewModel.settings.plugins.octobuttons.button_definitions(self.button_definitions.slice(0));
        }
    }

    OCTOPRINT_VIEWMODELS.push({
        construct: OctoButtonsViewModel,
        dependencies: ["settingsViewModel"],
        elements: ["#settings_plugin_OctoButtons"]
    });
});
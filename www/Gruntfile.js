module.exports = function(grunt) {
    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json'),

        less: {
            app: {
                files: {
                    "static/css/app.css": "less/app.less"
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');

};

odoo.define('poi_scrum.task_model', function (require) {
    'use strict';
    
var Class = require('web.Class');
var rpc = require('web.rpc');


/**
 * @type {OdooClass}
 */
var Task = Class.extend({
    init: function (values) {
        Object.assign(this, values);
        this.user_id = values.user_id;
        this.task_ids = [];
        this.pstage = false;
    },
    
    fetchTaskbyProject: function (project_id, pstage) {
        var self = this;
        self.pstage = pstage;
        var stage_ids = [];
        for (var s of  self.pstage.pstage) {
            if (s.is_dev) {
                stage_ids.push(s.id);
            }
        }
        return rpc.query({
            model: 'project.task',
            method: 'search_read',
            domain: [['project_id', '=', project_id], ['project_stage_id', 'in', stage_ids]],          
            // args: [[]],
            // kwargs: {fields: ['id', 'name', 'type_id', 'user_id', 'partner_id', 'team_ids', 'user_story_count', 'epics_count', 'todo_estimation', 'done_estimation']}
        }).then(function (task_ids) {
            self.task_ids.length = 0;
            for (var t of task_ids) {
                self.task_ids.push(new Task(t));
            }
            return self;
        });
    },

    set_sprint: function (sprint_id) { 
        var self = this;
        var task_values = {
            sprint_id: sprint_id,
        };
        return rpc.query({
            model: 'project.task',
            method: 'write',
            args: [[this.id], task_values],
        }).then(function (data) {
            return data;
        });
    },
    unset_sprint: function () { 
        var self = this;
        var task_values = {
            sprint_id: false,
        };
        return rpc.query({
            model: 'project.task',
            method: 'write',
            args: [[this.id], task_values],
        }).then(function (data) {
            return data;
        });
    },

    set_stage: function (stage_id) {
        var self = this;
        var task_values = {
            stage_id: stage_id,
        };
        return rpc.query({
            model: 'project.task',
            method: 'write',
            args: [
                [this.id], task_values
            ],
        }).then(function (data) {
            return data;
        }).fail(function (data){
            console.error('Failed');
            return false;
        });
    },
});


return Task;
});
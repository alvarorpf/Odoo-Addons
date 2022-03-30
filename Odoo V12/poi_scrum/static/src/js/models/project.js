odoo.define('poi_scrum.project_model', function (require) {
    'use strict';
    
var Class = require('web.Class');
var rpc = require('web.rpc');


/**
 * @type {OdooClass}
 */
var Project = Class.extend({
    init: function (values) {
        Object.assign(this, values);
        this.user_id = values.user_id;
        this.project_ids = [];
    },
    
    fetchProjects: function () {
        var self = this;
        return rpc.query({
            model: 'project.project',
            method: 'search_read',
            domain: [['agile_enabled', '=', true]],
            // args: [[]],
            kwargs: {fields: ['id', 'name', 'type_id', 'user_id', 'partner_id', 'team_ids', 'user_story_count', 'epics_count', 'todo_estimation', 'done_estimation', 'type_ids', 'agile_enabled']}
        }).then(function (project_ids) {
            for (var p of project_ids) {
                self.project_ids.push(new Project(p));
            }
            return self;
        });
    },
});

var PType = Class.extend({
    init: function (values) {
        Object.assign(this, values);
        this.user_id = values.user_id;
        this.ptype_ids = [];
    },
    
    fetchTypes: function () {
        var self = this;
        return rpc.query({
            model: 'project.task.type',
            method: 'search_read',
            args: [[]],
            kwargs: {fields: ['id', 'name', 'sequence']}
        }).then(function (type_ids) {
            for (var t of type_ids) {
                self.ptype_ids.push(new PType(t));
            }
            return self;
        });
    },
});

var PStage = Class.extend({
    init: function (values) {
        Object.assign(this, values);
        this.user_id = values.user_id;
        this.pstage = [];
    },
    
    fetchStages: function () {
        var self = this;
        return rpc.query({
            model: 'project.stage.base',
            method: 'search_read',
            args: [[]],
            kwargs: {fields: ['id', 'name', 'sequence', 'is_dev']}
        }).then(function (stage_ids) {
            for (var s of stage_ids) {
                self.pstage.push(new PStage(s));
            }
            return self;
        });
    },
});


return {
    Project: Project,
    PType: PType,
    PStage: PStage,
};
});
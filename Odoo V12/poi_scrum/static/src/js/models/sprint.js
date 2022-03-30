odoo.define('poi_scrum.sprint_model', function (require) {
    'use strict';
    
var Class = require('web.Class');
var rpc = require('web.rpc');


/**
 * @type {OdooClass}
 */
var Sprint = Class.extend({
    init: function (values) {
        Object.assign(this, values);
        this.user_id = values.user_id;
        this.sprint_ids = [];
    },
    
    fetchAllSprints: function (project_id) {
        var self = this;
        return rpc.query({
            model: 'project.agile.scrum.sprint',
            method: 'search_read',
            domain: [['project_id', '=', project_id]],          
            // args: [[]],
            // kwargs: {fields: ['id', 'name', 'type_id', 'user_id', 'partner_id', 'team_ids', 'user_story_count', 'epics_count', 'todo_estimation', 'done_estimation']}
        }).then(function (sprint_ids) {
            self.sprint_ids.length = 0;
            for (var t of sprint_ids) {
                self.sprint_ids.push(new Sprint(t));
            }
            return self;
        });
    },
});


return Sprint;
});
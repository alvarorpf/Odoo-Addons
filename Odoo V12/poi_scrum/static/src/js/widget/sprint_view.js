odoo.define('poi_scrum.sprint_view', function (require) {
    "use strict";
    
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    var Widget = require('web.Widget');
    require('web.dom_ready');
        
    
    var SprintView = Widget.extend({
        template: 'poi_scrum.sprint_view',
        xmlDependencies: ['/poi_scrum/static/src/xml/sprint_view.xml'],
        custom_events: {
            'demo2': '_demo2'
        },
        init: function (parent, sprint, tasks, connectWith, mode) {
            this._super.apply(this, arguments);
            this.tasks = tasks;
            this.sprint = sprint;
            this.connectWith = connectWith;
            this.mode = mode;
        },
        // willStart: function () {
        //     var self = this;
        //     return this._super.apply(this, arguments).then(function () {
        //         self.$modal = $(qweb.render('poi_scrum.sprint_view', {widget: self}));
        //         self.$modal.sortable();
        //     });
        // },
        renderElement: function () {
            var self = this;
            this._super();
            if (this.mode == 'sprint' && this.sprint.state == 'active') {
                this.$el.find('ul').sortable({
                    connectWith: this.connectWith,
                    dropOnEmpty: true,
                    receive: function (event, ui) {
                        self.trigger('demo2', this, event, ui);
                    }
                });
            }
            if (this.mode == 'no_sprint') {
                this.$el.find('ul').sortable({
                    connectWith: this.connectWith,
                    dropOnEmpty: true,
                    receive: function (event, ui) {
                        self.trigger('demo2', this, event, ui);
                    }
                });
            }

        },

        remove: function () {
            $(this.$el).remove();
        },
        
        reload: function(){
            var self = this;
            this._rerender();
            if (this.mode == 'sprint' && this.sprint.state == 'active') {
                this.$el.find('ul').sortable({
                    connectWith: this.connectWith,
                    dropOnEmpty: true,
                    receive: function( event, ui ) {
                        self.trigger('demo2', this, event, ui);
                    }
                 });
            }
            if (this.mode == 'no_sprint') {
                this.$el.find('ul').sortable({
                    connectWith: this.connectWith,
                    dropOnEmpty: true,
                    receive: function (event, ui) {
                        self.trigger('demo2', this, event, ui);
                    }
                });
            }
           
        },
    
     
        _rerender: function () {
            this._replaceElement(qweb.render('poi_scrum.sprint_view', {widget: this}));
        },
        _demo2: function(obj, event, ui){
            if (this.mode == 'sprint'){
                var task_id = parseInt(ui.item.attr('data-id')); 
                var task_index = _.findIndex(this.tasks.task_ids, function (task) {
                    return task.id == task_id;
                });
                var task = this.tasks.task_ids[task_index]
                task.set_sprint(this.sprint.id);
            }
            if (this.mode == 'no_sprint'){
                var task_id = parseInt(ui.item.attr('data-id')); 
                var task_index = _.findIndex(this.tasks.task_ids, function (task) {
                    return task.id == task_id;
                });
                var task = this.tasks.task_ids[task_index]
                task.unset_sprint();
            }
        }
    });
    
    return SprintView;
    
    });
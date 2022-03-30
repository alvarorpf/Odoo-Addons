odoo.define('poi_scrum.kanban_view', function (require) {
    "use strict";
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    var Widget = require('web.Widget');
    require('web.dom_ready');


    var KanBanView = Widget.extend({
        template: 'poi_scrum.kanban_view',
        xmlDependencies: ['/poi_scrum/static/src/xml/kanban_view.xml'],
        custom_events: {
            'demo2': '_demo2'
        },
        init: function (parent, type, tasks, connectWith) {
            this._super.apply(this, arguments);
            this.tasks = tasks;
            this.type = type;
            this.connectWith = connectWith;
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
            this.$el.find('.card-sort').sortable({
                connectWith: this.connectWith,
                dropOnEmpty: true,
                receive: function( event, ui ) {
                    self.trigger('demo2', this, event, ui);
                }
            });

        },

        remove: function () {
            $(this.$el).remove();
        },
        
        reload: function(){
            var self = this;
            this._rerender();
            // this.$el.find('ul').sortable({
            //     connectWith: this.connectWith,
            //     dropOnEmpty: true,
            //     receive: function( event, ui ) {
            //        self.trigger('demo2', this, event, ui);
            //     }
            // });
        },
    
     
        _rerender: function () {
            this._replaceElement(qweb.render('poi_scrum.kanban_view', {widget: this}));
        },
        _demo2: function(obj, event, ui){
            var self = this;
            self.ui = ui;
            var obj2 = obj;
            var task_id = parseInt(ui.item.attr('data-id')); 
            var task_index = _.findIndex(this.tasks.task_ids, function (task) {
                return task.id == task_id;
            });
            var task = this.tasks.task_ids[task_index];
            task.set_stage(this.type.id).fail( function(data){
                self.ui.item.appendTo(self.ui.sender);
                new AlertDialog(this, {
                    title: _t('Alerta'),
                    size: 'medium',
                    $content: qweb.render('poi_scrum.alert', {data: data}),
                    buttons: [{
                        text: _t('Cerrar'),
                        click: function () {
                            this.close();
                        },
                    }],
                }).open();
            });
          
        }
    });

    var AlertDialog = Dialog.extend({
    });
    
    return KanBanView;
    
    });
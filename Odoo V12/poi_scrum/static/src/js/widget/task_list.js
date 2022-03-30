odoo.define('poi_scrum.task_list_view', function (require) {
    "use strict";
    
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;
    var Widget = require('web.Widget');
    require('web.dom_ready');
        
    
    var TaskList = Widget.extend({
        template: 'poi_scrum.task_list',
        /* Lifecycle */
        init: function (parent, tasks) {
            this._super.apply(this, arguments);
            this.tasks = tasks;
        },
        xmlDependencies: ['/poi_scrum/static/src/xml/task_list.xml'],
        /**
         * Insert a new ticket instance in the list. If the list is hidden
         * (because there was no ticket prior to the insertion), call for
         * a complete rerendering instead.
         * @param  {OdooClass.Ticket} ticket Ticket to insert in the list
         */
        // insert: function (project) {
        //     if (!this.$('tbody').length) {
        //         this._rerender();
        //         return;
        //     }
        //     var charge_node = qweb.render('charge_viewer.charge_list.charge', {charge: charge});
        //     this.$('tbody').prepend(charge_node);
        // },
        /**
         * Remove a ticket from the list. If this is the last ticket to be
         * removed, rerender the widget completely to reflect the 'empty list'
         * state.
         * @param  {Integer} id ID of the ticket to remove.
         */
        // remove: function (id) {
        //     this.$('tr[data-id=' + id + ']').remove();
        //     if (!this.$('tr[data-id]').length) {
        //         this._rerender();
        //     }
        // },
        reload: function(){
            this._rerender();
        },
    
        /**
         * Rerender the whole widget; will be useful when we switch from
         * an empty list of tickets to one or more ticket (or vice-versa)
         * by using the bus.
         */
        _rerender: function () {
            this._replaceElement(qweb.render('poi_scrum.task_list', {widget: this}));
        },

        remove_active: function(){
            $.each(this.$el, function(element_index, element){
                $(element).removeClass('active');
            });
        }
    });
    
    return TaskList;
    
    });
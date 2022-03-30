odoo.define('poi_scrum.scrum_app', function (require) {
'use strict';

var core = require('web.core');
var Dialog = require('web.Dialog');
var notification = require('web.Notification');
var framework = require('web.framework');
var loading = require('web.Loading');
var User = require('poi_scrum.user_model');
var Project = require('poi_scrum.project_model').Project;
var PType = require('poi_scrum.project_model').PType;
var PStage = require('poi_scrum.project_model').PStage;
var ProjectListView = require('poi_scrum.project_list_view');

var Task = require('poi_scrum.task_model');
var TaskListView = require('poi_scrum.task_list_view');
var TaskView = require('poi_scrum.task_view');
var portal_chatter = require('portal.chatter');

var Sprint = require('poi_scrum.sprint_model');
var SprintView = require('poi_scrum.sprint_view');
var KanBanView = require('poi_scrum.kanban_view');
var Widget = require('web.Widget');
var Router = require('poi_scrum.router');
var not = require('web.NotificationService')
var qweb = core.qweb;
var _t = core._t;
var rpc = require('web.rpc');

require('web.dom_ready');

var ScrumApp = Widget.extend({
    template: 'poi_scrum.scrum_app',
    events: {
        'click .toggle-card': function(ev){
            ev.preventDefault();
            $(ev.currentTarget).next().toggle('fast'); 
        },
        'click .project': '_get_task',
        'click .project_home': '_open_home',
        // 'click .project_sprint': '_open_sprint',
        'click .project_kanban': '_open_kanban',
        'click .task_open': '_open_task',
    },
    xmlDependencies: ['/poi_scrum/static/src/xml/scrum_app_view.xml'],
    /* Lifecycle */
    init: function (parent, options) {
        this._super.apply(this, arguments);
        this.user = new User({id: odoo.session_info.user_id});
        this.project = new Project({user_id:this.user.id})
        this.ptype = new PType({user_id:this.user.id})
        this.pstage = new PStage({user_id:this.user.id})
        this.task = new Task({user_id:this.user.id})
        this.sprint = new Sprint({user_id:this.user.id})
        this.task_view = new TaskView({user_id:this.user.id})
        this.sprint_views = [];
        this.kanban_views = [];
        this.project_id_active = false;
        this.task_id_active = false;
        this.task_no_sprint = false;
        this.sprint_state = false;
        var self = this;
        Router.config({ mode: 'history', root:'/scrum'});

        // adding routes
        // Router
        // .add(/new/, function () {
        //     self._onNewTicket();
        // }).add(/about/, function () {
        //     self._about();
        // })
        // .listen();
    },
    willStart: function () {
        var self = this;
        return $.when(this._super.apply(this, arguments),
                    this.pstage.fetchStages(),
                    this.project.fetchProjects(),
                    this.ptype.fetchTypes(),
                    //   this.user.fetchUserInfo(),
                    //   this.user.fetchAllTickets()
        ).then(function (dummy, user) {
            // self.call('bus_service', 'startPolling');
            // self.call('bus_service', 'updateOption', 'demo.ticket', user.partner_id);
            // self.bus.updateOption('demo.ticket', user.partner_id);
        });
    },
    start: function () {
        var self = this;
        return this._super.apply(this, arguments).then(function () {
            self.loading = new loading(self);
            self.loading.appendTo($('.o_scrum_app'));
            self.project_list = new ProjectListView(self, self.project.project_ids);
            self.project_list.appendTo($('.o_project_list'));
            self.task_list = new TaskListView(self, self.task.task_ids);
            self.task_list.appendTo($('.o_task_list'));
            // self.sprint_view = new SprintView(self, self.sprint, self.task);
            // self.sprint_view.appendTo($('.o_sprint_view'));
            self.notification = new not(self);
            self.notification.start();
            // self.bus = new bus(self);
            // self.bus.startPolling();
        
            // self.bus.on('notification', self, self._onNotification);
            // self.call('bus_service', 'onNotification', this, self._onNotification);
            // Router.check();
        });
    },
    _get_task: function (ev) {
        ev.preventDefault();
        var self = this;
        if  (!$(ev.currentTarget).hasClass('active')) {
            self.project_list.remove_active();
            $(ev.currentTarget).addClass('active');
            var project_id = parseInt($(ev.currentTarget).attr('data-id'));
            self.task.fetchTaskbyProject(project_id, self.pstage).then(function () {
                self.task_list.reload();
                
            });
            if (project_id) {
                var project_index = _.findIndex(self.project.project_ids, function (project) {
                    return project.id == project_id;
                });
                self.project_id_active = self.project.project_ids[project_index]
            }
        }
        
        
    },
    _open_home: function(ev){
        ev.preventDefault();
        $('.project-home-view').show();
        $('.project-sprint-view').hide();
        $('.project-kanban-view').hide();
        
    },

    _open_sprint: function(ev){
        ev.preventDefault();
        var self = this;
        if (!self.project_id_active){
            new AlertDialog2(this, {
                title: _t('Alerta'),
                size: 'small',
                $content: qweb.render('poi_scrum.alert2'),
                buttons: [{
                    text: _t('Cerrar'),
                    click: function () {
                        $(".project_home").addClass('active');
                $(ev.currentTarget).removeClass('active');
                        this.close();
                    },
                }],
            }).open();
            return;
        }
        $('.project-home-view').hide();
        $('.project-sprint-view').show();
        $('.project-kanban-view').hide();
        self.sprint.fetchAllSprints(self.project_id_active.id).then(function (){
            for (var view of  self.sprint_views) {
                view.remove();
            }
            self.sprint_views = [];
            for (var sprint of  self.sprint.sprint_ids) {
                self.sprint_views.push(new SprintView(self, sprint, self.task, ".drag-t", 'sprint'))
            }
            for (var view of  self.sprint_views) {
                view.appendTo($('.o_sprint_view'));
            }
            
            if (!self.task_no_sprint) {
                self.task_no_sprint = new SprintView(self, self.project_id_active, self.task, ".drag-t", 'no_sprint');
                self.task_no_sprint.appendTo($('.o_task_no_sprint'));
            } else{
                self.task_no_sprint.sprint  = self.project_id_active;
                self.task_no_sprint.reload();
            }
        });
    },
    _open_kanban: function(ev) {
        var self = this;
        if (!self.project_id_active){
            new AlertDialog2(this, {
                title: _t('Alerta'),
                size: 'small',
                $content: qweb.render('poi_scrum.alert2'),
                buttons: [{
                    text: _t('Cerrar'),
                    click: function () {
                        $(".project_home").addClass('active');
                        $(ev.currentTarget).removeClass('active');
                        this.close();
                    },
                }],
            }).open();
            return;
        }
        ev.preventDefault();
        $('.project-home-view').hide();
        $('.project-sprint-view').hide();
        $('.project-kanban-view').show();
        for (var view of  self.kanban_views) {
            view.remove();
        }
        self.kanban_views = [];
        for (var ptype of  self.ptype.ptype_ids) {
            var type_index = _.findIndex(self.project_id_active.type_ids, function (type) {
                return type == ptype.id;
            });
            if (type_index >= 0) {
                self.kanban_views.push(new KanBanView(self, ptype, self.task, ".card-drag"));
            }
        }
        for (var view of  self.kanban_views) {
            view.appendTo($('.o_kanban_view'));
        }
    },

    _open_task: function(ev){
        var self = this;
        ev.preventDefault();
        if (!$(ev.currentTarget).hasClass('active')) {
            self.task_list.remove_active();
            $(ev.currentTarget).addClass('active');
            var task_id = parseInt($(ev.currentTarget).attr('data-id'));
            if (task_id) {
                var task_index = _.findIndex(self.task_list.tasks, function (task) {
                    return task.id == task_id;
                });
                self.task_id_active = self.task_list.tasks[task_index]
                self.task_view.task = self.task_id_active;
                self.task_view.appendTo($('.task_open_view'));
            }
        }
        // var self = this;
        // var task = qweb.render('poi_scrum.comments', {t: this.task.task_ids[0]});
        // var $elem = $(task);
        // var chatter = new RequestChatter(null, $elem.data());
        // chatter.appendTo('.comments-div');
    }
});

var AlertDialog2 = Dialog.extend({
});
var RequestChatter = portal_chatter.PortalChatter.extend({
    // start: function () {
    //     this._super.apply(this, arguments);
    //     self.$(
    //         '.o_portal_chatter_composer textarea[name="message"]'
    //     ).each(function () {
    //         var $textarea = $(this);
    //         $textarea.trumbowyg(trumbowyg.trumbowygOptions);
    //     });
    //     self.$(
    //         '.o_portal_chatter_composer ' +
    //         'form.o_portal_chatter_composer_form'
    //     ).each(function () {
    //         $(this).attr('action', '/mail/request_chatter_post');
    //     });
    // },
    _onSubmitButtonClick: function (ev) {
        this._super();
        ev.preventDefault();
        var data = this.$el.find('form').serializeArray().reduce(function(obj, item) {
            obj[item.name] = item.value;
            return obj;
        }, {});

    
        rpc.query({
            route: '/mail/chatter_post2',
            params: data
        });
    },
});
    
var $elem = $('.o_scrum_app');
var app = new ScrumApp(null);
app.appendTo($elem).then(function () {
    // bus.startPolling();
});
});
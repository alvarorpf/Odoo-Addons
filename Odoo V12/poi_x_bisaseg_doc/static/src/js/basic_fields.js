odoo.define('poi_x_bisaseg_doc.basic_fields', function (require) {
"use strict";

var FieldBinaryFile = require('web.basic_fields').FieldBinaryFile;

var AbstractField = require('web.AbstractField');
var core = require('web.core');
var crash_manager = require('web.crash_manager');
var datepicker = require('web.datepicker');
var dom = require('web.dom');
var Domain = require('web.Domain');
var DomainSelector = require('web.DomainSelector');
var DomainSelectorDialog = require('web.DomainSelectorDialog');
var framework = require('web.framework');
var session = require('web.session');
var utils = require('web.utils');
var view_dialogs = require('web.view_dialogs');
var field_utils = require('web.field_utils');

var qweb = core.qweb;
var _t = core._t;

FieldBinaryFile.include({
    on_save_as: function (ev) {
        var modelo = this.model
        if(modelo == 'muk_quality_docs.document' || modelo == 'document.history'){
            var down = this.recordData['download']
            if (down == true){
                    if (!this.value) {
                    this.do_warn(_t("Save As..."), _t("The field is empty, there's nothing to save !"));
                    ev.stopPropagation();
                } else if (this.res_id) {
                    framework.blockUI();
                    var c = crash_manager;
                    var filename_fieldname = this.attrs.filename;
                    this.getSession().get_file({
                        'url': '/web/content',
                        'data': {
                            'model': this.model,
                            'id': this.res_id,
                            'field': this.name,
                            'filename_field': filename_fieldname,
                            'filename': this.recordData[filename_fieldname] || "",
                            'download': true,
                            'data': utils.is_bin_size(this.value) ? null : this.value,
                        },
                        'complete': framework.unblockUI,
                        'error': c.rpc_error.bind(c),
                    });
                    ev.stopPropagation();
                }
            }
            else{}
        }
        else{
            if (!this.value) {
                this.do_warn(_t("Save As..."), _t("The field is empty, there's nothing to save !"));
                ev.stopPropagation();
            } else if (this.res_id) {
                framework.blockUI();
                var c = crash_manager;
                var filename_fieldname = this.attrs.filename;
                this.getSession().get_file({
                    'url': '/web/content',
                    'data': {
                        'model': this.model,
                        'id': this.res_id,
                        'field': this.name,
                        'filename_field': filename_fieldname,
                        'filename': this.recordData[filename_fieldname] || "",
                        'download': true,
                        'data': utils.is_bin_size(this.value) ? null : this.value,
                    },
                    'complete': framework.unblockUI,
                    'error': c.rpc_error.bind(c),
                });
                ev.stopPropagation();
            }
        }

    },
});
});


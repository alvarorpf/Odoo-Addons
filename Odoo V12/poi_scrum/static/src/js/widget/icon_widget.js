// odoo.define('poi_scrum.icon_widget', function (require) {
// "use strict";

// var core = require('web.core');
// var qweb = core.qweb;
// var _t = core._t;
// var Widget = require('web.Widget');
// var FieldChar = require('web.basic_fields').FieldChar;
// var fieldRegistry = require('web.field_registry'); 

// var icon_widget = FieldChar.extend({
//     // template: 'poi_scrum.icon_popover',
//     events: _.extend({}, FieldChar.prototype.events, {
//         // 'click': '_onClick',
//         'click .icon': '_set_icon',
//     }),
//     xmlDependencies: ['/poi_scrum/static/src/xml/icon_widget.xml'],
//     icons: [
//         {
//             class: "fa-glass",
//         },
//         {
//             class: "fa-music",
//         },
//         {
//             class: "fa-search",
//         },
//         {
//             class: "fa-envelope-o",
//         },
//         {
//             class: "fa-heart",
//         },
//         {
//             class: "fa-star",
//         },
//         {
//             class: "fa-star-o",
//         },
//         {
//             class: "fa-user",
//         },
//         {
//             class: "fa-film",
//         },
//         {
//             class: "fa-th-large",
//         },
//         {
//             class: "fa-th",
//         },
//         {
//             class: "fa-th-list",
//         },
//         {
//             class: "fa-check",
//         },
//         {
//             class: "fa-remove",
//         },
//         {
//             class: "fa-close",
//         },
//         {
//             class: "fa-times",
//         },
//         {
//             class: "fa-search-plus",
//         },
//         {
//             class: "fa-search-minus",
//         },
//         {
//             class: "fa-power-off",
//         },
//         {
//             class: "fa-signal",
//         },
//         {
//             class: "fa-gear",
//         },
//         {
//             class: "fa-cog",
//         },
//         {
//             class: "fa-trash-o",
//         },
//         {
//             class: "fa-home",
//         },
//         {
//             class: "fa-file-o",
//         },
//         {
//             class: "fa-clock-o",
//         },
//         {
//             class: "fa-road",
//         },
//         {
//             class: "fa-download",
//         },
//         {
//             class: "fa-arrow-circle-o-down",
//         },
//         {
//             class: "fa-arrow-circle-o-up",
//         },
//         {
//             class: "fa-inbox",
//         },
//         {
//             class: "fa-play-circle-o",
//         },
//         {
//         class: "fa-rotate-right",
//         },
//         {
//             class: "fa-repeat",
//         },
//         {
//             class: "fa-refresh",
//         },
//         {
//             class: "fa-list-alt",
//         },
//         {
//             class: "fa-lock",
//         },
//         {
//             class: "fa-flag",
//         },
//         {
//             class: "fa-headphones",
//         },
//         {
//             class: "fa-volume-off",
//         },
//         {
//             class: "fa-volume-down",
//         },
//         {
//             class: "fa-volume-up",
//         },
//         {
//             class: "fa-qrcode",
//         },
//         {
//             class: "fa-barcode",
//         },
//         {
//             class: "fa-tag",
//         },
//         {
//             class: "fa-tags",
//         },
//         {
//             class: "fa-book",
//         },
//         {
//             class: "fa-bookmark",
//         },
//         {
//             class: "fa-print",
//         },
//         {
//             class: "fa-camera",
//         },
//         {
//             class: "fa-font",
//         },
//         {
//             class: "fa-bold",
//         },
//         {
//             class: "fa-italic",
//         },
//         {
//             class: "fa-text-height",
//         },
//         {
//             class: "fa-text-width",
//         },
//         {
//             class: "fa-align-left",
//         },
//         {
//             class: "fa-align-center",
//         },
//         {
//             class: "fa-align-right",
//         },
//         {
//             class: "fa-align-justify",
//         },
//         {
//             class: "fa-list",
//         },
//         {
//             class: "fa-dedent:before",
//         },
//         {
//             class: "fa-outdent",
//         },
//         {
//             class: "fa-indent",
//         },
//         {
//             class: "fa-video-camera",
//         },
//         {
//             class: "fa-photo"
//         },
//         {        
//             class: "fa-image",
//         },
//         {
//             class: "fa-picture-o",
//         },
//         {
//             class: "fa-pencil",
//         },
//         {
//             class: "fa-map-marker",
//         },
//         {
//             class: "fa-adjust",
//         },
//         {
//             class: "fa-tint",
//         },
//         {
//             class: "fa-edit",
//         },
//         {
//             class: "fa-pencil-square-o",
//         },
//         {
//             class: "fa-share-square-o",
//         },
//         {
//             class: "fa-check-square-o",
//         },
//         {
//             class: "fa-arrows",
//         },
//         {
//             class: "fa-step-backward",
//         },
//         {
//             class: "fa-fast-backward",
//         },
//         {
//             class: "fa-backward",
//         },
//         {
//             class: "fa-play",
//         },
//         {
//             class: "fa-pause",
//         },
//         {
//             class: "fa-stop",
//         },
//         {
//             class: "fa-forward",
//         },
//         {
//             class: "fa-fast-forward",
//         },
//         {
//             class: "fa-step-forward",
//         },
//         {
//             class: "fa-eject",
//         },
//         {
//             class: "fa-chevron-left",
//         },
//         {
//             class: "fa-chevron-right",
//         },
//         {
//             class: "fa-plus-circle",
//         },
//         {
//             class: "fa-minus-circle",
//         },
//         {
//             class: "fa-times-circle",
//         },
//         {
//             class: "fa-check-circle",
//         },
//         {
//             class: "fa-question-circle",
//         },
//         {
//             class: "fa-info-circle",
//         },
//         {
//             class: "fa-crosshairs",
//         },
//         {
//             class: "fa-times-circle-o",
//         },
//         {
//             class: "fa-check-circle-o",
//         },
//         {
//             class: "fa-ban",
//         },
//         {
//             class: "fa-arrow-left",
//         },
//         {
//             class: "fa-arrow-right",
//         },
//         {
//             class: "fa-arrow-up",
//         },
//         {
//             class: "fa-arrow-down",
//         },
//         {
//             class: "fa-mail-forward",
//         },
//         {
//             class: "fa-share",
//         },
//         {
//             class: "fa-expand",
//         },
//         {
//             class: "fa-compress",
//         },
//         {
//             class: "fa-plus",
//         },
//         {
//             class: "fa-minus",
//         },
//         {
//             class: "fa-asterisk",
//         },
//         {
//             class: "fa-exclamation-circle",
//         },
//         {
//             class: "fa-gift",
//         },
//         {
//             class: "fa-leaf",
//         },
//         {
//             class: "fa-fire",
//         },
//         {
//             class: "fa-eye",
//         },
//         {
//             class: "fa-eye-slash",
//         },
//         {
//             class: "fa-warning",
//         },
//         {
//             class: "fa-exclamation-triangle",
//         },
//         {
//             class: "fa-plane",
//         },
//         {
//             class: "fa-calendar",
//         },
//         {
//             class: "fa-random",
//         },
//         {
//             class: "fa-comment",
//         },
//         {
//             class: "fa-magnet",
//         },
//         {
//             class: "fa-chevron-up",
//         },
//         {
//             class: "fa-chevron-down",
//         },
//         {
//             class: "fa-retweet",
//         },
//         {
//             class: "fa-shopping-cart",
//         },
//         {
//             class: "fa-folder",
//         },
//         {
//             class: "fa-folder-open",
//         },
//         {
//             class: "fa-arrows-v",
//         },
//         {
//             class: "fa-arrows-h",
//         },
//         {
//             class: "fa-bar-chart-o",
//         },
//         {
//             class: "fa-bar-chart",
//         },
//         {
//             class: "fa-twitter-square",
//         },
//         {
//             class: "fa-facebook-square",
//         },
//         {
//             class: "fa-camera-retro",
//         },
//         {
//             class: "fa-key",
//         },
//         {
//             class: "fa-gears",
//         },
//         {
//             class: "fa-cogs",
//         },
//         {
//             class: "fa-comments",
//         },
//         {
//             class: "fa-thumbs-o-up",
//         },
//         {
//             class: "fa-thumbs-o-down",
//         },
//         {
//             class: "fa-star-half",
//         },
//         {
//             class: "fa-heart-o",
//         },
//         {
//             class: "fa-sign-out",
//         },
//         {
//             class: "fa-linkedin-square",
//         },
//         {
//             class: "fa-thumb-tack",
//         },
//         {
//             class: "fa-external-link",
//         },
//         {
//             class: "fa-sign-in",
//         },
//         {
//             class: "fa-trophy",
//         },
//         {
//             class: "fa-github-square",
//         },
//         {
//             class: "fa-upload",
//         },
//         {
//             class: "fa-lemon-o",
//         },
//         {
//             class: "fa-phone",
//         },
//         {
//             class: "fa-square-o",
//         },
//         {
//             class: "fa-bookmark-o",
//         },
//         {
//             class: "fa-phone-square",
//         },
//         {
//             class: "fa-twitter",
//         },
//         {
//             class: "fa-facebook-f",
//         },
//         {
//             class: "fa-facebook",
//         },
//         {
//             class: "fa-github",
//         },
//         {
//             class: "fa-unlock",
//         },
//         {
//             class: "fa-credit-card",
//         },
//         {
//             class: "fa-feed",
//         },
//         {
//             class: "fa-rss",
//         },
//         {
//             class: "fa-hdd-o",
//         },
//         {
//             class: "fa-bullhorn",
//         },
//         {
//             class: "fa-bell",
//         },
//         {
//             class: "fa-certificate",
//         },
//         {
//             class: "fa-hand-o-right",
//         },
//         {
//             class: "fa-hand-o-left",
//         },
//         {
//             class: "fa-hand-o-up",
//         },
//         {
//             class: "fa-hand-o-down",
//         },
//         {
//             class: "fa-arrow-circle-left",
//         },
//         {
//             class: "fa-arrow-circle-right",
//         },
//         {
//             class: "fa-arrow-circle-up",
//         },
//         {
//             class: "fa-arrow-circle-down",
//         },
//         {
//             class: "fa-globe",
//         },
//         {
//             class: "fa-wrench",
//         },
//         {
//             class: "fa-tasks",
//         },
//         {
//             class: "fa-filter",
//         },
//         {
//             class: "fa-briefcase",
//         },
//         {
//             class: "fa-arrows-alt",
//         },
//         {
//             class: "fa-group",
//         },
//         {
//             class: "fa-users",
//         },
//         {
//             class: "fa-chain",
//         },
//         {
//             class: "fa-link",
//         },
//         {
//             class: "fa-cloud",
//         },
//         {
//             class: "fa-flask",
//         },
//         {
//             class: "fa-cut",
//         },
//         {
//             class: "fa-scissors",
//         },
//         {
//             class: "fa-copy",
//         },
//         {
//             class: "fa-files-o",
//         },
//         {
//             class: "fa-paperclip",
//         },
//         {
//             class: "fa-save",
//         },
//         {
//             class: "fa-floppy-o",
//         },
//         {
//             class: "fa-square",
//         },
//         {
//             class: "fa-navicon",
//         },
//         {
//             class: "fa-reorder",
//         },
//         {
//             class: "fa-bars",
//         },
//         {
//             class: "fa-list-ul",
//         },
//         {
//             class: "fa-list-ol",
//         },
//         {
//             class: "fa-strikethrough",
//         },
//         {
//             class: "fa-underline",
//         },
//         {
//             class: "fa-table",
//         },
//         {
//             class: "fa-magic",
//         },
//         {
//             class: "fa-truck",
//         },
//         {
//             class: "fa-pinterest",
//         },
//         {
//             class: "fa-pinterest-square",
//         },
//         {
//             class: "fa-google-plus-square",
//         },
//         {
//             class: "fa-google-plus",
//         },
//         {
//             class: "fa-money",
//         },
//         {
//             class: "fa-caret-down",
//         },
//         {
//             class: "fa-caret-up",
//         },
//         {
//             class: "fa-caret-left",
//         },
//         {
//             class: "fa-caret-right",
//         },
//         {
//             class: "fa-columns",
//         },
//         {
//             class: "fa-unsorted",
//         },
//         {
//             class: "fa-sort",
//         },
//         {
//             class: "fa-sort-down",
//         },
//         {
//             class: "fa-sort-desc",
//         },
//         {
//             class: "fa-sort-up",
//         },
//         {
//             class: "fa-sort-asc",
//         },
//         {
//             class: "fa-envelope",
//         },
//         {
//             class: "fa-linkedin",
//         },
//         {
//             class: "fa-rotate-left",
//         },
//         {
//             class: "fa-undo",
//         },
//         {
//             class: "fa-legal",
//         },
//         {
//             class: "fa-gavel",
//         },
//         {
//             class: "fa-dashboard",
//         },
//         {
//             class: "fa-tachometer",
//         },
//         {
//             class: "fa-comment-o",
//         },
//         {
//             class: "fa-comments-o",
//         },
//         {
//             class: "fa-flash",
//         },
//         {
//             class: "fa-bolt",
//         },
//         {
//             class: "fa-sitemap",
//         },
//         {
//             class: "fa-umbrella",
//         },
//         {
//             class: "fa-paste",
//         },
//         {
//             class: "fa-clipboard",
//         },
//         {
//             class: "fa-lightbulb-o",
//         },
//         {
//             class: "fa-exchange",
//         },
//         {
//             class: "fa-cloud-download",
//         },
//         {
//             class: "fa-cloud-upload",
//         },
//         {
//             class: "fa-user-md",
//         },
//         {
//             class: "fa-stethoscope",
//         },
//         {
//             class: "fa-suitcase",
//         },
//         {
//             class: "fa-bell-o",
//         },
//         {
//             class: "fa-coffee",
//         },
//         {
//             class: "fa-cutlery",
//         },
//         {
//             class: "fa-file-text-o",
//         },
//         {
//             class: "fa-building-o",
//         },
//         {
//             class: "fa-hospital-o",
//         },
//         {
//             class: "fa-ambulance",
//         },
//         {
//             class: "fa-medkit",
//         },
//         {
//             class: "fa-fighter-jet",
//         },
//         {
//             class: "fa-beer",
//         },
//         {
//             class: "fa-h-square",
//         },
//         {
//             class: "fa-plus-square",
//         },
//         {
//             class: "fa-angle-double-left",
//         },
//         {
//             class: "fa-angle-double-right",
//         },
//         {
//             class: "fa-angle-double-up",
//         },
//         {
//             class: "fa-angle-double-down",
//         },
//         {
//             class: "fa-angle-left",
//         },
//         {
//             class: "fa-angle-right",
//         },
//         {
//             class: "fa-angle-up",
//         },
//         {
//             class: "fa-angle-down",
//         },
//         {
//             class: "fa-desktop",
//         },
//         {
//             class: "fa-laptop",
//         },
//         {
//             class: "fa-tablet",
//         },
//         {
//             class: "fa-mobile-phone",
//         },
//         {
//             class: "fa-mobile",
//         },
//         {
//             class: "fa-circle-o",
//         },
//         {
//             class: "fa-quote-left",
//         },
//         {
//             class: "fa-quote-right",
//         },
//         {
//             class: "fa-spinner",
//         },
//         {
//             class: "fa-circle",
//         },
//         {
//             class: "fa-mail-reply",
//         },
//         {
//             class: "fa-reply",
//         },
//         {
//             class: "fa-github-alt",
//         },
//         {
//             class: "fa-folder-o",
//         },
//         {
//             class: "fa-folder-open-o",
//         },
//         {
//             class: "fa-smile-o",
//         },
//         {
//             class: "fa-frown-o",
//         },
//         {
//             class: "fa-meh-o",
//         },
//         {
//             class: "fa-gamepad",
//         },
//         {
//             class: "fa-keyboard-o",
//         },
//         {
//             class: "fa-flag-o",
//         },
//         {
//             class: "fa-flag-checkered",
//         },
//         {
//             class: "fa-terminal",
//         },
//         {
//             class: "fa-code",
//         },
//         {
//             class: "fa-mail-reply-all",
//         },
//         {
//             class: "fa-reply-all",
//         },
//         {
//             class: "fa-star-half-empty",
//         },
//         {
//             class: "fa-star-half-full",
//         },
//         {
//             class: "fa-star-half-o",
//         },
//         {
//             class: "fa-location-arrow",
//         },
//         {
//             class: "fa-crop",
//         },
//         {
//             class: "fa-code-fork",
//         },
//         {
//             class: "fa-unlink",
//         },
//         {
//             class: "fa-chain-broken",
//         },
//         {
//             class: "fa-question",
//         },
//         {
//             class: "fa-info",
//         },
//         {
//             class: "fa-exclamation",
//         },
//         {
//             class: "fa-superscript",
//         },
//         {
//             class: "fa-subscript",
//         },
//         {
//             class: "fa-eraser",
//         },
//         {
//             class: "fa-puzzle-piece",
//         },
//         {
//             class: "fa-microphone",
//         },
//         {
//             class: "fa-microphone-slash",
//         },
//         {
//             class: "fa-shield",
//         },
//         {
//             class: "fa-calendar-o",
//         },
//         {
//             class: "fa-fire-extinguisher",
//         },
//         {
//             class: "fa-rocket",
//         },
//         {
//             class: "fa-maxcdn",
//         },
//         {
//             class: "fa-chevron-circle-left",
//         },
//         {
//             class: "fa-chevron-circle-right",
//         },
//         {
//             class: "fa-chevron-circle-up",
//         },
//         {
//             class: "fa-chevron-circle-down",
//         },
//         {
//             class: "fa-html5",
//         },
//         {
//             class: "fa-css3",
//         },
//         {
//             class: "fa-anchor",
//         },
//         {
//             class: "fa-unlock-alt",
//         },
//         {
//             class: "fa-bullseye",
//         },
//         {
//             class: "fa-ellipsis-h",
//         },
//         {
//             class: "fa-ellipsis-v",
//         },
//         {
//             class: "fa-rss-square",
//         },
//         {
//             class: "fa-play-circle",
//         },
//         {
//             class: "fa-ticket",
//         },
//         {
//             class: "fa-minus-square",
//         },
//         {
//             class: "fa-minus-square-o",
//         },
//         {
//             class: "fa-level-up",
//         },
//         {
//             class: "fa-level-down",
//         },
//         {
//             class: "fa-check-square",
//         },
//         {
//             class: "fa-pencil-square",
//         },
//         {
//             class: "fa-external-link-square",
//         },
//         {
//             class: "fa-share-square",
//         },
//         {
//             class: "fa-compass",
//         },
//         {
//             class: "fa-toggle-down",
//         },
//         {
//             class: "fa-caret-square-o-down",
//         },
//         {
//             class: "fa-toggle-up",
//         },
//         {
//             class: "fa-caret-square-o-up",
//         },
//         {
//             class: "fa-toggle-right",
//         },
//         {
//             class: "fa-caret-square-o-right",
//         },
//         {
//             class: "fa-euro",
//         },
//         {
//             class: "fa-eur",
//         },
//         {
//             class: "fa-gbp",
//         },
//         {
//             class: "fa-dollar",
//         },
//         {
//             class: "fa-usd",
//         },
//         {
//             class: "fa-rupee",
//         },
//         {
//             class: "fa-inr",
//         },
//         {
//             class: "fa-cny",
//         },
//         {
//             class: "fa-rmb",
//         },
//         {
//             class: "fa-yen",
//         },
//         {
//             class: "fa-jpy",
//         },
//         {
//             class: "fa-ruble",
//         },
//         {
//             class: "fa-rouble",
//         },
//         {
//             class: "fa-rub",
//         },
//         {
//             class: "fa-won",
//         },
//         {
//             class: "fa-krw",
//         },
//         {
//             class: "fa-bitcoin",
//         },
//         {
//             class: "fa-btc",
//         },
//         {
//             class: "fa-file",
//         },
//         {
//             class: "fa-file-text",
//         },
//         {
//             class: "fa-sort-alpha-asc",
//         },
//         {
//             class: "fa-sort-alpha-desc",
//         },
//         {
//             class: "fa-sort-amount-asc",
//         },
//         {
//             class: "fa-sort-amount-desc",
//         },
//         {
//             class: "fa-sort-numeric-asc",
//         },
//         {
//             class: "fa-sort-numeric-desc",
//         },
//         {
//             class: "fa-thumbs-up",
//         },
//         {
//             class: "fa-thumbs-down",
//         },
//         {
//             class: "fa-youtube-square",
//         },
//         {
//             class: "fa-youtube",
//         },
//         {
//             class: "fa-xing",
//         },
//         {
//             class: "fa-xing-square",
//         },
//         {
//             class: "fa-youtube-play",
//         },
//         {
//             class: "fa-dropbox",
//         },
//         {
//             class: "fa-stack-overflow",
//         },
//         {
//             class: "fa-instagram",
//         },
//         {
//             class: "fa-flickr",
//         },
//         {
//             class: "fa-adn",
//         },
//         {
//             class: "fa-bitbucket",
//         },
//         {
//             class: "fa-bitbucket-square",
//         },
//         {
//             class: "fa-tumblr",
//         },
//         {
//             class: "fa-tumblr-square",
//         },
//         {
//             class: "fa-long-arrow-down",
//         },
//         {
//             class: "fa-long-arrow-up",
//         },
//         {
//             class: "fa-long-arrow-left",
//         },
//         {
//             class: "fa-long-arrow-right",
//         },
//         {
//             class: "fa-apple",
//         },
//         {
//             class: "fa-windows",
//         },
//         {
//             class: "fa-android",
//         },
//         {
//             class: "fa-linux",
//         },
//         {
//             class: "fa-dribbble",
//         },
//         {
//             class: "fa-skype",
//         },
//         {
//             class: "fa-foursquare",
//         },
//         {
//             class: "fa-trello",
//         },
//         {
//             class: "fa-female",
//         },
//         {
//             class: "fa-male",
//         },
//         {
//         class: "fa-gittip",
//         },
//         {
//             class: "fa-gratipay",
//         },
//         {
//             class: "fa-sun-o",
//         },
//         {
//             class: "fa-moon-o",
//         },
//         {
//             class: "fa-archive",
//         },
//         {
//             class: "fa-bug",
//         },
//         {
//             class: "fa-vk",
//         },
//         {
//             class: "fa-weibo",
//         },
//         {
//             class: "fa-renren",
//         },
//         {
//             class: "fa-pagelines",
//         },
//         {
//             class: "fa-stack-exchange",
//         },
//         {
//             class: "fa-arrow-circle-o-right",
//         },
//         {
//             class: "fa-arrow-circle-o-left",
//         },
//         {
//             class: "fa-toggle-left",
//         },
//         {
//             class: "fa-caret-square-o-left",
//         },
//         {
//             class: "fa-dot-circle-o",
//         },
//         {
//             class: "fa-wheelchair",
//         },
//         {
//             class: "fa-vimeo-square",
//         },
//         {
//             class: "fa-turkish-lira",
//         },
//         {
//             class: "fa-try",
//         },
//         {
//             class: "fa-plus-square-o",
//         },
//         {
//             class: "fa-space-shuttle",
//         },
//         {
//             class: "fa-slack",
//         },
//         {
//             class: "fa-envelope-square",
//         },
//         {
//             class: "fa-wordpress",
//         },
//         {
//             class: "fa-openid",
//         },
//         {
//             class: "fa-institution",
//         },
//         {
//             class: "fa-bank",
//         },
//         {
//             class: "fa-university",
//         },
//         {
//             class: "fa-mortar-board",
//         },
//         {
//             class: "fa-graduation-cap",
//         },
//         {
//             class: "fa-yahoo",
//         },
//         {
//             class: "fa-google",
//         },
//         {
//             class: "fa-reddit",
//         },
//         {
//             class: "fa-reddit-square",
//         },
//         {
//             class: "fa-stumbleupon-circle",
//         },
//         {
//             class: "fa-stumbleupon",
//         },
//         {
//             class: "fa-delicious",
//         },
//         {
//             class: "fa-digg",
//         },
//         {
//             class: "fa-pied-piper-pp",
//         },
//         {
//             class: "fa-pied-piper-alt",
//         },
//         {
//             class: "fa-drupal",
//         },
//         {
//             class: "fa-joomla",
//         },
//         {
//             class: "fa-language",
//         },
//         {
//             class: "fa-fax",
//         },
//         {
//             class: "fa-building",
//         },
//         {
//             class: "fa-child",
//         },
//         {
//             class: "fa-paw",
//         },
//         {
//             class: "fa-spoon",
//         },
//         {
//             class: "fa-cube",
//         },
//         {
//             class: "fa-cubes",
//         },
//         {
//             class: "fa-behance",
//         },
//         {
//             class: "fa-behance-square",
//         },
//         {
//             class: "fa-steam",
//         },
//         {
//             class: "fa-steam-square",
//         },
//         {
//             class: "fa-recycle",
//         },
//         {
//             class: "fa-automobile",
//         },
//         {
//             class: "fa-car",
//         },
//         {
//             class: "fa-cab",
//         },
//         {
//             class: "fa-taxi",
//         },
//         {
//             class: "fa-tree",
//         },
//         {
//             class: "fa-spotify",
//         },
//         {
//             class: "fa-deviantart",
//         },
//         {
//             class: "fa-soundcloud",
//         },
//         {
//             class: "fa-database",
//         },
//         {
//             class: "fa-file-pdf-o",
//         },
//         {
//             class: "fa-file-word-o",
//         },
//         {
//             class: "fa-file-excel-o",
//         },
//         {
//             class: "fa-file-powerpoint-o",
//         },
//         {
//             class: "fa-file-photo-o",
//         },
//         {
//             class: "fa-file-picture-o",
//         },
//         {
//             class: "fa-file-image-o",
//         },
//         {
//             class: "fa-file-zip-o",
//         },
//         {
//             class: "fa-file-archive-o",
//         },
//         {
//             class: "fa-file-sound-o",
//         },
//         {
//             class: "fa-file-audio-o",
//         },
//         {
//             class: "fa-file-movie-o",
//         },
//         {
//             class: "fa-file-video-o",
//         },
//         {
//             class: "fa-file-code-o",
//         },
//         {
//             class: "fa-vine",
//         },
//         {
//             class: "fa-codepen",
//         },
//         {
//             class: "fa-jsfiddle",
//         },
//         {
//             class: "fa-life-bouy",
//         },
//         {
//             class: "fa-life-buoy",
//         },
//         {
//             class: "fa-life-saver",
//         },
//         {
//             class: "fa-support",
//         },
//         {
//             class: "fa-life-ring",
//         },
//         {
//             class: "fa-circle-o-notch",
//         },
//         {
//             class: "fa-ra",
//         },
//         {
//             class: "fa-resistance",
//         },
//         {
//             class: "fa-rebel",
//         },
//         {
//             class: "fa-ge",
//         },
//         {
//             class: "fa-empire",
//         },
//         {
//             class: "fa-git-square",
//         },
//         {
//             class: "fa-git",
//         },
//         {
//             class: "fa-y-combinator-square",
//         },
//         {
//             class: "fa-yc-square",
//         },
//         {
//             class: "fa-hacker-news",
//         },
//         {
//             class: "fa-tencent-weibo",
//         },
//         {
//             class: "fa-qq",
//         },
//         {
//             class: "fa-wechat",
//         },
//         {
//             class: "fa-weixin",
//         },
//         {
//             class: "fa-send",
//         },
//         {
//             class: "fa-paper-plane",
//         },
//         {
//             class: "fa-send-o",
//         },
//         {
//             class: "fa-paper-plane-o",
//         },
//         {
//             class: "fa-history",
//         },
//         {
//             class: "fa-circle-thin",
//         },
//         {
//             class: "fa-header",
//         },
//         {
//             class: "fa-paragraph",
//         },
//         {
//             class: "fa-sliders",
//         },
//         {
//             class: "fa-share-alt",
//         },
//         {
//             class: "fa-share-alt-square",
//         },
//         {
//             class: "fa-bomb",
//         },
//         {
//             class: "fa-soccer-ball-o",
//         },
//         {
//             class: "fa-futbol-o",
//         },
//         {
//             class: "fa-tty",
//         },
//         {
//             class: "fa-binoculars",
//         },
//         {
//             class: "fa-plug",
//         },
//         {
//             class: "fa-slideshare",
//         },
//         {
//             class: "fa-twitch",
//         },
//         {
//             class: "fa-yelp",
//         },
//         {
//             class: "fa-newspaper-o",
//         },
//         {
//             class: "fa-wifi",
//         },
//         {
//             class: "fa-calculator",
//         },
//         {
//             class: "fa-paypal",
//         },
//         {
//             class: "fa-google-wallet",
//         },
//         {
//             class: "fa-cc-visa",
//         },
//         {
//             class: "fa-cc-mastercard",
//         },
//         {
//             class: "fa-cc-discover",
//         },
//         {
//             class: "fa-cc-amex",
//         },
//         {
//             class: "fa-cc-paypal",
//         },
//         {
//             class: "fa-cc-stripe",
//         },
//         {
//             class: "fa-bell-slash",
//         },
//         {
//             class: "fa-bell-slash-o",
//         },
//         {
//             class: "fa-trash",
//         },
//         {
//             class: "fa-copyright",
//         },
//         {
//             class: "fa-at",
//         },
//         {
//             class: "fa-eyedropper",
//         },
//         {
//             class: "fa-paint-brush",
//         },
//         {
//             class: "fa-birthday-cake",
//         },
//         {
//             class: "fa-area-chart",
//         },
//         {
//             class: "fa-pie-chart",
//         },
//         {
//             class: "fa-line-chart",
//         },
//         {
//             class: "fa-lastfm",
//         },
//         {
//             class: "fa-lastfm-square",
//         },
//         {
//             class: "fa-toggle-off",
//         },
//         {
//             class: "fa-toggle-on",
//         },
//         {
//             class: "fa-bicycle",
//         },
//         {
//             class: "fa-bus",
//         },
//         {
//             class: "fa-ioxhost",
//         },
//         {
//             class: "fa-angellist",
//         },
//         {
//             class: "fa-cc",
//         },
//         {
//             class: "fa-shekel",
//         },
//         {
//             class: "fa-sheqel",
//         },
//         {
//             class: "fa-ils",
//         },
//         {
//             class: "fa-meanpath",
//         },
//         {
//             class: "fa-buysellads",
//         },
//         {
//             class: "fa-connectdevelop",
//         },
//         {
//             class: "fa-dashcube",
//         },
//         {
//             class: "fa-forumbee",
//         },
//         {
//             class: "fa-leanpub",
//         },
//         {
//             class: "fa-sellsy",
//         },
//         {
//             class: "fa-shirtsinbulk",
//         },
//         {
//             class: "fa-simplybuilt",
//         },
//         {
//             class: "fa-skyatlas",
//         },
//         {
//             class: "fa-cart-plus",
//         },
//         {
//             class: "fa-cart-arrow-down",
//         },
//         {
//             class: "fa-diamond",
//         },
//         {
//             class: "fa-ship",
//         },
//         {
//             class: "fa-user-secret",
//         },
//         {
//             class: "fa-motorcycle",
//         },
//         {
//             class: "fa-street-view",
//         },
//         {
//             class: "fa-heartbeat",
//         },
//         {
//             class: "fa-venus",
//         },
//         {
//             class: "fa-mars",
//         },
//         {
//             class: "fa-mercury",
//         },
//         {
//             class: "fa-intersex",
//         },
//         {
//             class: "fa-transgender",
//         },
//         {
//             class: "fa-transgender-alt",
//         },
//         {
//             class: "fa-venus-double",
//         },
//         {
//             class: "fa-mars-double",
//         },
//         {
//             class: "fa-venus-mars",
//         },
//         {
//             class: "fa-mars-stroke",
//         },
//         {
//             class: "fa-mars-stroke-v",
//         },
//         {
//             class: "fa-mars-stroke-h",
//         },
//         {
//             class: "fa-neuter",
//         },
//         {
//             class: "fa-genderless",
//         },
//         {
//             class: "fa-facebook-official",
//         },
//         {
//             class: "fa-pinterest-p",
//         },
//         {
//             class: "fa-whatsapp",
//         },
//         {
//             class: "fa-server",
//         },
//         {
//             class: "fa-user-plus",
//         },
//         {
//             class: "fa-user-times",
//         },
//         {
//             class: "fa-hotel",
//         },
//         {
//             class: "fa-bed",
//         },
//         {
//             class: "fa-viacoin",
//         },
//         {
//             class: "fa-train",
//         },
//         {
//             class: "fa-subway",
//         },
//         {
//             class: "fa-medium",
//         },
//         {
//             class: "fa-yc",
//         },
//         {
//             class: "fa-y-combinator",
//         },
//         {
//             class: "fa-optin-monster",
//         },
//         {
//             class: "fa-opencart",
//         },
//         {
//             class: "fa-expeditedssl",
//         },
//         {
//             class: "fa-battery-4",
//         },
//         {
//             class: "fa-battery",
//         },
//         {
//             class: "fa-battery-full",
//         },
//         {
//             class: "fa-battery-3",
//         },
//         {
//             class: "fa-battery-three-quarters",
//         },
//         {
//             class: "fa-battery-2",
//         },
//         {
//             class: "fa-battery-half",
//         },
//         {
//             class: "fa-battery-1",
//         },
//         {
//             class: "fa-battery-quarter",
//         },
//         {
//             class: "fa-battery-0",
//         },
//         {
//             class: "fa-battery-empty",
//         },
//         {
//             class: "fa-mouse-pointer",
//         },
//         {
//             class: "fa-i-cursor",
//         },
//         {
//             class: "fa-object-group",
//         },
//         {
//             class: "fa-object-ungroup",
//         },
//         {
//             class: "fa-sticky-note",
//         },
//         {
//             class: "fa-sticky-note-o",
//         },
//         {
//             class: "fa-cc-jcb",
//         },
//         {
//             class: "fa-cc-diners-club",
//         },
//         {
//             class: "fa-clone",
//         },
//         {
//             class: "fa-balance-scale",
//         },
//         {
//             class: "fa-hourglass-o",
//         },
//         {
//             class: "fa-hourglass-1",
//         },
//         {
//             class: "fa-hourglass-start",
//         },
//         {
//             class: "fa-hourglass-2",
//         },
//         {
//             class: "fa-hourglass-half",
//         },
//         {
//             class: "fa-hourglass-3",
//         },
//         {
//             class: "fa-hourglass-end",
//         },
//         {
//             class: "fa-hourglass",
//         },
//         {
//             class: "fa-hand-grab-o",
//         },
//         {
//             class: "fa-hand-rock-o",
//         },
//         {
//             class: "fa-hand-stop-o",
//         },
//         {
//             class: "fa-hand-paper-o",
//         },
//         {
//             class: "fa-hand-scissors-o",
//         },
//         {
//             class: "fa-hand-lizard-o",
//         },
//         {
//             class: "fa-hand-spock-o",
//         },
//         {
//             class: "fa-hand-pointer-o",
//         },
//         {
//             class: "fa-hand-peace-o",
//         },
//         {
//             class: "fa-trademark",
//         },
//         {
//             class: "fa-registered",
//         },
//         {
//             class: "fa-creative-commons",
//         },
//         {
//             class: "fa-gg",
//         },
//         {
//             class: "fa-gg-circle",
//         },
//         {
//             class: "fa-tripadvisor",
//         },
//         {
//             class: "fa-odnoklassniki",
//         },
//         {
//             class: "fa-odnoklassniki-square",
//         },
//         {
//             class: "fa-get-pocket",
//         },
//         {
//             class: "fa-wikipedia-w",
//         },
//         {
//             class: "fa-safari",
//         },
//         {
//             class: "fa-chrome",
//         },
//         {
//             class: "fa-firefox",
//         },
//         {
//             class: "fa-opera",
//         },
//         {
//             class: "fa-internet-explorer",
//         },
//         {
//             class: "fa-tv",
//         },
//         {
//             class: "fa-television",
//         },
//         {
//             class: "fa-contao",
//         },
//         {
//             class: "fa-500px",
//         },
//         {
//             class: "fa-amazon",
//         },
//         {
//             class: "fa-calendar-plus-o",
//         },
//         {
//             class: "fa-calendar-minus-o",
//         },
//         {
//             class: "fa-calendar-times-o",
//         },
//         {
//             class: "fa-calendar-check-o",
//         },
//         {
//             class: "fa-industry",
//         },
//         {
//             class: "fa-map-pin",
//         },
//         {
//             class: "fa-map-signs",
//         },
//         {
//             class: "fa-map-o",
//         },
//         {
//             class: "fa-map",
//         },
//         {
//             class: "fa-commenting",
//         },
//         {
//             class: "fa-commenting-o",
//         },
//         {
//             class: "fa-houzz",
//         },
//         {
//             class: "fa-vimeo",
//         },
//         {
//             class: "fa-black-tie",
//         },
//         {
//             class: "fa-fonticons",
//         },
//         {
//             class: "fa-reddit-alien",
//         },
//         {
//             class: "fa-edge",
//         },
//         {
//             class: "fa-credit-card-alt",
//         },
//         {
//             class: "fa-codiepie",
//         },
//         {
//             class: "fa-modx",
//         },
//         {
//             class: "fa-fort-awesome",
//         },
//         {
//             class: "fa-usb",
//         },
//         {
//             class: "fa-product-hunt",
//         },
//         {
//             class: "fa-mixcloud",
//         },
//         {
//             class: "fa-scribd",
//         },
//         {
//             class: "fa-pause-circle",
//         },
//         {
//             class: "fa-pause-circle-o",
//         },
//         {
//             class: "fa-stop-circle",
//         },
//         {
//             class: "fa-stop-circle-o",
//         },
//         {
//             class: "fa-shopping-bag",
//         },
//         {
//             class: "fa-shopping-basket",
//         },
//         {
//             class: "fa-hashtag",
//         },
//         {
//             class: "fa-bluetooth",
//         },
//         {
//             class: "fa-bluetooth-b",
//         },
//         {
//             class: "fa-percent",
//         },
//         {
//             class: "fa-gitlab",
//         },
//         {
//             class: "fa-wpbeginner",
//         },
//         {
//             class: "fa-wpforms",
//         },
//         {
//             class: "fa-envira",
//         },
//         {
//             class: "fa-universal-access",
//         },
//         {
//             class: "fa-wheelchair-alt",
//         },
//         {
//             class: "fa-question-circle-o",
//         },
//         {
//             class: "fa-blind",
//         },
//         {
//             class: "fa-audio-description",
//         },
//         {
//             class: "fa-volume-control-phone",
//         },
//         {
//             class: "fa-braille",
//         },
//         {
//             class: "fa-assistive-listening-systems",
//         },
//         {
//             class: "fa-asl-interpreting",
//         },
//         {
//             class: "fa-american-sign-language-interpreting",
//         },
//         {
//             class: "fa-deafness",
//         },
//         {
//             class: "fa-hard-of-hearing",
//         },
//         {
//             class: "fa-deaf",
//         },
//         {
//             class: "fa-glide",
//         },
//         {
//             class: "fa-glide-g",
//         },
//         {
//             class: "fa-signing",
//         },
//         {
//             class: "fa-sign-language",
//         },
//         {
//             class: "fa-low-vision",
//         },
//         {
//             class: "fa-viadeo",
//         },
//         {
//             class: "fa-viadeo-square",
//         },
//         {
//             class: "fa-snapchat",
//         },
//         {
//             class: "fa-snapchat-ghost",
//         },
//         {
//             class: "fa-snapchat-square",
//         },
//         {
//             class: "fa-pied-piper",
//         },
//         {
//             class: "fa-first-order",
//         },
//         {
//             class: "fa-yoast",
//         },
//         {
//             class: "fa-themeisle",
//         },
//         {
//             class: "fa-google-plus-circle",
//         },
//         {
//             class: "fa-google-plus-official",
//         },
//         {
//             class: "fa-fa",
//         },
//         {
//             class: "fa-font-awesome",
//         },
//         {
//             class: "fa-handshake-o",
//         },
//         {
//             class: "fa-envelope-open",
//         },
//         {
//             class: "fa-envelope-open-o",
//         },
//         {
//             class: "fa-linode",
//         },
//         {
//             class: "fa-address-book",
//         },
//         {
//             class: "fa-address-book-o",
//         },
//         {
//             class: "fa-vcard",
//         },
//         {
//             class: "fa-address-card",
//         },
//         {
//             class: "fa-vcard-o",
//         },
//         {
//             class: "fa-address-card-o",
//         },
//         {
//             class: "fa-user-circle",
//         },
//         {
//             class: "fa-user-circle-o",
//         },
//         {
//             class: "fa-user-o",
//         },
//         {
//             class: "fa-id-badge",
//         },
//         {
//             class: "fa-drivers-license",
//         },
//         {
//             class: "fa-id-card",
//         },
//         {
//             class: "fa-drivers-license-o",
//         },
//         {
//             class: "fa-id-card-o",
//         },
//         {
//             class: "fa-quora",
//         },
//         {
//             class: "fa-free-code-camp",
//         },
//         {
//             class: "fa-telegram",
//         },
//         {
//             class: "fa-thermometer-4",
//         },
//         {
//             class: "fa-thermometer",
//         },
//         {
//             class: "fa-thermometer-full",
//         },
//         {
//             class: "fa-thermometer-3",
//         },
//         {
//             class: "fa-thermometer-three-quarters",
//         },
//         {
//             class: "fa-thermometer-2",
//         },
//         {
//             class: "fa-thermometer-half",
//         },
//         {
//             class: "fa-thermometer-1",
//         },
//         {
//             class: "fa-thermometer-quarter",
//         },
//         {
//             class: "fa-thermometer-0",
//         },
//         {
//             class: "fa-thermometer-empty",
//         },
//         {
//             class: "fa-shower",
//         },
//         {
//             class: "fa-bathtub",
//         },
//         {
//             class: "fa-s15",
//         },
//         {
//             class: "fa-bath",
//         },
//         {
//             class: "fa-podcast",
//         },
//         {
//             class: "fa-window-maximize",
//         },
//         {
//             class: "fa-window-minimize",
//         },
//         {
//             class: "fa-window-restore",
//         },
//         {
//             class: "fa-times-rectangle",
//         },
//         {
//             class: "fa-window-close",
//         },
//         {
//             class: "fa-times-rectangle-o",
//         },
//         {
//             class: "fa-window-close-o",
//         },
//         {
//             class: "fa-bandcamp",
//         },
//         {
//             class: "fa-grav",
//         },
//         {
//             class: "fa-etsy",
//         },
//         {
//             class: "fa-imdb",
//         },
//         {
//             class: "fa-ravelry",
//         },
//         {
//             class: "fa-eercast",
//         },
//         {
//             class: "fa-microchip",
//         },
//         {
//             class: "fa-snowflake-o",
//         },
//         {
//             class: "fa-superpowers",
//         },
//         {
//             class: "fa-wpexplorer",
//         },
//         {
//             class: "fa-meetup",
//         },
//     ],
//     start: function () {
//         var self = this;
//         var defs = [this._super.apply(this, arguments)];
//         $(this.$el).addClass('popover_widget').attr("data-toggle","popover").attr("data-content", qweb.render('poi_scrum.icon_widget', {widget: self.icons}));
//         this.$el.popover({
        
//             // 'selector': '.popover_widget',
//             'placement': 'auto',
//             'container': 'body',
//             'html': true,
//             'trigger': 'click,focus',
//             // 'animation': false,
//             'toggle': 'popover',
//             // 'content':  qweb.render('poi_scrum.icon_widget', {widget: self.icons}),
//             'template': qweb.render('poi_scrum.icon_popover'),
//         });
//         $('body').on('click','.icon', function (ev) {
//             ev.preventDefault();
            
//             var $event = $(ev.currentTarget);
//             var data = $event.attr('data-id');
//             $(self.$el).val(data);
//             self._setValue(data);
//             self.$el.popover('hide');
//         });
//         return $.when.apply($, defs);
//     },

//     _onClick: function (ev) {
//         ev.preventDefault();
//         var icon = {};
        
//     },
//     _set_icon: function(ev){
//         ev.preventDefault();
//         $(this.$el).value('asd');
//     },
//     // _renderEdit: function () {
//     //     // Keep a reference to the input so $el can become something else
//     //     // without losing track of the actual input.
//     //     var self = this;
//     //     return $.when(this._super.apply(this, arguments)).then(function () {
//     //         self.$el.empty();
//     //     });
//     // },
    
// });

// fieldRegistry.add('icon_widget', icon_widget);

// });
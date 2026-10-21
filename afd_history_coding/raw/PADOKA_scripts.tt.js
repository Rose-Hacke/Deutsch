

'use strict';

// BOOTSTRAP COMPONENTS

// =======================================================================================
// TOOLTIP
// =======================================================================================
//
$(document).ready(function () {
  if ($('*[data-toggle="tooltip"]').length) {
    $('body').tooltip({
      selector: '[data-toggle="tooltip"]'
    });
  }
});
/* eslint-disable */
$(document).ready(function () {

  // ---------------------- link ui ----------------------
  // prevent dropdown from closing
  $(document).on('click', '.js-dropdown-moreActions .dropdown-menu', function (e) {
    e.stopPropagation();
  });
  // temporarily copy data attr to an input so it can be copied via execCommand
  $('body').on('mousedown', '.js-copy-link', function () {
    const link = $(this).attr('data-link');
    const $temp = $("<input>");
    $("body").append($temp);
    $temp.val(link).select();
    document.execCommand("copy");
    $temp.remove();
  });
  // init specific tooltip
  $('html').popover({
    selector: '.js-copy-link-popover',
    placement: 'top',
    trigger: 'focus',
    template: '<div class="popover popover-success" role="tooltip"><div class="arrow"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>'
  });

  // ---------------------- link logic ----------------------
  let qLinkConditional = false;
  let actionLinkUrl = '';

  const setAnonPath = (urlString) => urlString.replace('portal/', 'portal/');

  const setQLinkConditional = () => {
    qLinkConditional = true;
  };

  const unsetQLinkConditional = () => {
    qLinkConditional = false;
  };

  const setActionLink = (_,e) => {
    // e is the esearch internal params obj for the event, which we use to extract the search query.
    const qParams = e.params;
    var urlQuery = `?` + Object.keys(qParams).map(key => key ? `${key}=${qParams[key]}` : '').join("&");
    actionLinkUrl = setAnonPath(window.location.href.split('?')[0] + urlQuery);
  };

  const unsetActionLink = () => {
    actionLinkUrl = '';
  };

  const setSearchlink = () => {
    if (!qLinkConditional) {
      $('#searchLinkContainer').show();
      if (!actionLinkUrl) {
        const ctx = ESearch.getPageContext();
        const searchPage = ctx?.page;
        const searchQuery = ctx.lastsearchurl?.url;
        const searchLink = setAnonPath(window.location.href) + `?type=${searchPage}&action=link` + searchQuery;
        $('#copySearchLink').attr('data-link', searchLink);
      } else {
        $('#copySearchLink').attr('data-link', actionLinkUrl);
        unsetActionLink();
      }
    } else {
      $('#searchLinkContainer').hide();
      unsetQLinkConditional();
    }
  };
  // add logic above to relevant esearch event handlers
  ESearch.addEventHandler("efxAction.qlink", setQLinkConditional, {});
  ESearch.addEventHandler("efxAction.link", setActionLink, {});
  const searchtabs = $('.nav-link-searchtab').toArray();
  for (const tab of searchtabs) {
    const tabId = $(tab).attr('id').match(/\d{1,}/)[0];
    ESearch.addEventHandler(`efxSearch.SearchDisplayTriggerGeneric${tabId}`, setSearchlink, {});
  }
});
/* eslint-enable */


// =======================================================================================
// MORE/LESS FACETS
// =======================================================================================

/* eslint-disable */
$(window).on('load', function() {
  function facetsSelection() {
    var $panel = $('.js-facetpanel');

    $panel.each(function() {
      var $this = $(this);
      var $label = $this.find('.js-facetlabel');
      var $label_default = $label.find('.js-facetlabel__default');
      var $label_dynamic = $label.find('.js-facetlabel__dynamic');
      var $selectedItems = $this.find('.efxFacetItem.selected');
      var $facets_all = $this.find('.efxFacetItem');
      var $dynamicCount = $this.find('.js-dynamic-facet-count');

      if ($selectedItems.length > 0) {
        var text = '';
        var spacer;
        $label_default.addClass('js-d-none');
        $label_dynamic.removeClass('js-d-none');
    
        $selectedItems.each(function(index) {
          var $that = $(this);
          (index === 0) ? spacer = '' : spacer = ', ';
          text = text + spacer + $that.contents().get(0).nodeValue;
          $label_dynamic.text(text);
        }); 
      } else {
        $label_default.removeClass('js-d-none');
        $label_dynamic.addClass('js-d-none');
      }

      $dynamicCount.text($facets_all.length);
    });
  }

  if (typeof ESearch !== 'undefined') {
    ESearch.addEventHandler('reportLoaded.ViewportMain', facetsSelection, {});
  }
});
/* eslint-enable */

// =======================================================================================
// Hypersearchlinks
// =======================================================================================
$(document).ready(function () {
  /*
  * output fields: <a class="qlink" data-term="SUB=POLITIK" data-text="Politik" href="#">Politik</a>
  * Anf�hrungszeichen im Text ersetzen [.rt "'"" "''"]
  */

  /* home page topics, link in news, searchtree */
  $('.qlink').click(function () {
    var v1 = $(this).data('term');
    var v2 = encodeURIComponent(v1);
    var t1 = $(this).data('text');
    var t2 = encodeURIComponent(t1);
    // star output field replaces " with '. ' is now replaced with %22
    var q = v2.replace(/\'/g, '%22');
    var qtext = t2.replace(/\'/g, '%22');
    // var path = "browse.tt.html?type=link&q=" + q + "&qtext=" + qtext + "&action=qlink";
    var path = 'browse.tt.html?type=professional&q=' + q + '&qtext=' + qtext + '&action=link';
    console.log(path)
    window.location.href = path;
  });
  /* search tid: serials */
  $('a.qtidlink').click(function () {
    var v1 = $(this).data('tid');
    var v2 = encodeURIComponent(v1);
    var t1 = $(this).data('text');
    var t2 = encodeURIComponent(t1);
    // star output field replaces " with '. ' is now replaced with %22
    var q = v2.replace(/\'/g, '%22');
    var qtext = t2.replace(/\'/g, '%22');
    // var path = "browse.tt.html?type=link&qtid=" + q + "&qtext=" + qtext + "&action=qlink";
    var path = 'browse.tt.html?type=professional&qtid=' + q + '&qtext=' + qtext + '&action=link';
    console.log(path)
    window.location.href = path;
  });
  /* mongo searchtree */
  $('.mlink').click(function () {
    var v = JSON.stringify($(this).data('term'));
    var t = $(this).data('text');
    var q = encodeURIComponent(v);
    var qtext = encodeURIComponent(t);
    var path = 'browse.tt.html?type=link&q=' + q + '&qtext=' + qtext + '&action=mlink&db=Mongo';
    console.log(path)
    window.location.href = path;
  });
});

/* home page: link in news (old version) */
function SetSearchLink (v, t) {
  var q = encodeURIComponent(v);
  var qtext = encodeURIComponent(t);
  var path = 'browse.tt.html?type=link&q=' + q + '&qtext=' + qtext + '&action=qlink';
  console.log(path)
  window.location.href = path;
}
// =======================================================================================
// DataEntry
// =======================================================================================
function edit (u) {
  u += '&ts=' + $.now();
  var EditWindow = window.open(u, 'EditWindow', 'left=10,top=10,resizable=yes,scrollbars=yes');
  EditWindow.focus();
}

/*--- Menu build (pho) ---*/
$(document).ready(function () {
  var $navContainer = $('#js-dataentry-content');
  var idPrefixList = 'js-dataentry-list';
  var idPrefixListItem = 'js-dataentry-listitem';
  var $card = $('.js-dataentry-card');
  var $bodyDataEntry = $('body.dataentry');

  if ($bodyDataEntry.length) {
    $card.each(function (i) {
      var $this = $(this);
      var $navEl = $this.find('.js-dataentry-navelement');

      // change initial index to 1000
      i = (i + 1) * 1000;

      // markup for unordered list
      var $list = $('<ul role="tablist" class="dataentry-list" id=' + '"' + idPrefixList + '-' + i + '"' + '></ul>');

      // add list to container
      $navContainer.append($list);

      // loop through all items in card
      $navEl.each(function (j) {
        var $that = $(this);

        // change initial index to 1
        j = j + 1;

        // add id to card item
        $that.attr({
          'id': idPrefixListItem + '-' + i + '-' + j
        });

        // create list item for each card item and add anchor related to card item
        var listItem = '<li role="tab" class="dataentry-listitem"><a class="js-dataentry-anchor" href="#' + idPrefixListItem + '-' + i + '-' + j + '">' + $that.text() + '</a></li>';

        // add listitems to list
        $list.append(listItem);
      });
    });

    $('.js-dataentry-anchor').on('click', function (e) {
      e.preventDefault();

      var href = $(this).attr('href');
      var $id = $(href);
      var $collapseHeader = $id.parents('.js-dataentry-card').find('.collapse');

      // check if parent (collapse) is expanded
      if (!$collapseHeader.hasClass('show')) {
        $collapseHeader.collapse('show');
      }

      /* animation shamelessly borrowed from https://wp-mix.com/jquery-scroll-target-offset/ */
      var offset = 85;
      var target = this.hash;
      if ($(this).data('offset') !== undefined) {
        offset = $(this).data('offset');
      }
      $('html, body').stop().animate({
        'scrollTop': $(target).offset().top - offset
      }, 500, 'swing', function () {
        // window.location.hash = target;

        // zoom in headline to indicate position
        $id.addClass('js-el-zoom');
        setTimeout(function () {
          $id.removeClass('js-el-zoom');
        }, 400);
      });
    });

    var $navTriggerBtn = $('.js-btn-nav-trigger');
    var $sidebar = $('.js-dataentry-sidebar');

    $navTriggerBtn.on('click', function (e) {
      e.preventDefault();
      var $this = $(this);
      $this.toggleClass('js-btn-nav-trigger--active');
      $sidebar.toggleClass('js-dataentry-sidebar--visible');
    });

    $('.js-dataentry-content, .js-dataentry-anchor').on('click', function (e) {
      e.preventDefault();
      if ($navTriggerBtn.hasClass('js-btn-nav-trigger--active')) {
        $navTriggerBtn.removeClass('js-btn-nav-trigger--active');
        $sidebar.removeClass('js-dataentry-sidebar--visible');
      }
    });
  }
});

/*--- Misc (Nw) ---*/
//  custom.js
//  Created NW - 2018
//  This version is in development for Di-Norms

var lastSearchLink;

// Hide the multiocc "X" when it is only 1 or show when its more Occs
$('.addOcc').click(function(){
  //retun only the field name without the other stuff ORIG-1-addOcc -> ORIG
  let getID = $(this).attr('id').split(/\-[^.]*$/);
  let element = $("#" + getID[0] + "--panel");
  let numOfOccs = element.find(".remOcc").length + 1;
  console.log(numOfOccs)

  if(numOfOccs > 1){
    element.find(".remOcc").removeClass("d-none");
  }
});

$('.remOcc').click(function(){
  let getID = $(this).attr('id').split(/\-[^.]*$/);
  let element = $("#" + getID[0] + "--panel");
  let numOfOccs = element.find(".remOcc").length - 1;
  
  if(numOfOccs == 1 && getID[0] != 'VDOK' && getID[0] != 'DAEN' && getID[0] != 'SYDO' && element.find("input").attr('readonly') != 'readonly'){
    element.find(".remOcc").addClass("d-none");
  }
});

//Set the current date to the hand over id
function checkSetDate(tgtid) {
  var Datum = new Date();
  var Tag = Datum.getDate();
  var Monat = Datum.getMonth() + 1;
  var Jahr = Datum.getFullYear();
  var Stunden = Datum.getHours();
  var Minuten = Datum.getMinutes();
  Minuten = ((Minuten < 10) ? "0" + Minuten : Minuten);
  Tag = ((Tag < 10) ? "0" + Tag : Tag);
  Monat = ((Monat < 10) ? "0" + Monat : Monat);
  ndat = Jahr + "-" + Monat + "-" + Tag;
  document.getElementById(tgtid).value = ndat;
  //alert (ndat);
}

//Check and uncheck the checkbox and if needed call the funktion to set time
$('.custom-control-input').click(function(){
  let checkCheckbox = $(this).next('input').attr('value');
  var dateFieldID = $(this).parent().prev('.input-group').children('.form-control').attr('id');
  var checkShouldSetDate = $(this).attr('class');

  if(checkCheckbox === ""){
    $(this).next('input').val('x');
    
    if(checkShouldSetDate === "custom-control-input setDate"){
      checkSetDate(dateFieldID);
    }
  }else if(checkCheckbox === "x"){
    $(this).next('input').val('--CLEAR--');
    
    if(checkShouldSetDate === "custom-control-input setDate"){
      $(this).parent().prev('.input-group').children('input').val('');
    }
  }else{
    $(this).next('input').val('x');
    
    if(checkShouldSetDate === "custom-control-input setDate"){
      checkSetDate(dateFieldID);
    }
  }
});

var search_result_fld = '';
function openSearchWinTrig(who, win_url, win_name, wi, hi) {
  // This is the same basic function as the openSearchWin() below, but modified to work only with an <img>
  // tag having the same "id" as the field to paste into, + "-trigger" suffix.
  // Example : if the field to paste into has the id="NREF-3", then the <img> tag should have the id="NREF-3-trigger".
  // open another window, with the url given as document, and dimensions
  // given by wi (width) and hi (height)
  // also create a new var in the new window, referring back to the opening window (iow, this one)
  // and also create another var there, referring to the id of the element in which the result should be pasted back here
  var debug = 0;
  var myId = who.id;
  //alert ("caller is : " + myId);
  var myTargetId = myId.replace(/-trigger$/, "");
  var myurl = win_url;
  myurl = myurl.replace(/(\x0D|\x0A)/g, "");
  // debug == 0 ? debug = 0 : alert('openSearchWin(), myurl = ' + url);
  var winFeatures =
    'location=yes,directories=no,toolbar=no,scrollbars=yes,resizable=yes,status=yes'
    + ',height=' + hi
    + ',width=' + wi;
  // debug == 0 ? debug = 0 : alert('openSearchWin(), opening window, features = ' + winFeatures);
  var pickwin = window.open(myurl, win_name, winFeatures); // open the window with the requested url
  pickwin = window.open('', win_name); // make sure we have a ref.
  // store locally the id of the field we want to paste the result in, so that the set_result_field function can find it
  window.search_result_fld = myTargetId;
  pickwin.moveTo(30, 30); // small offset to make sure it's visible
  pickwin.focus(); // bring it in front
  return pickwin; // return ref to the new window object
}
function openSearchWin(fld_id, win_url, win_name, wi, hi) {
  // open another window, with the url given as document, and dimensions
  // given by wi (width) and hi (height)
  // also create a new var in the new window, referring back to the opening window (iow, this one)
  // and also create another var there, referring to the id of the element in which the result should be pasted back here
  var debug = 0;
  var myurl = win_url;
  myurl = myurl.replace(/(\x0D|\x0A)/g, "");
  debug == 0 ? debug = 0 : alert('openSearchWin(), myurl = ' + url);
  //var id_store = document.getElementById('de-result-id'); // store the id there
  //id_store.value = fld_id;
  //alert('openSearchWin(), id_store value = ' + document.getElementById('de-result-id').value);
  var winFeatures =
    'location=yes,directories=no,toolbar=no,scrollbars=yes,resizable=yes,status=yes'
    + ',height=' + hi
    + ',width=' + wi;

  debug == 0 ? debug = 0 : alert('openSearchWin(), opening window, features = ' + winFeatures);

  var pickwin = window.open(myurl, win_name, winFeatures); // open the window with the requested url
  pickwin = window.open('', win_name); // make sure we have a ref.
  // store locally the id of the field we want to paste the result in, so that the set_result_field function can find it
  window.search_result_fld = fld_id;
  //alert('openSearchWin(): (in picklist window, result field id is : ' + pickwin.pick_result_fld);
  pickwin.moveTo(30, 30); // small offset to make sure it's visible
  pickwin.focus(); // bring it in front
  return pickwin; // return ref to the new window object
}
function set_result_field(result, close_win) {
  // this function is called by the child picklist window, don't remove it !
  // close_win, if supplied, is a reference to that child window, and indicates that we want to close it
  document.getElementById(window.search_result_fld).value = result;
  if (close_win != null) {
    close_win.close();
  }
}
function retrieve_result_field() {
  // used by child window
  // another possible way for the child to set the value
  return document.getElementById(window.search_result_fld);
}

$('.required').click(function(){
  var RqId = $(this).attr("id");
  if($('#' + RqId).focus()){
    $('#' + RqId).css('border-color', '');
  }
});



// =======================================================================================
// MENU-TAB (ACCOUNT)
// =======================================================================================

$(function () {
  var current_page_URL = location.protocol + '//' + location.host + location.pathname;
  var $link = $('.menu-tab > li > a');
  $link.each(function () {
    var $this = $(this);
    if ($this.attr('href') !== '#') {
      var target_URL = $this.prop('href');
      if (target_URL === current_page_URL) {
        $this.parent('li').removeClass('active').addClass('active');
        return false;
      }
    }
  });
});

// START 2018-06-25 add sticky function to menu tabs (pho)
$(function () {
  var $menuTab = $('.js-menu-tab');

  if ($menuTab.length) {
    $('body').find($menuTab).sticky({
      topSpacing: 50
    });
  }
});
// END 2018-06-25 add sticky function to menu tabs (pho)
// =======================================================================================
// REQUEST
// =======================================================================================
$(document).ready(function () {
  var $reloadLink = $('.js-reload');

  if ($reloadLink.length) {
    $reloadLink.on('click', function (e) {
      // reload page
      window.location.href = window.location.href;
    });
  }
});
// =======================================================================================
// INPUT TOGGLE TRIGGER
// =======================================================================================
$(window).on('load', function () {
  
  function inputEdit ($ref) {
    var $form = $ref.find('.js-input-toggle-form');
    var origFormVal = $form.serialize();

    var $btnEdit = $ref.find('.js-input-edit-trigger');
    var $btnReset = $ref.find('.js-input-reset-trigger');
    var $btnClauseSubmit = $ref.find('.js-clause-submit');
    var $btnCommentSubmit = $ref.find('.js-comment-submit');
    var $btnMultiOcc = $ref.find('.js-multiocc-add');

    var $elToggle = $ref.find('.js-toggleable');

    $btnEdit.on('click', function () {
      $(this).addClass('js-d-none');
      $btnReset.removeClass('js-d-none');
      $elToggle.prop('disabled', false);
      $btnMultiOcc.removeClass('js-d-none');
    });

    $btnReset.on('click', function () {
      $(this).addClass('js-d-none');
      $btnEdit.removeClass('js-d-none');
      $elToggle.prop('disabled', true);
      $btnClauseSubmit.addClass('js-d-none');
      $btnCommentSubmit.addClass('js-d-none');
      $btnMultiOcc.addClass('js-d-none');
      $('.js-occGroup-new').remove();
    });

    $('.js-input-toggle-form .js-toggleable').on('change input', function() {
      if ($form.serialize() !== origFormVal) {
        $btnClauseSubmit.removeClass('js-d-none');
        $btnCommentSubmit.removeClass('js-d-none');
      } else {
        $btnClauseSubmit.addClass('js-d-none');
        $btnCommentSubmit.addClass('js-d-none');
      }
    });
  }

  $('body').on('show.bs.modal', '.js-modal-edit', function (e) {
    inputEdit($(this));
  })
});
// =======================================================================================
// COMMENT COLLAPSE
// =======================================================================================
$(window).on('load', function () {

  function collapseTrigger () {
    var $collapseTrigger = $('.js-btn-acc');

    $collapseTrigger.each(function (i) {
      var $this = $(this);
      var $collapse = $this.parent('.js-btn-collapse');
      var $collapseHeader = $collapse.parent('.js-acc');
      var collapseHeaderWidth;
      var count = 0;

      $this.on('click', function (e) {

        if (count === 0) {
          collapseHeaderWidth = $this.outerWidth();
          count = 1;
        }

        if ($this.hasClass('js-clickblock')) {
          e.preventDefault();
          e.stopPropagation();
        } else {
          if ($collapse.hasClass('js-btn-collapse--active')) {
            $collapse.removeClass('js-btn-collapse--active');
            $collapseHeader.animate({
              width: collapseHeaderWidth + 3  //add extra pixels to prevent unwanted text wrapping
            });
          } else {
            $collapse.addClass('js-btn-collapse--active');
            $collapseHeader.animate({
              width: '100%'
            });
          }
  
          // dirty hack to prevent doubleclicks which could lead to bugs
          $this.addClass('js-clickblock');
  
          // enable next click event after 300ms
          setTimeout(function () {
            $this.removeClass('js-clickblock');
          }, 300);
        } 
        
      });
    })

  }

  if (typeof ESearch !== 'undefined') {
    ESearch.addEventHandler('reportLoaded.ViewportMain', collapseTrigger, {});
  }
});

// =======================================================================================
// DYNAMIC MODAL CLOSER
// =======================================================================================
function modalCloser (ref) {
  // ref has to be a jQuery object
  let $modal = ref.parents('.modal');
  $modal ? $modal.modal('hide') : false;
}



$(window).on('load', function() {
  var $facetDropdown = $('.js-dropdown-menu--facets');
  if ($facetDropdown.length > 0) {
    $facetDropdown.on("click.bs.dropdown", function (e) {
      if ($(e.target).hasClass('js-facet-trigger')) {
        e.stopPropagation();
        e.preventDefault();
      }
    });
  }
});
$(document).on('ready', function() {
  $('body').on('click', '.js-expand-text-trigger-input', function () {
    var $this = $(this);
    var $text = $this.closest('.js-expand-text-container').prevAll('.js-expand-text');
    var $ellipsis = $text.next('.js-expand-text-ellipsis');
  
    if ($text.length) {
      if ($text.is('.js-d-none')) {
        $text.removeClass('js-d-none');
        $ellipsis.addClass('js-d-none');
      } else {
        $text.addClass('js-d-none');
        $ellipsis.removeClass('js-d-none');
      };
    }
  });
})
// =======================================================================================
// DYNAMIC ELEMENT REMOVER
// =======================================================================================
function removeEl() {
  var $rmElBtn = $('.js-remove-el--trigger');

  $rmElBtn.on('click', function(e) {
    e.preventDefault();
    var $this = $(this);
    $this.parents('.js-remove-el').fadeOut("normal", function() {
      $this.parents('.js-remove-el').remove();
  });
  });
}

$(window).on('load', function() {
  removeEl();
});
/* eslint-disable */
function toggleDisplaySelect($trigger, conditionalClass, $elToShow, $elToHide) {
  if ($elToShow.length && $elToHide.length) {
    $trigger.on('change', function(e) {
      var $this = $(this);

      if ($this.children("option:selected").is(conditionalClass)) {
        $elToShow.removeClass('js-d-none');
        $elToHide.addClass('js-d-none');
        $elToHide.find('input').val('');
      } else {
        $elToHide.removeClass('js-d-none');
        $elToShow.addClass('js-d-none');
        $elToShow.find('input').val('');
      }
    });
  }
}

$(window).on('load', function() {
  toggleDisplaySelect(
    $('.js-toggleDisplaySelect-docType'),
    $('.js-toggleDisplayCondition'),
    $('.js-toggleDisplaySelect-docType__show'),
    $('.js-toggleDisplaySelect-docType__hide')
  )
});
/* eslint-enable */

/* eslint-disable */
$(window).on('load', function() {
  var $dropdownInput = $('.js-dropdown-menu-input');
  if ($dropdownInput.length) {
    $dropdownInput.click(function(e) {
      e.stopPropagation();
    });
  }
});
/* eslint-enable */

/*!
 * typeahead.js 0.11.1
 * https://github.com/twitter/typeahead.js
 * Copyright 2013-2015 Twitter, Inc. and other contributors; Licensed MIT
 * THIS IS THE FIXED VERSION!
 */

(function(root, factory) {
    if (typeof define === "function" && define.amd) {
        define("bloodhound", [ "jquery" ], function(a0) {
            return root["Bloodhound"] = factory(a0);
        });
    } else if (typeof exports === "object") {
        module.exports = factory(require("jquery"));
    } else {
        root["Bloodhound"] = factory(jQuery);
    }
})(this, function($) {
    var _ = function() {
        "use strict";
        return {
            isMsie: function() {
                return /(msie|trident)/i.test(navigator.userAgent) ? navigator.userAgent.match(/(msie |rv:)(\d+(.\d+)?)/i)[2] : false;
            },
            isBlankString: function(str) {
                return !str || /^\s*$/.test(str);
            },
            escapeRegExChars: function(str) {
                return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
            },
            isString: function(obj) {
                return typeof obj === "string";
            },
            isNumber: function(obj) {
                return typeof obj === "number";
            },
            isArray: $.isArray,
            isFunction: $.isFunction,
            isObject: $.isPlainObject,
            isUndefined: function(obj) {
                return typeof obj === "undefined";
            },
            isElement: function(obj) {
                return !!(obj && obj.nodeType === 1);
            },
            isJQuery: function(obj) {
                return obj instanceof $;
            },
            toStr: function toStr(s) {
                return _.isUndefined(s) || s === null ? "" : s + "";
            },
            bind: $.proxy,
            each: function(collection, cb) {
                $.each(collection, reverseArgs);
                function reverseArgs(index, value) {
                    return cb(value, index);
                }
            },
            map: $.map,
            filter: $.grep,
            every: function(obj, test) {
                var result = true;
                if (!obj) {
                    return result;
                }
                $.each(obj, function(key, val) {
                    if (!(result = test.call(null, val, key, obj))) {
                        return false;
                    }
                });
                return !!result;
            },
            some: function(obj, test) {
                var result = false;
                if (!obj) {
                    return result;
                }
                $.each(obj, function(key, val) {
                    if (result = test.call(null, val, key, obj)) {
                        return false;
                    }
                });
                return !!result;
            },
            mixin: $.extend,
            identity: function(x) {
                return x;
            },
            clone: function(obj) {
                return $.extend(true, {}, obj);
            },
            getIdGenerator: function() {
                var counter = 0;
                return function() {
                    return counter++;
                };
            },
            templatify: function templatify(obj) {
                return $.isFunction(obj) ? obj : template;
                function template() {
                    return String(obj);
                }
            },
            defer: function(fn) {
                setTimeout(fn, 0);
            },
            debounce: function(func, wait, immediate) {
                var timeout, result;
                return function() {
                    var context = this, args = arguments, later, callNow;
                    later = function() {
                        timeout = null;
                        if (!immediate) {
                            result = func.apply(context, args);
                        }
                    };
                    callNow = immediate && !timeout;
                    clearTimeout(timeout);
                    timeout = setTimeout(later, wait);
                    if (callNow) {
                        result = func.apply(context, args);
                    }
                    return result;
                };
            },
            throttle: function(func, wait) {
                var context, args, timeout, result, previous, later;
                previous = 0;
                later = function() {
                    previous = new Date();
                    timeout = null;
                    result = func.apply(context, args);
                };
                return function() {
                    var now = new Date(), remaining = wait - (now - previous);
                    context = this;
                    args = arguments;
                    if (remaining <= 0) {
                        clearTimeout(timeout);
                        timeout = null;
                        previous = now;
                        result = func.apply(context, args);
                    } else if (!timeout) {
                        timeout = setTimeout(later, remaining);
                    }
                    return result;
                };
            },
            stringify: function(val) {
                return _.isString(val) ? val : JSON.stringify(val);
            },
            noop: function() {}
        };
    }();
    var VERSION = "0.11.1";
    var tokenizers = function() {
        "use strict";
        return {
            nonword: nonword,
            whitespace: whitespace,
            obj: {
                nonword: getObjTokenizer(nonword),
                whitespace: getObjTokenizer(whitespace)
            }
        };
        function whitespace(str) {
            str = _.toStr(str);
            return str ? str.split(/\s+/) : [];
        }
        function nonword(str) {
            str = _.toStr(str);
            return str ? str.split(/\W+/) : [];
        }
        function getObjTokenizer(tokenizer) {
            return function setKey(keys) {
                keys = _.isArray(keys) ? keys : [].slice.call(arguments, 0);
                return function tokenize(o) {
                    var tokens = [];
                    _.each(keys, function(k) {
                        tokens = tokens.concat(tokenizer(_.toStr(o[k])));
                    });
                    return tokens;
                };
            };
        }
    }();
    var LruCache = function() {
        "use strict";
        function LruCache(maxSize) {
            this.maxSize = _.isNumber(maxSize) ? maxSize : 100;
            this.reset();
            if (this.maxSize <= 0) {
                this.set = this.get = $.noop;
            }
        }
        _.mixin(LruCache.prototype, {
            set: function set(key, val) {
                var tailItem = this.list.tail, node;
                if (this.size >= this.maxSize) {
                    this.list.remove(tailItem);
                    delete this.hash[tailItem.key];
                    this.size--;
                }
                if (node = this.hash[key]) {
                    node.val = val;
                    this.list.moveToFront(node);
                } else {
                    node = new Node(key, val);
                    this.list.add(node);
                    this.hash[key] = node;
                    this.size++;
                }
            },
            get: function get(key) {
                var node = this.hash[key];
                if (node) {
                    this.list.moveToFront(node);
                    return node.val;
                }
            },
            reset: function reset() {
                this.size = 0;
                this.hash = {};
                this.list = new List();
            }
        });
        function List() {
            this.head = this.tail = null;
        }
        _.mixin(List.prototype, {
            add: function add(node) {
                if (this.head) {
                    node.next = this.head;
                    this.head.prev = node;
                }
                this.head = node;
                this.tail = this.tail || node;
            },
            remove: function remove(node) {
                node.prev ? node.prev.next = node.next : this.head = node.next;
                node.next ? node.next.prev = node.prev : this.tail = node.prev;
            },
            moveToFront: function(node) {
                this.remove(node);
                this.add(node);
            }
        });
        function Node(key, val) {
            this.key = key;
            this.val = val;
            this.prev = this.next = null;
        }
        return LruCache;
    }();
    var PersistentStorage = function() {
        "use strict";
        var LOCAL_STORAGE;
        try {
            LOCAL_STORAGE = window.localStorage;
            LOCAL_STORAGE.setItem("~~~", "!");
            LOCAL_STORAGE.removeItem("~~~");
        } catch (err) {
            LOCAL_STORAGE = null;
        }
        function PersistentStorage(namespace, override) {
            this.prefix = [ "__", namespace, "__" ].join("");
            this.ttlKey = "__ttl__";
            this.keyMatcher = new RegExp("^" + _.escapeRegExChars(this.prefix));
            this.ls = override || LOCAL_STORAGE;
            !this.ls && this._noop();
        }
        _.mixin(PersistentStorage.prototype, {
            _prefix: function(key) {
                return this.prefix + key;
            },
            _ttlKey: function(key) {
                return this._prefix(key) + this.ttlKey;
            },
            _noop: function() {
                this.get = this.set = this.remove = this.clear = this.isExpired = _.noop;
            },
            _safeSet: function(key, val) {
                try {
                    this.ls.setItem(key, val);
                } catch (err) {
                    if (err.name === "QuotaExceededError") {
                        this.clear();
                        this._noop();
                    }
                }
            },
            get: function(key) {
                if (this.isExpired(key)) {
                    this.remove(key);
                }
                return decode(this.ls.getItem(this._prefix(key)));
            },
            set: function(key, val, ttl) {
                if (_.isNumber(ttl)) {
                    this._safeSet(this._ttlKey(key), encode(now() + ttl));
                } else {
                    this.ls.removeItem(this._ttlKey(key));
                }
                return this._safeSet(this._prefix(key), encode(val));
            },
            remove: function(key) {
                this.ls.removeItem(this._ttlKey(key));
                this.ls.removeItem(this._prefix(key));
                return this;
            },
            clear: function() {
                var i, keys = gatherMatchingKeys(this.keyMatcher);
                for (i = keys.length; i--; ) {
                    this.remove(keys[i]);
                }
                return this;
            },
            isExpired: function(key) {
                var ttl = decode(this.ls.getItem(this._ttlKey(key)));
                return _.isNumber(ttl) && now() > ttl ? true : false;
            }
        });
        return PersistentStorage;
        function now() {
            return new Date().getTime();
        }
        function encode(val) {
            return JSON.stringify(_.isUndefined(val) ? null : val);
        }
        function decode(val) {
            return $.parseJSON(val);
        }
        function gatherMatchingKeys(keyMatcher) {
            var i, key, keys = [], len = LOCAL_STORAGE.length;
            for (i = 0; i < len; i++) {
                if ((key = LOCAL_STORAGE.key(i)).match(keyMatcher)) {
                    keys.push(key.replace(keyMatcher, ""));
                }
            }
            return keys;
        }
    }();
    var Transport = function() {
        "use strict";
        var pendingRequestsCount = 0, pendingRequests = {}, maxPendingRequests = 6, sharedCache = new LruCache(10);
        function Transport(o) {
            o = o || {};
            this.cancelled = false;
            this.lastReq = null;
            this._send = o.transport;
            this._get = o.limiter ? o.limiter(this._get) : this._get;
            this._cache = o.cache === false ? new LruCache(0) : sharedCache;
        }
        Transport.setMaxPendingRequests = function setMaxPendingRequests(num) {
            maxPendingRequests = num;
        };
        Transport.resetCache = function resetCache() {
            sharedCache.reset();
        };
        _.mixin(Transport.prototype, {
            _fingerprint: function fingerprint(o) {
                o = o || {};
                return o.url + o.type + $.param(o.data || {});
            },
            _get: function(o, cb) {
                var that = this, fingerprint, jqXhr;
                fingerprint = this._fingerprint(o);
                if (this.cancelled || fingerprint !== this.lastReq) {
                    return;
                }
                if (jqXhr = pendingRequests[fingerprint]) {
                    jqXhr.done(done).fail(fail);
                } else if (pendingRequestsCount < maxPendingRequests) {
                    pendingRequestsCount++;
                    pendingRequests[fingerprint] = this._send(o).done(done).fail(fail).always(always);
                } else {
                    this.onDeckRequestArgs = [].slice.call(arguments, 0);
                }
                function done(resp) {
                    cb(null, resp);
                    that._cache.set(fingerprint, resp);
                }
                function fail() {
                    cb(true);
                }
                function always() {
                    pendingRequestsCount--;
                    delete pendingRequests[fingerprint];
                    if (that.onDeckRequestArgs) {
                        that._get.apply(that, that.onDeckRequestArgs);
                        that.onDeckRequestArgs = null;
                    }
                }
            },
            get: function(o, cb) {
                var resp, fingerprint;
                cb = cb || $.noop;
                o = _.isString(o) ? {
                    url: o
                } : o || {};
                fingerprint = this._fingerprint(o);
                this.cancelled = false;
                this.lastReq = fingerprint;
                if (resp = this._cache.get(fingerprint)) {
                    cb(null, resp);
                } else {
                    this._get(o, cb);
                }
            },
            cancel: function() {
                this.cancelled = true;
            }
        });
        return Transport;
    }();
    var SearchIndex = window.SearchIndex = function() {
        "use strict";
        var CHILDREN = "c", IDS = "i";
        function SearchIndex(o) {
            o = o || {};
            if (!o.datumTokenizer || !o.queryTokenizer) {
                $.error("datumTokenizer and queryTokenizer are both required");
            }
            this.identify = o.identify || _.stringify;
            this.datumTokenizer = o.datumTokenizer;
            this.queryTokenizer = o.queryTokenizer;
            this.reset();
        }
        _.mixin(SearchIndex.prototype, {
            bootstrap: function bootstrap(o) {
                this.datums = o.datums;
                this.trie = o.trie;
            },
            add: function(data) {
                var that = this;
                data = _.isArray(data) ? data : [ data ];
                _.each(data, function(datum) {
                    var id, tokens;
                    that.datums[id = that.identify(datum)] = datum;
                    tokens = normalizeTokens(that.datumTokenizer(datum));
                    _.each(tokens, function(token) {
                        var node, chars, ch;
                        node = that.trie;
                        chars = token.split("");
                        while (ch = chars.shift()) {
                            node = node[CHILDREN][ch] || (node[CHILDREN][ch] = newNode());
                            node[IDS].push(id);
                        }
                    });
                });
            },
            get: function get(ids) {
                var that = this;
                return _.map(ids, function(id) {
                    return that.datums[id];
                });
            },
            search: function search(query) {
                var that = this, tokens, matches;
                tokens = normalizeTokens(this.queryTokenizer(query));
                _.each(tokens, function(token) {
                    var node, chars, ch, ids;
                    if (matches && matches.length === 0) {
                        return false;
                    }
                    node = that.trie;
                    chars = token.split("");
                    while (node && (ch = chars.shift())) {
                        node = node[CHILDREN][ch];
                    }
                    if (node && chars.length === 0) {
                        ids = node[IDS].slice(0);
                        matches = matches ? getIntersection(matches, ids) : ids;
                    } else {
                        matches = [];
                        return false;
                    }
                });
                return matches ? _.map(unique(matches), function(id) {
                    return that.datums[id];
                }) : [];
            },
            all: function all() {
                var values = [];
                for (var key in this.datums) {
                    values.push(this.datums[key]);
                }
                return values;
            },
            reset: function reset() {
                this.datums = {};
                this.trie = newNode();
            },
            serialize: function serialize() {
                return {
                    datums: this.datums,
                    trie: this.trie
                };
            }
        });
        return SearchIndex;
        function normalizeTokens(tokens) {
            tokens = _.filter(tokens, function(token) {
                return !!token;
            });
            tokens = _.map(tokens, function(token) {
                return token.toLowerCase();
            });
            return tokens;
        }
        function newNode() {
            var node = {};
            node[IDS] = [];
            node[CHILDREN] = {};
            return node;
        }
        function unique(array) {
            var seen = {}, uniques = [];
            for (var i = 0, len = array.length; i < len; i++) {
                if (!seen[array[i]]) {
                    seen[array[i]] = true;
                    uniques.push(array[i]);
                }
            }
            return uniques;
        }
        function getIntersection(arrayA, arrayB) {
            var ai = 0, bi = 0, intersection = [];
            arrayA = arrayA.sort();
            arrayB = arrayB.sort();
            var lenArrayA = arrayA.length, lenArrayB = arrayB.length;
            while (ai < lenArrayA && bi < lenArrayB) {
                if (arrayA[ai] < arrayB[bi]) {
                    ai++;
                } else if (arrayA[ai] > arrayB[bi]) {
                    bi++;
                } else {
                    intersection.push(arrayA[ai]);
                    ai++;
                    bi++;
                }
            }
            return intersection;
        }
    }();
    var Prefetch = function() {
        "use strict";
        var keys;
        keys = {
            data: "data",
            protocol: "protocol",
            thumbprint: "thumbprint"
        };
        function Prefetch(o) {
            this.url = o.url;
            this.ttl = o.ttl;
            this.cache = o.cache;
            this.prepare = o.prepare;
            this.transform = o.transform;
            this.transport = o.transport;
            this.thumbprint = o.thumbprint;
            this.storage = new PersistentStorage(o.cacheKey);
        }
        _.mixin(Prefetch.prototype, {
            _settings: function settings() {
                return {
                    url: this.url,
                    type: "GET",
                    dataType: "json"
                };
            },
            store: function store(data) {
                if (!this.cache) {
                    return;
                }
                this.storage.set(keys.data, data, this.ttl);
                this.storage.set(keys.protocol, location.protocol, this.ttl);
                this.storage.set(keys.thumbprint, this.thumbprint, this.ttl);
            },
            fromCache: function fromCache() {
                var stored = {}, isExpired;
                if (!this.cache) {
                    return null;
                }
                stored.data = this.storage.get(keys.data);
                stored.protocol = this.storage.get(keys.protocol);
                stored.thumbprint = this.storage.get(keys.thumbprint);
                isExpired = stored.thumbprint !== this.thumbprint || stored.protocol !== location.protocol;
                return stored.data && !isExpired ? stored.data : null;
            },
            fromNetwork: function(cb) {
                var that = this, settings;
                if (!cb) {
                    return;
                }
                settings = this.prepare(this._settings());
                this.transport(settings).fail(onError).done(onResponse);
                function onError() {
                    cb(true);
                }
                function onResponse(resp) {
                    cb(null, that.transform(resp));
                }
            },
            clear: function clear() {
                this.storage.clear();
                return this;
            }
        });
        return Prefetch;
    }();
    var Remote = function() {
        "use strict";
        function Remote(o) {
            this.url = o.url;
            this.prepare = o.prepare;
            this.transform = o.transform;
            this.transport = new Transport({
                cache: o.cache,
                limiter: o.limiter,
                transport: o.transport
            });
        }
        _.mixin(Remote.prototype, {
            _settings: function settings() {
                return {
                    url: this.url,
                    type: "GET",
                    dataType: "json"
                };
            },
            get: function get(query, cb) {
                var that = this, settings;
                if (!cb) {
                    return;
                }
                query = query || "";
                settings = this.prepare(query, this._settings());
                return this.transport.get(settings, onResponse);
                function onResponse(err, resp) {
                    err ? cb([]) : cb(that.transform(resp));
                }
            },
            cancelLastRequest: function cancelLastRequest() {
                this.transport.cancel();
            }
        });
        return Remote;
    }();
    var oParser = function() {
        "use strict";
        return function parse(o) {
            var defaults, sorter;
            defaults = {
                initialize: true,
                identify: _.stringify,
                datumTokenizer: null,
                queryTokenizer: null,
                sufficient: 5,
                sorter: null,
                local: [],
                prefetch: null,
                remote: null
            };
            o = _.mixin(defaults, o || {});
            !o.datumTokenizer && $.error("datumTokenizer is required");
            !o.queryTokenizer && $.error("queryTokenizer is required");
            sorter = o.sorter;
            o.sorter = sorter ? function(x) {
                return x.sort(sorter);
            } : _.identity;
            o.local = _.isFunction(o.local) ? o.local() : o.local;
            o.prefetch = parsePrefetch(o.prefetch);
            o.remote = parseRemote(o.remote);
            return o;
        };
        function parsePrefetch(o) {
            var defaults;
            if (!o) {
                return null;
            }
            defaults = {
                url: null,
                ttl: 24 * 60 * 60 * 1e3,
                cache: true,
                cacheKey: null,
                thumbprint: "",
                prepare: _.identity,
                transform: _.identity,
                transport: null
            };
            o = _.isString(o) ? {
                url: o
            } : o;
            o = _.mixin(defaults, o);
            !o.url && $.error("prefetch requires url to be set");
            o.transform = o.filter || o.transform;
            o.cacheKey = o.cacheKey || o.url;
            o.thumbprint = VERSION + o.thumbprint;
            o.transport = o.transport ? callbackToDeferred(o.transport) : $.ajax;
            return o;
        }
        function parseRemote(o) {
            var defaults;
            if (!o) {
                return;
            }
            defaults = {
                url: null,
                cache: true,
                prepare: null,
                replace: null,
                wildcard: null,
                limiter: null,
                rateLimitBy: "debounce",
                rateLimitWait: 300,
                transform: _.identity,
                transport: null
            };
            o = _.isString(o) ? {
                url: o
            } : o;
            o = _.mixin(defaults, o);
            !o.url && $.error("remote requires url to be set");
            o.transform = o.filter || o.transform;
            o.prepare = toRemotePrepare(o);
            o.limiter = toLimiter(o);
            o.transport = o.transport ? callbackToDeferred(o.transport) : $.ajax;
            delete o.replace;
            delete o.wildcard;
            delete o.rateLimitBy;
            delete o.rateLimitWait;
            return o;
        }
        function toRemotePrepare(o) {
            var prepare, replace, wildcard;
            prepare = o.prepare;
            replace = o.replace;
            wildcard = o.wildcard;
            if (prepare) {
                return prepare;
            }
            if (replace) {
                prepare = prepareByReplace;
            } else if (o.wildcard) {
                prepare = prepareByWildcard;
            } else {
                prepare = idenityPrepare;
            }
            return prepare;
            function prepareByReplace(query, settings) {
                settings.url = replace(settings.url, query);
                return settings;
            }
            function prepareByWildcard(query, settings) {
                settings.url = settings.url.replace(wildcard, encodeURIComponent(query));
                return settings;
            }
            function idenityPrepare(query, settings) {
                return settings;
            }
        }
        function toLimiter(o) {
            var limiter, method, wait;
            limiter = o.limiter;
            method = o.rateLimitBy;
            wait = o.rateLimitWait;
            if (!limiter) {
                limiter = /^throttle$/i.test(method) ? throttle(wait) : debounce(wait);
            }
            return limiter;
            function debounce(wait) {
                return function debounce(fn) {
                    return _.debounce(fn, wait);
                };
            }
            function throttle(wait) {
                return function throttle(fn) {
                    return _.throttle(fn, wait);
                };
            }
        }
        function callbackToDeferred(fn) {
            return function wrapper(o) {
                var deferred = $.Deferred();
                fn(o, onSuccess, onError);
                return deferred;
                function onSuccess(resp) {
                    _.defer(function() {
                        deferred.resolve(resp);
                    });
                }
                function onError(err) {
                    _.defer(function() {
                        deferred.reject(err);
                    });
                }
            };
        }
    }();
    var Bloodhound = function() {
        "use strict";
        var old;
        old = window && window.Bloodhound;
        function Bloodhound(o) {
            o = oParser(o);
            this.sorter = o.sorter;
            this.identify = o.identify;
            this.sufficient = o.sufficient;
            this.local = o.local;
            this.remote = o.remote ? new Remote(o.remote) : null;
            this.prefetch = o.prefetch ? new Prefetch(o.prefetch) : null;
            this.index = new SearchIndex({
                identify: this.identify,
                datumTokenizer: o.datumTokenizer,
                queryTokenizer: o.queryTokenizer
            });
            o.initialize !== false && this.initialize();
        }
        Bloodhound.noConflict = function noConflict() {
            window && (window.Bloodhound = old);
            return Bloodhound;
        };
        Bloodhound.tokenizers = tokenizers;
        _.mixin(Bloodhound.prototype, {
            __ttAdapter: function ttAdapter() {
                var that = this;
                return this.remote ? withAsync : withoutAsync;
                function withAsync(query, sync, async) {
                    return that.search(query, sync, async);
                }
                function withoutAsync(query, sync) {
                    return that.search(query, sync);
                }
            },
            _loadPrefetch: function loadPrefetch() {
                var that = this, deferred, serialized;
                deferred = $.Deferred();
                if (!this.prefetch) {
                    deferred.resolve();
                } else if (serialized = this.prefetch.fromCache()) {
                    this.index.bootstrap(serialized);
                    deferred.resolve();
                } else {
                    this.prefetch.fromNetwork(done);
                }
                return deferred.promise();
                function done(err, data) {
                    if (err) {
                        return deferred.reject();
                    }
                    that.add(data);
                    that.prefetch.store(that.index.serialize());
                    deferred.resolve();
                }
            },
            _initialize: function initialize() {
                var that = this, deferred;
                this.clear();
                (this.initPromise = this._loadPrefetch()).done(addLocalToIndex);
                return this.initPromise;
                function addLocalToIndex() {
                    that.add(that.local);
                }
            },
            initialize: function initialize(force) {
                return !this.initPromise || force ? this._initialize() : this.initPromise;
            },
            add: function add(data) {
                this.index.add(data);
                return this;
            },
            get: function get(ids) {
                ids = _.isArray(ids) ? ids : [].slice.call(arguments);
                return this.index.get(ids);
            },
            search: function search(query, sync, async) {
                var that = this, local;
                local = this.sorter(this.index.search(query));
                sync(this.remote ? local.slice() : local);
                if (this.remote && local.length < this.sufficient) {
                    this.remote.get(query, processRemote);
                } else if (this.remote) {
                    this.remote.cancelLastRequest();
                }
                return this;
                function processRemote(remote) {
                    var nonDuplicates = [];
                    _.each(remote, function(r) {
                        !_.some(local, function(l) {
                            return that.identify(r) === that.identify(l);
                        }) && nonDuplicates.push(r);
                    });
                    async && async(nonDuplicates);
                }
            },
            all: function all() {
                return this.index.all();
            },
            clear: function clear() {
                this.index.reset();
                return this;
            },
            clearPrefetchCache: function clearPrefetchCache() {
                this.prefetch && this.prefetch.clear();
                return this;
            },
            clearRemoteCache: function clearRemoteCache() {
                Transport.resetCache();
                return this;
            },
            ttAdapter: function ttAdapter() {
                return this.__ttAdapter();
            }
        });
        return Bloodhound;
    }();
    return Bloodhound;
});

(function(root, factory) {
    if (typeof define === "function" && define.amd) {
        define("typeahead.js", [ "jquery" ], function(a0) {
            return factory(a0);
        });
    } else if (typeof exports === "object") {
        module.exports = factory(require("jquery"));
    } else {
        factory(jQuery);
    }
})(this, function($) {
    var _ = function() {
        "use strict";
        return {
            isMsie: function() {
                return /(msie|trident)/i.test(navigator.userAgent) ? navigator.userAgent.match(/(msie |rv:)(\d+(.\d+)?)/i)[2] : false;
            },
            isBlankString: function(str) {
                return !str || /^\s*$/.test(str);
            },
            escapeRegExChars: function(str) {
                return str.replace(/[\-\[\]\/\{\}\(\)\*\+\?\.\\\^\$\|]/g, "\\$&");
            },
            isString: function(obj) {
                return typeof obj === "string";
            },
            isNumber: function(obj) {
                return typeof obj === "number";
            },
            isArray: $.isArray,
            isFunction: $.isFunction,
            isObject: $.isPlainObject,
            isUndefined: function(obj) {
                return typeof obj === "undefined";
            },
            isElement: function(obj) {
                return !!(obj && obj.nodeType === 1);
            },
            isJQuery: function(obj) {
                return obj instanceof $;
            },
            toStr: function toStr(s) {
                return _.isUndefined(s) || s === null ? "" : s + "";
            },
            bind: $.proxy,
            each: function(collection, cb) {
                $.each(collection, reverseArgs);
                function reverseArgs(index, value) {
                    return cb(value, index);
                }
            },
            map: $.map,
            filter: $.grep,
            every: function(obj, test) {
                var result = true;
                if (!obj) {
                    return result;
                }
                $.each(obj, function(key, val) {
                    if (!(result = test.call(null, val, key, obj))) {
                        return false;
                    }
                });
                return !!result;
            },
            some: function(obj, test) {
                var result = false;
                if (!obj) {
                    return result;
                }
                $.each(obj, function(key, val) {
                    if (result = test.call(null, val, key, obj)) {
                        return false;
                    }
                });
                return !!result;
            },
            mixin: $.extend,
            identity: function(x) {
                return x;
            },
            clone: function(obj) {
                return $.extend(true, {}, obj);
            },
            getIdGenerator: function() {
                var counter = 0;
                return function() {
                    return counter++;
                };
            },
            templatify: function templatify(obj) {
                return $.isFunction(obj) ? obj : template;
                function template() {
                    return String(obj);
                }
            },
            defer: function(fn) {
                setTimeout(fn, 0);
            },
            debounce: function(func, wait, immediate) {
                var timeout, result;
                return function() {
                    var context = this, args = arguments, later, callNow;
                    later = function() {
                        timeout = null;
                        if (!immediate) {
                            result = func.apply(context, args);
                        }
                    };
                    callNow = immediate && !timeout;
                    clearTimeout(timeout);
                    timeout = setTimeout(later, wait);
                    if (callNow) {
                        result = func.apply(context, args);
                    }
                    return result;
                };
            },
            throttle: function(func, wait) {
                var context, args, timeout, result, previous, later;
                previous = 0;
                later = function() {
                    previous = new Date();
                    timeout = null;
                    result = func.apply(context, args);
                };
                return function() {
                    var now = new Date(), remaining = wait - (now - previous);
                    context = this;
                    args = arguments;
                    if (remaining <= 0) {
                        clearTimeout(timeout);
                        timeout = null;
                        previous = now;
                        result = func.apply(context, args);
                    } else if (!timeout) {
                        timeout = setTimeout(later, remaining);
                    }
                    return result;
                };
            },
            stringify: function(val) {
                return _.isString(val) ? val : JSON.stringify(val);
            },
            noop: function() {}
        };
    }();
    var WWW = function() {
        "use strict";
        var defaultClassNames = {
            wrapper: "twitter-typeahead",
            input: "tt-input",
            hint: "tt-hint",
            menu: "tt-menu",
            dataset: "tt-dataset",
            suggestion: "tt-suggestion",
            selectable: "tt-selectable",
            empty: "tt-empty",
            open: "tt-open",
            cursor: "tt-cursor",
            highlight: "tt-highlight"
        };
        return build;
        function build(o) {
            var www, classes;
            classes = _.mixin({}, defaultClassNames, o);
            www = {
                css: buildCss(),
                classes: classes,
                html: buildHtml(classes),
                selectors: buildSelectors(classes)
            };
            return {
                css: www.css,
                html: www.html,
                classes: www.classes,
                selectors: www.selectors,
                mixin: function(o) {
                    _.mixin(o, www);
                }
            };
        }
        function buildHtml(c) {
            return {
                wrapper: '<span class="' + c.wrapper + '"></span>',
                menu: '<div class="' + c.menu + '"></div>'
            };
        }
        function buildSelectors(classes) {
            var selectors = {};
            _.each(classes, function(v, k) {
                selectors[k] = "." + v;
            });
            return selectors;
        }
        function buildCss() {
            var css = {
                wrapper: {
                    position: "relative",
                    display: "inline-block"
                },
                hint: {
                    position: "absolute",
                    top: "0",
                    left: "0",
                    borderColor: "transparent",
                    boxShadow: "none",
                    opacity: "1"
                },
                input: {
                    position: "relative",
                    verticalAlign: "top",
                    backgroundColor: "transparent"
                },
                inputWithNoHint: {
                    position: "relative",
                    verticalAlign: "top"
                },
                menu: {
                    position: "absolute",
                    top: "100%",
                    left: "0",
                    zIndex: "100",
                    display: "none"
                },
                ltr: {
                    left: "0",
                    right: "auto"
                },
                rtl: {
                    left: "auto",
                    right: " 0"
                }
            };
            if (_.isMsie()) {
                _.mixin(css.input, {
                    backgroundImage: "url(data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7)"
                });
            }
            return css;
        }
    }();
    var EventBus = function() {
        "use strict";
        var namespace, deprecationMap;
        namespace = "typeahead:";
        deprecationMap = {
            render: "rendered",
            cursorchange: "cursorchanged",
            select: "selected",
            autocomplete: "autocompleted"
        };
        function EventBus(o) {
            if (!o || !o.el) {
                $.error("EventBus initialized without el");
            }
            this.$el = $(o.el);
        }
        _.mixin(EventBus.prototype, {
            _trigger: function(type, args) {
                var $e;
                $e = $.Event(namespace + type);
                (args = args || []).unshift($e);
                this.$el.trigger.apply(this.$el, args);
                return $e;
            },
            before: function(type) {
                var args, $e;
                args = [].slice.call(arguments, 1);
                $e = this._trigger("before" + type, args);
                return $e.isDefaultPrevented();
            },
            trigger: function(type) {
                var deprecatedType;
                this._trigger(type, [].slice.call(arguments, 1));
                if (deprecatedType = deprecationMap[type]) {
                    this._trigger(deprecatedType, [].slice.call(arguments, 1));
                }
            }
        });
        return EventBus;
    }();
    var EventEmitter = function() {
        "use strict";
        var splitter = /\s+/, nextTick = getNextTick();
        return {
            onSync: onSync,
            onAsync: onAsync,
            off: off,
            trigger: trigger
        };
        function on(method, types, cb, context) {
            var type;
            if (!cb) {
                return this;
            }
            types = types.split(splitter);
            cb = context ? bindContext(cb, context) : cb;
            this._callbacks = this._callbacks || {};
            while (type = types.shift()) {
                this._callbacks[type] = this._callbacks[type] || {
                    sync: [],
                    async: []
                };
                this._callbacks[type][method].push(cb);
            }
            return this;
        }
        function onAsync(types, cb, context) {
            return on.call(this, "async", types, cb, context);
        }
        function onSync(types, cb, context) {
            return on.call(this, "sync", types, cb, context);
        }
        function off(types) {
            var type;
            if (!this._callbacks) {
                return this;
            }
            types = types.split(splitter);
            while (type = types.shift()) {
                delete this._callbacks[type];
            }
            return this;
        }
        function trigger(types) {
            var type, callbacks, args, syncFlush, asyncFlush;
            if (!this._callbacks) {
                return this;
            }
            types = types.split(splitter);
            args = [].slice.call(arguments, 1);
            while ((type = types.shift()) && (callbacks = this._callbacks[type])) {
                syncFlush = getFlush(callbacks.sync, this, [ type ].concat(args));
                asyncFlush = getFlush(callbacks.async, this, [ type ].concat(args));
                syncFlush() && nextTick(asyncFlush);
            }
            return this;
        }
        function getFlush(callbacks, context, args) {
            return flush;
            function flush() {
                var cancelled;
                for (var i = 0, len = callbacks.length; !cancelled && i < len; i += 1) {
                    cancelled = callbacks[i].apply(context, args) === false;
                }
                return !cancelled;
            }
        }
        function getNextTick() {
            var nextTickFn;
            if (window.setImmediate) {
                nextTickFn = function nextTickSetImmediate(fn) {
                    setImmediate(function() {
                        fn();
                    });
                };
            } else {
                nextTickFn = function nextTickSetTimeout(fn) {
                    setTimeout(function() {
                        fn();
                    }, 0);
                };
            }
            return nextTickFn;
        }
        function bindContext(fn, context) {
            return fn.bind ? fn.bind(context) : function() {
                fn.apply(context, [].slice.call(arguments, 0));
            };
        }
    }();
    var highlight = function(doc) {
        "use strict";
        var defaults = {
            node: null,
            pattern: null,
            tagName: "strong",
            className: null,
            wordsOnly: false,
            caseSensitive: false
        };
        return function hightlight(o) {
            var regex;
            o = _.mixin({}, defaults, o);
            if (!o.node || !o.pattern) {
                return;
            }
            o.pattern = _.isArray(o.pattern) ? o.pattern : [ o.pattern ];
            regex = getRegex(o.pattern, o.caseSensitive, o.wordsOnly);
            traverse(o.node, hightlightTextNode);
            function hightlightTextNode(textNode) {
                var match, patternNode, wrapperNode;
                if (match = regex.exec(textNode.data)) {
                    wrapperNode = doc.createElement(o.tagName);
                    o.className && (wrapperNode.className = o.className);
                    patternNode = textNode.splitText(match.index);
                    patternNode.splitText(match[0].length);
                    wrapperNode.appendChild(patternNode.cloneNode(true));
                    textNode.parentNode.replaceChild(wrapperNode, patternNode);
                }
                return !!match;
            }
            function traverse(el, hightlightTextNode) {
                var childNode, TEXT_NODE_TYPE = 3;
                for (var i = 0; i < el.childNodes.length; i++) {
                    childNode = el.childNodes[i];
                    if (childNode.nodeType === TEXT_NODE_TYPE) {
                        i += hightlightTextNode(childNode) ? 1 : 0;
                    } else {
                        traverse(childNode, hightlightTextNode);
                    }
                }
            }
        };
        function getRegex(patterns, caseSensitive, wordsOnly) {
            var escapedPatterns = [], regexStr;
            for (var i = 0, len = patterns.length; i < len; i++) {
                escapedPatterns.push(_.escapeRegExChars(patterns[i]));
            }
            regexStr = wordsOnly ? "\\b(" + escapedPatterns.join("|") + ")\\b" : "(" + escapedPatterns.join("|") + ")";
            return caseSensitive ? new RegExp(regexStr) : new RegExp(regexStr, "i");
        }
    }(window.document);
    var Input = function() {
        "use strict";
        var specialKeyCodeMap;
        specialKeyCodeMap = {
            9: "tab",
            27: "esc",
            37: "left",
            39: "right",
            13: "enter",
            38: "up",
            40: "down"
        };
        function Input(o, www) {
            o = o || {};
            if (!o.input) {
                $.error("input is missing");
            }
            www.mixin(this);
            this.$hint = $(o.hint);
            this.$input = $(o.input);
            this.query = this.$input.val();
            this.queryWhenFocused = this.hasFocus() ? this.query : null;
            this.$overflowHelper = buildOverflowHelper(this.$input);
            this._checkLanguageDirection();
            if (this.$hint.length === 0) {
                this.setHint = this.getHint = this.clearHint = this.clearHintIfInvalid = _.noop;
            }
        }
        Input.normalizeQuery = function(str) {
            return _.toStr(str).replace(/^\s*/g, "").replace(/\s{2,}/g, " ");
        };
        _.mixin(Input.prototype, EventEmitter, {
            _onBlur: function onBlur() {
                this.resetInputValue();
                this.trigger("blurred");
            },
            _onFocus: function onFocus() {
                this.queryWhenFocused = this.query;
                this.trigger("focused");
            },
            _onKeydown: function onKeydown($e) {
                var keyName = specialKeyCodeMap[$e.which || $e.keyCode];
                this._managePreventDefault(keyName, $e);
                if (keyName && this._shouldTrigger(keyName, $e)) {
                    this.trigger(keyName + "Keyed", $e);
                }
            },
            _onInput: function onInput() {
                this._setQuery(this.getInputValue());
                this.clearHintIfInvalid();
                this._checkLanguageDirection();
            },
            _managePreventDefault: function managePreventDefault(keyName, $e) {
                var preventDefault;
                switch (keyName) {
                  case "up":
                  case "down":
                    preventDefault = !withModifier($e);
                    break;

                  default:
                    preventDefault = false;
                }
                preventDefault && $e.preventDefault();
            },
            _shouldTrigger: function shouldTrigger(keyName, $e) {
                var trigger;
                switch (keyName) {
                  case "tab":
                    trigger = !withModifier($e);
                    break;

                  default:
                    trigger = true;
                }
                return trigger;
            },
            _checkLanguageDirection: function checkLanguageDirection() {
                var dir = (this.$input.css("direction") || "ltr").toLowerCase();
                if (this.dir !== dir) {
                    this.dir = dir;
                    this.$hint.attr("dir", dir);
                    this.trigger("langDirChanged", dir);
                }
            },
            _setQuery: function setQuery(val, silent) {
                var areEquivalent, hasDifferentWhitespace;
                areEquivalent = areQueriesEquivalent(val, this.query);
                hasDifferentWhitespace = areEquivalent ? this.query.length !== val.length : false;
                this.query = val;
                if (!silent && !areEquivalent) {
                    this.trigger("queryChanged", this.query);
                } else if (!silent && hasDifferentWhitespace) {
                    this.trigger("whitespaceChanged", this.query);
                }
            },
            bind: function() {
                var that = this, onBlur, onFocus, onKeydown, onInput;
                onBlur = _.bind(this._onBlur, this);
                onFocus = _.bind(this._onFocus, this);
                onKeydown = _.bind(this._onKeydown, this);
                onInput = _.bind(this._onInput, this);
                this.$input.on("blur.tt", onBlur).on("focus.tt", onFocus).on("keydown.tt", onKeydown);
                if (!_.isMsie() || _.isMsie() > 9) {
                    this.$input.on("input.tt", onInput);
                } else {
                    this.$input.on("keydown.tt keypress.tt cut.tt paste.tt", function($e) {
                        if (specialKeyCodeMap[$e.which || $e.keyCode]) {
                            return;
                        }
                        _.defer(_.bind(that._onInput, that, $e));
                    });
                }
                return this;
            },
            focus: function focus() {
                this.$input.focus();
            },
            blur: function blur() {
                this.$input.blur();
            },
            getLangDir: function getLangDir() {
                return this.dir;
            },
            getQuery: function getQuery() {
                return this.query || "";
            },
            setQuery: function setQuery(val, silent) {
                this.setInputValue(val);
                this._setQuery(val, silent);
            },
            hasQueryChangedSinceLastFocus: function hasQueryChangedSinceLastFocus() {
                return this.query !== this.queryWhenFocused;
            },
            getInputValue: function getInputValue() {
                return this.$input.val();
            },
            setInputValue: function setInputValue(value) {
                this.$input.val(value);
                this.clearHintIfInvalid();
                this._checkLanguageDirection();
            },
            resetInputValue: function resetInputValue() {
                this.setInputValue(this.query);
            },
            getHint: function getHint() {
                return this.$hint.val();
            },
            setHint: function setHint(value) {
                this.$hint.val(value);
            },
            clearHint: function clearHint() {
                this.setHint("");
            },
            clearHintIfInvalid: function clearHintIfInvalid() {
                var val, hint, valIsPrefixOfHint, isValid;
                val = this.getInputValue();
                hint = this.getHint();
                valIsPrefixOfHint = val !== hint && hint.indexOf(val) === 0;
                isValid = val !== "" && valIsPrefixOfHint && !this.hasOverflow();
                !isValid && this.clearHint();
            },
            hasFocus: function hasFocus() {
                return this.$input.is(":focus");
            },
            hasOverflow: function hasOverflow() {
                var constraint = this.$input.width() - 2;
                this.$overflowHelper.text(this.getInputValue());
                return this.$overflowHelper.width() >= constraint;
            },
            isCursorAtEnd: function() {
                var valueLength, selectionStart, range;
                valueLength = this.$input.val().length;
                selectionStart = this.$input[0].selectionStart;
                if (_.isNumber(selectionStart)) {
                    return selectionStart === valueLength;
                } else if (document.selection) {
                    range = document.selection.createRange();
                    range.moveStart("character", -valueLength);
                    return valueLength === range.text.length;
                }
                return true;
            },
            destroy: function destroy() {
                this.$hint.off(".tt");
                this.$input.off(".tt");
                this.$overflowHelper.remove();
                this.$hint = this.$input = this.$overflowHelper = $("<div>");
            }
        });
        return Input;
        function buildOverflowHelper($input) {
            return $('<pre aria-hidden="true"></pre>').css({
                position: "absolute",
                visibility: "hidden",
                whiteSpace: "pre",
                fontFamily: $input.css("font-family"),
                fontSize: $input.css("font-size"),
                fontStyle: $input.css("font-style"),
                fontVariant: $input.css("font-variant"),
                fontWeight: $input.css("font-weight"),
                wordSpacing: $input.css("word-spacing"),
                letterSpacing: $input.css("letter-spacing"),
                textIndent: $input.css("text-indent"),
                textRendering: $input.css("text-rendering"),
                textTransform: $input.css("text-transform")
            }).insertAfter($input);
        }
        function areQueriesEquivalent(a, b) {
            return Input.normalizeQuery(a) === Input.normalizeQuery(b);
        }
        function withModifier($e) {
            return $e.altKey || $e.ctrlKey || $e.metaKey || $e.shiftKey;
        }
    }();
    var Dataset = function() {
        "use strict";
        var keys, nameGenerator;
        keys = {
            val: "tt-selectable-display",
            obj: "tt-selectable-object"
        };
        nameGenerator = _.getIdGenerator();
        function Dataset(o, www) {
            o = o || {};
            o.templates = o.templates || {};
            o.templates.notFound = o.templates.notFound || o.templates.empty;
            if (!o.source) {
                $.error("missing source");
            }
            if (!o.node) {
                $.error("missing node");
            }
            if (o.name && !isValidName(o.name)) {
                $.error("invalid dataset name: " + o.name);
            }
            www.mixin(this);
            this.highlight = !!o.highlight;
            this.name = o.name || nameGenerator();
            this.limit = o.limit || 5;
            this.displayFn = getDisplayFn(o.display || o.displayKey);
            this.templates = getTemplates(o.templates, this.displayFn);
            this.source = o.source.__ttAdapter ? o.source.__ttAdapter() : o.source;
            this.async = _.isUndefined(o.async) ? this.source.length > 2 : !!o.async;
            this._resetLastSuggestion();
            this.$el = $(o.node).addClass(this.classes.dataset).addClass(this.classes.dataset + "-" + this.name);
        }
        Dataset.extractData = function extractData(el) {
            var $el = $(el);
            if ($el.data(keys.obj)) {
                return {
                    val: $el.data(keys.val) || "",
                    obj: $el.data(keys.obj) || null
                };
            }
            return null;
        };
        _.mixin(Dataset.prototype, EventEmitter, {
            _overwrite: function overwrite(query, suggestions) {
                suggestions = suggestions || [];
                if (suggestions.length) {
                    this._renderSuggestions(query, suggestions);
                } else if (this.async && this.templates.pending) {
                    this._renderPending(query);
                } else if (!this.async && this.templates.notFound) {
                    this._renderNotFound(query);
                } else {
                    this._empty();
                }
                this.trigger("rendered", this.name, suggestions, false);
            },
            _append: function append(query, suggestions) {
                suggestions = suggestions || [];
                if (suggestions.length && this.$lastSuggestion.length) {
                    this._appendSuggestions(query, suggestions);
                } else if (suggestions.length) {
                    this._renderSuggestions(query, suggestions);
                } else if (!this.$lastSuggestion.length && this.templates.notFound) {
                    this._renderNotFound(query);
                }
                this.trigger("rendered", this.name, suggestions, true);
            },
            _renderSuggestions: function renderSuggestions(query, suggestions) {
                var $fragment;
                $fragment = this._getSuggestionsFragment(query, suggestions);
                this.$lastSuggestion = $fragment.children().last();
                this.$el.html($fragment).prepend(this._getHeader(query, suggestions)).append(this._getFooter(query, suggestions));
            },
            _appendSuggestions: function appendSuggestions(query, suggestions) {
                var $fragment, $lastSuggestion;
                $fragment = this._getSuggestionsFragment(query, suggestions);
                $lastSuggestion = $fragment.children().last();
                this.$lastSuggestion.after($fragment);
                this.$lastSuggestion = $lastSuggestion;
            },
            _renderPending: function renderPending(query) {
                var template = this.templates.pending;
                this._resetLastSuggestion();
                template && this.$el.html(template({
                    query: query,
                    dataset: this.name
                }));
            },
            _renderNotFound: function renderNotFound(query) {
                var template = this.templates.notFound;
                this._resetLastSuggestion();
                template && this.$el.html(template({
                    query: query,
                    dataset: this.name
                }));
            },
            _empty: function empty() {
                this.$el.empty();
                this._resetLastSuggestion();
            },
            _getSuggestionsFragment: function getSuggestionsFragment(query, suggestions) {
                var that = this, fragment;
                fragment = document.createDocumentFragment();
                _.each(suggestions, function getSuggestionNode(suggestion) {
                    var $el, context;
                    context = that._injectQuery(query, suggestion);
                    $el = $(that.templates.suggestion(context)).data(keys.obj, suggestion).data(keys.val, that.displayFn(suggestion)).addClass(that.classes.suggestion + " " + that.classes.selectable);
                    fragment.appendChild($el[0]);
                });
                this.highlight && highlight({
                    className: this.classes.highlight,
                    node: fragment,
                    pattern: query
                });
                return $(fragment);
            },
            _getFooter: function getFooter(query, suggestions) {
                return this.templates.footer ? this.templates.footer({
                    query: query,
                    suggestions: suggestions,
                    dataset: this.name
                }) : null;
            },
            _getHeader: function getHeader(query, suggestions) {
                return this.templates.header ? this.templates.header({
                    query: query,
                    suggestions: suggestions,
                    dataset: this.name
                }) : null;
            },
            _resetLastSuggestion: function resetLastSuggestion() {
                this.$lastSuggestion = $();
            },
            _injectQuery: function injectQuery(query, obj) {
                return _.isObject(obj) ? _.mixin({
                    _query: query
                }, obj) : obj;
            },
            update: function update(query) {
                var that = this, canceled = false, syncCalled = false, rendered = 0;
                this.cancel();
                this.cancel = function cancel() {
                    canceled = true;
                    that.cancel = $.noop;
                    that.async && that.trigger("asyncCanceled", query);
                };
                this.source(query, sync, async);
                !syncCalled && sync([]);
                function sync(suggestions) {
                    if (syncCalled) {
                        return;
                    }
                    syncCalled = true;
                    suggestions = (suggestions || []).slice(0, that.limit);
                    rendered = suggestions.length;
                    that._overwrite(query, suggestions);
                    if (rendered < that.limit && that.async) {
                        that.trigger("asyncRequested", query);
                    }
                }
                function async(suggestions) {
                    suggestions = suggestions || [];
                    if (!canceled && rendered < that.limit) {
                        that.cancel = $.noop;
                        that._append(query, suggestions.slice(0, that.limit - rendered));
                        rendered += suggestions.length;
                        that.async && that.trigger("asyncReceived", query);
                    }
                }
            },
            cancel: $.noop,
            clear: function clear() {
                this._empty();
                this.cancel();
                this.trigger("cleared");
            },
            isEmpty: function isEmpty() {
                return this.$el.is(":empty");
            },
            destroy: function destroy() {
                this.$el = $("<div>");
            }
        });
        return Dataset;
        function getDisplayFn(display) {
            display = display || _.stringify;
            return _.isFunction(display) ? display : displayFn;
            function displayFn(obj) {
                return obj[display];
            }
        }
        function getTemplates(templates, displayFn) {
            return {
                notFound: templates.notFound && _.templatify(templates.notFound),
                pending: templates.pending && _.templatify(templates.pending),
                header: templates.header && _.templatify(templates.header),
                footer: templates.footer && _.templatify(templates.footer),
                suggestion: templates.suggestion || suggestionTemplate
            };
            function suggestionTemplate(context) {
                return $("<div>").text(displayFn(context));
            }
        }
        function isValidName(str) {
            return /^[_a-zA-Z0-9-]+$/.test(str);
        }
    }();
    var Menu = function() {
        "use strict";
        function Menu(o, www) {
            var that = this;
            o = o || {};
            if (!o.node) {
                $.error("node is required");
            }
            www.mixin(this);
            this.$node = $(o.node);
            this.query = null;
            this.datasets = _.map(o.datasets, initializeDataset);
            function initializeDataset(oDataset) {
                var node = that.$node.find(oDataset.node).first();
                oDataset.node = node.length ? node : $("<div>").appendTo(that.$node);
                return new Dataset(oDataset, www);
            }
        }
        _.mixin(Menu.prototype, EventEmitter, {
            _onSelectableClick: function onSelectableClick($e) {
                this.trigger("selectableClicked", $($e.currentTarget));
            },
            _onRendered: function onRendered(type, dataset, suggestions, async) {
                this.$node.toggleClass(this.classes.empty, this._allDatasetsEmpty());
                this.trigger("datasetRendered", dataset, suggestions, async);
            },
            _onCleared: function onCleared() {
                this.$node.toggleClass(this.classes.empty, this._allDatasetsEmpty());
                this.trigger("datasetCleared");
            },
            _propagate: function propagate() {
                this.trigger.apply(this, arguments);
            },
            _allDatasetsEmpty: function allDatasetsEmpty() {
                return _.every(this.datasets, isDatasetEmpty);
                function isDatasetEmpty(dataset) {
                    return dataset.isEmpty();
                }
            },
            _getSelectables: function getSelectables() {
                return this.$node.find(this.selectors.selectable);
            },
            _removeCursor: function _removeCursor() {
                var $selectable = this.getActiveSelectable();
                $selectable && $selectable.removeClass(this.classes.cursor);
            },
            _ensureVisible: function ensureVisible($el) {
                var elTop, elBottom, nodeScrollTop, nodeHeight;
                elTop = $el.position().top;
                elBottom = elTop + $el.outerHeight(true);
                nodeScrollTop = this.$node.scrollTop();
                nodeHeight = this.$node.height() + parseInt(this.$node.css("paddingTop"), 10) + parseInt(this.$node.css("paddingBottom"), 10);
                if (elTop < 0) {
                    this.$node.scrollTop(nodeScrollTop + elTop);
                } else if (nodeHeight < elBottom) {
                    this.$node.scrollTop(nodeScrollTop + (elBottom - nodeHeight));
                }
            },
            bind: function() {
                var that = this, onSelectableClick;
                onSelectableClick = _.bind(this._onSelectableClick, this);
                this.$node.on("click.tt", this.selectors.selectable, onSelectableClick);
                _.each(this.datasets, function(dataset) {
                    dataset.onSync("asyncRequested", that._propagate, that).onSync("asyncCanceled", that._propagate, that).onSync("asyncReceived", that._propagate, that).onSync("rendered", that._onRendered, that).onSync("cleared", that._onCleared, that);
                });
                return this;
            },
            isOpen: function isOpen() {
                return this.$node.hasClass(this.classes.open);
            },
            open: function open() {
                this.$node.addClass(this.classes.open);
            },
            close: function close() {
                this.$node.removeClass(this.classes.open);
                this._removeCursor();
            },
            setLanguageDirection: function setLanguageDirection(dir) {
                this.$node.attr("dir", dir);
            },
            selectableRelativeToCursor: function selectableRelativeToCursor(delta) {
                var $selectables, $oldCursor, oldIndex, newIndex;
                $oldCursor = this.getActiveSelectable();
                $selectables = this._getSelectables();
                oldIndex = $oldCursor ? $selectables.index($oldCursor) : -1;
                newIndex = oldIndex + delta;
                newIndex = (newIndex + 1) % ($selectables.length + 1) - 1;
                newIndex = newIndex < -1 ? $selectables.length - 1 : newIndex;
                return newIndex === -1 ? null : $selectables.eq(newIndex);
            },
            setCursor: function setCursor($selectable) {
                this._removeCursor();
                if ($selectable = $selectable && $selectable.first()) {
                    $selectable.addClass(this.classes.cursor);
                    this._ensureVisible($selectable);
                }
            },
            getSelectableData: function getSelectableData($el) {
                return $el && $el.length ? Dataset.extractData($el) : null;
            },
            getActiveSelectable: function getActiveSelectable() {
                var $selectable = this._getSelectables().filter(this.selectors.cursor).first();
                return $selectable.length ? $selectable : null;
            },
            getTopSelectable: function getTopSelectable() {
                var $selectable = this._getSelectables().first();
                return $selectable.length ? $selectable : null;
            },
            update: function update(query) {
                var isValidUpdate = query !== this.query;
                if (isValidUpdate) {
                    this.query = query;
                    _.each(this.datasets, updateDataset);
                }
                return isValidUpdate;
                function updateDataset(dataset) {
                    dataset.update(query);
                }
            },
            empty: function empty() {
                _.each(this.datasets, clearDataset);
                this.query = null;
                this.$node.addClass(this.classes.empty);
                function clearDataset(dataset) {
                    dataset.clear();
                }
            },
            destroy: function destroy() {
                this.$node.off(".tt");
                this.$node = $("<div>");
                _.each(this.datasets, destroyDataset);
                function destroyDataset(dataset) {
                    dataset.destroy();
                }
            }
        });
        return Menu;
    }();
    var DefaultMenu = function() {
        "use strict";
        var s = Menu.prototype;
        function DefaultMenu() {
            Menu.apply(this, [].slice.call(arguments, 0));
        }
        _.mixin(DefaultMenu.prototype, Menu.prototype, {
            open: function open() {
                !this._allDatasetsEmpty() && this._show();
                return s.open.apply(this, [].slice.call(arguments, 0));
            },
            close: function close() {
                this._hide();
                return s.close.apply(this, [].slice.call(arguments, 0));
            },
            _onRendered: function onRendered() {
                if (this._allDatasetsEmpty()) {
                    this._hide();
                } else {
                    this.isOpen() && this._show();
                }
                return s._onRendered.apply(this, [].slice.call(arguments, 0));
            },
            _onCleared: function onCleared() {
                if (this._allDatasetsEmpty()) {
                    this._hide();
                } else {
                    this.isOpen() && this._show();
                }
                return s._onCleared.apply(this, [].slice.call(arguments, 0));
            },
            setLanguageDirection: function setLanguageDirection(dir) {
                this.$node.css(dir === "ltr" ? this.css.ltr : this.css.rtl);
                return s.setLanguageDirection.apply(this, [].slice.call(arguments, 0));
            },
            _hide: function hide() {
                this.$node.hide();
            },
            _show: function show() {
                this.$node.css("display", "block");
            }
        });
        return DefaultMenu;
    }();
    var Typeahead = function() {
        "use strict";
        function Typeahead(o, www) {
            var onFocused, onBlurred, onEnterKeyed, onTabKeyed, onEscKeyed, onUpKeyed, onDownKeyed, onLeftKeyed, onRightKeyed, onQueryChanged, onWhitespaceChanged;
            o = o || {};
            if (!o.input) {
                $.error("missing input");
            }
            if (!o.menu) {
                $.error("missing menu");
            }
            if (!o.eventBus) {
                $.error("missing event bus");
            }
            www.mixin(this);
            this.eventBus = o.eventBus;
            this.minLength = _.isNumber(o.minLength) ? o.minLength : 1;
            this.input = o.input;
            this.menu = o.menu;
            this.enabled = true;
            this.active = false;
            this.input.hasFocus() && this.activate();
            this.dir = this.input.getLangDir();
            this._hacks();
            this.menu.bind().onSync("selectableClicked", this._onSelectableClicked, this).onSync("asyncRequested", this._onAsyncRequested, this).onSync("asyncCanceled", this._onAsyncCanceled, this).onSync("asyncReceived", this._onAsyncReceived, this).onSync("datasetRendered", this._onDatasetRendered, this).onSync("datasetCleared", this._onDatasetCleared, this);
            onFocused = c(this, "activate", "open", "_onFocused");
            onBlurred = c(this, "deactivate", "_onBlurred");
            onEnterKeyed = c(this, "isActive", "isOpen", "_onEnterKeyed");
            onTabKeyed = c(this, "isActive", "isOpen", "_onTabKeyed");
            onEscKeyed = c(this, "isActive", "_onEscKeyed");
            onUpKeyed = c(this, "isActive", "open", "_onUpKeyed");
            onDownKeyed = c(this, "isActive", "open", "_onDownKeyed");
            onLeftKeyed = c(this, "isActive", "isOpen", "_onLeftKeyed");
            onRightKeyed = c(this, "isActive", "isOpen", "_onRightKeyed");
            onQueryChanged = c(this, "_openIfActive", "_onQueryChanged");
            onWhitespaceChanged = c(this, "_openIfActive", "_onWhitespaceChanged");
            this.input.bind().onSync("focused", onFocused, this).onSync("blurred", onBlurred, this).onSync("enterKeyed", onEnterKeyed, this).onSync("tabKeyed", onTabKeyed, this).onSync("escKeyed", onEscKeyed, this).onSync("upKeyed", onUpKeyed, this).onSync("downKeyed", onDownKeyed, this).onSync("leftKeyed", onLeftKeyed, this).onSync("rightKeyed", onRightKeyed, this).onSync("queryChanged", onQueryChanged, this).onSync("whitespaceChanged", onWhitespaceChanged, this).onSync("langDirChanged", this._onLangDirChanged, this);
        }
        _.mixin(Typeahead.prototype, {
            _hacks: function hacks() {
                var $input, $menu;
                $input = this.input.$input || $("<div>");
                $menu = this.menu.$node || $("<div>");
                $input.on("blur.tt", function($e) {
                    var active, isActive, hasActive;
                    active = document.activeElement;
                    isActive = $menu.is(active);
                    hasActive = $menu.has(active).length > 0;
                    if (_.isMsie() && (isActive || hasActive)) {
                        $e.preventDefault();
                        $e.stopImmediatePropagation();
                        _.defer(function() {
                            $input.focus();
                        });
                    }
                });
                $menu.on("mousedown.tt", function($e) {
                    $e.preventDefault();
                });
            },
            _onSelectableClicked: function onSelectableClicked(type, $el) {
                this.select($el);
            },
            _onDatasetCleared: function onDatasetCleared() {
                this._updateHint();
            },
            _onDatasetRendered: function onDatasetRendered(type, dataset, suggestions, async) {
                this._updateHint();
                this.eventBus.trigger("render", suggestions, async, dataset);
            },
            _onAsyncRequested: function onAsyncRequested(type, dataset, query) {
                this.eventBus.trigger("asyncrequest", query, dataset);
            },
            _onAsyncCanceled: function onAsyncCanceled(type, dataset, query) {
                this.eventBus.trigger("asynccancel", query, dataset);
            },
            _onAsyncReceived: function onAsyncReceived(type, dataset, query) {
                this.eventBus.trigger("asyncreceive", query, dataset);
            },
            _onFocused: function onFocused() {
                this._minLengthMet() && this.menu.update(this.input.getQuery());
            },
            _onBlurred: function onBlurred() {
                if (this.input.hasQueryChangedSinceLastFocus()) {
                    this.eventBus.trigger("change", this.input.getQuery());
                }
            },
            _onEnterKeyed: function onEnterKeyed(type, $e) {
                var $selectable;
                if ($selectable = this.menu.getActiveSelectable()) {
                    this.select($selectable) && $e.preventDefault();
                }
            },
            _onTabKeyed: function onTabKeyed(type, $e) {
                var $selectable;
                if ($selectable = this.menu.getActiveSelectable()) {
                    this.select($selectable) && $e.preventDefault();
                } else if (this.autoselect) {
                    if ($selectable = this.menu.getTopSelectable()) {
                        this.autocomplete($selectable) && $e.preventDefault();
                    }
                }
            },
            _onEscKeyed: function onEscKeyed() {
                this.close();
            },
            _onUpKeyed: function onUpKeyed() {
                this.moveCursor(-1);
            },
            _onDownKeyed: function onDownKeyed() {
                this.moveCursor(+1);
            },
            _onLeftKeyed: function onLeftKeyed() {
                if (this.dir === "rtl" && this.input.isCursorAtEnd()) {
                    this.autocomplete(this.menu.getTopSelectable());
                }
            },
            _onRightKeyed: function onRightKeyed() {
                if (this.dir === "ltr" && this.input.isCursorAtEnd()) {
                    this.autocomplete(this.menu.getTopSelectable());
                }
            },
            _onQueryChanged: function onQueryChanged(e, query) {
                this._minLengthMet(query) ? this.menu.update(query) : this.menu.empty();
            },
            _onWhitespaceChanged: function onWhitespaceChanged() {
                this._updateHint();
            },
            _onLangDirChanged: function onLangDirChanged(e, dir) {
                if (this.dir !== dir) {
                    this.dir = dir;
                    this.menu.setLanguageDirection(dir);
                }
            },
            _openIfActive: function openIfActive() {
                this.isActive() && this.open();
            },
            _minLengthMet: function minLengthMet(query) {
                query = _.isString(query) ? query : this.input.getQuery() || "";
                return query.length >= this.minLength;
            },
            _updateHint: function updateHint() {
                var $selectable, data, val, query, escapedQuery, frontMatchRegEx, match;
                $selectable = this.menu.getTopSelectable();
                data = this.menu.getSelectableData($selectable);
                val = this.input.getInputValue();
                if (data && !_.isBlankString(val) && !this.input.hasOverflow()) {
                    query = Input.normalizeQuery(val);
                    escapedQuery = _.escapeRegExChars(query);
                    frontMatchRegEx = new RegExp("^(?:" + escapedQuery + ")(.+$)", "i");
                    match = frontMatchRegEx.exec(data.val);
                    match && this.input.setHint(val + match[1]);
                } else {
                    this.input.clearHint();
                }
            },
            isEnabled: function isEnabled() {
                return this.enabled;
            },
            enable: function enable() {
                this.enabled = true;
            },
            disable: function disable() {
                this.enabled = false;
            },
            isActive: function isActive() {
                return this.active;
            },
            activate: function activate() {
                if (this.isActive()) {
                    return true;
                } else if (!this.isEnabled() || this.eventBus.before("active")) {
                    return false;
                } else {
                    this.active = true;
                    this.eventBus.trigger("active");
                    return true;
                }
            },
            deactivate: function deactivate() {
                if (!this.isActive()) {
                    return true;
                } else if (this.eventBus.before("idle")) {
                    return false;
                } else {
                    this.active = false;
                    this.close();
                    this.eventBus.trigger("idle");
                    return true;
                }
            },
            isOpen: function isOpen() {
                return this.menu.isOpen();
            },
            open: function open() {
                if (!this.isOpen() && !this.eventBus.before("open")) {
                    this.menu.open();
                    this._updateHint();
                    this.eventBus.trigger("open");
                }
                return this.isOpen();
            },
            close: function close() {
                if (this.isOpen() && !this.eventBus.before("close")) {
                    this.menu.close();
                    this.input.clearHint();
                    this.input.resetInputValue();
                    this.eventBus.trigger("close");
                }
                return !this.isOpen();
            },
            setVal: function setVal(val) {
                this.input.setQuery(_.toStr(val));
            },
            getVal: function getVal() {
                return this.input.getQuery();
            },
            select: function select($selectable) {
                var data = this.menu.getSelectableData($selectable);
                if (data && !this.eventBus.before("select", data.obj)) {
                    this.input.setQuery(data.val, true);
                    this.eventBus.trigger("select", data.obj);
                    this.close();
                    return true;
                }
                return false;
            },
            autocomplete: function autocomplete($selectable) {
                var query, data, isValid;
                query = this.input.getQuery();
                data = this.menu.getSelectableData($selectable);
                isValid = data && query !== data.val;
                if (isValid && !this.eventBus.before("autocomplete", data.obj)) {
                    this.input.setQuery(data.val);
                    this.eventBus.trigger("autocomplete", data.obj);
                    return true;
                }
                return false;
            },
            moveCursor: function moveCursor(delta) {
                var query, $candidate, data, payload, cancelMove;
                query = this.input.getQuery();
                $candidate = this.menu.selectableRelativeToCursor(delta);
                data = this.menu.getSelectableData($candidate);
                payload = data ? data.obj : null;
                cancelMove = this._minLengthMet() && this.menu.update(query);
                if (!cancelMove && !this.eventBus.before("cursorchange", payload)) {
                    this.menu.setCursor($candidate);
                    if (data) {
                        this.input.setInputValue(data.val);
                    } else {
                        this.input.resetInputValue();
                        this._updateHint();
                    }
                    this.eventBus.trigger("cursorchange", payload);
                    return true;
                }
                return false;
            },
            destroy: function destroy() {
                this.input.destroy();
                this.menu.destroy();
            }
        });
        return Typeahead;
        function c(ctx) {
            var methods = [].slice.call(arguments, 1);
            return function() {
                var args = [].slice.call(arguments);
                _.each(methods, function(method) {
                    return ctx[method].apply(ctx, args);
                });
            };
        }
    }();
    (function() {
        "use strict";
        var old, keys, methods;
        old = $.fn.typeahead;
        keys = {
            www: "tt-www",
            attrs: "tt-attrs",
            typeahead: "tt-typeahead"
        };
        methods = {
            initialize: function initialize(o, datasets) {
                var www;
                datasets = _.isArray(datasets) ? datasets : [].slice.call(arguments, 1);
                o = o || {};
                www = WWW(o.classNames);
                return this.each(attach);
                function attach() {
                    var $input, $wrapper, $hint, $menu, defaultHint, defaultMenu, eventBus, input, menu, typeahead, MenuConstructor;
                    _.each(datasets, function(d) {
                        d.highlight = !!o.highlight;
                    });
                    $input = $(this);
                    $wrapper = $(www.html.wrapper);
                    $hint = $elOrNull(o.hint);
                    $menu = $elOrNull(o.menu);
                    defaultHint = o.hint !== false && !$hint;
                    defaultMenu = o.menu !== false && !$menu;
                    defaultHint && ($hint = buildHintFromInput($input, www));
                    defaultMenu && ($menu = $(www.html.menu).css(www.css.menu));
                    $hint && $hint.val("");
                    $input = prepInput($input, www);
                    if (defaultHint || defaultMenu) {
                        $wrapper.css(www.css.wrapper);
                        $input.css(defaultHint ? www.css.input : www.css.inputWithNoHint);
                        $input.wrap($wrapper).parent().prepend(defaultHint ? $hint : null).append(defaultMenu ? $menu : null);
                    }
                    MenuConstructor = defaultMenu ? DefaultMenu : Menu;
                    eventBus = new EventBus({
                        el: $input
                    });
                    input = new Input({
                        hint: $hint,
                        input: $input
                    }, www);
                    menu = new MenuConstructor({
                        node: $menu,
                        datasets: datasets
                    }, www);
                    typeahead = new Typeahead({
                        input: input,
                        menu: menu,
                        eventBus: eventBus,
                        minLength: o.minLength
                    }, www);
                    $input.data(keys.www, www);
                    $input.data(keys.typeahead, typeahead);
                }
            },
            isEnabled: function isEnabled() {
                var enabled;
                ttEach(this.first(), function(t) {
                    enabled = t.isEnabled();
                });
                return enabled;
            },
            enable: function enable() {
                ttEach(this, function(t) {
                    t.enable();
                });
                return this;
            },
            disable: function disable() {
                ttEach(this, function(t) {
                    t.disable();
                });
                return this;
            },
            isActive: function isActive() {
                var active;
                ttEach(this.first(), function(t) {
                    active = t.isActive();
                });
                return active;
            },
            activate: function activate() {
                ttEach(this, function(t) {
                    t.activate();
                });
                return this;
            },
            deactivate: function deactivate() {
                ttEach(this, function(t) {
                    t.deactivate();
                });
                return this;
            },
            isOpen: function isOpen() {
                var open;
                ttEach(this.first(), function(t) {
                    open = t.isOpen();
                });
                return open;
            },
            open: function open() {
                ttEach(this, function(t) {
                    t.open();
                });
                return this;
            },
            close: function close() {
                ttEach(this, function(t) {
                    t.close();
                });
                return this;
            },
            select: function select(el) {
                var success = false, $el = $(el);
                ttEach(this.first(), function(t) {
                    success = t.select($el);
                });
                return success;
            },
            autocomplete: function autocomplete(el) {
                var success = false, $el = $(el);
                ttEach(this.first(), function(t) {
                    success = t.autocomplete($el);
                });
                return success;
            },
            moveCursor: function moveCursoe(delta) {
                var success = false;
                ttEach(this.first(), function(t) {
                    success = t.moveCursor(delta);
                });
                return success;
            },
            val: function val(newVal) {
                var query;
                if (!arguments.length) {
                    ttEach(this.first(), function(t) {
                        query = t.getVal();
                    });
                    return query;
                } else {
                    ttEach(this, function(t) {
                        t.setVal(newVal);
                    });
                    return this;
                }
            },
            destroy: function destroy() {
                ttEach(this, function(typeahead, $input) {
                    revert($input);
                    typeahead.destroy();
                });
                return this;
            }
        };
        $.fn.typeahead = function(method) {
            if (methods[method]) {
                return methods[method].apply(this, [].slice.call(arguments, 1));
            } else {
                return methods.initialize.apply(this, arguments);
            }
        };
        $.fn.typeahead.noConflict = function noConflict() {
            $.fn.typeahead = old;
            return this;
        };
        function ttEach($els, fn) {
            $els.each(function() {
                var $input = $(this), typeahead;
                (typeahead = $input.data(keys.typeahead)) && fn(typeahead, $input);
            });
        }
        function buildHintFromInput($input, www) {
            return $input.clone().addClass(www.classes.hint).removeData().css(www.css.hint).css(getBackgroundStyles($input)).prop("readonly", true).removeAttr("id name placeholder required").attr({
                autocomplete: "off",
                spellcheck: "false",
                tabindex: -1
            });
        }
        function prepInput($input, www) {
            $input.data(keys.attrs, {
                dir: $input.attr("dir"),
                autocomplete: $input.attr("autocomplete"),
                spellcheck: $input.attr("spellcheck"),
                style: $input.attr("style")
            });
            $input.addClass(www.classes.input).attr({
                autocomplete: "off",
                spellcheck: false
            });
            try {
                !$input.attr("dir") && $input.attr("dir", "auto");
            } catch (e) {}
            return $input;
        }
        function getBackgroundStyles($el) {
            return {
                backgroundAttachment: $el.css("background-attachment"),
                backgroundClip: $el.css("background-clip"),
                backgroundColor: $el.css("background-color"),
                backgroundImage: $el.css("background-image"),
                backgroundOrigin: $el.css("background-origin"),
                backgroundPosition: $el.css("background-position"),
                backgroundRepeat: $el.css("background-repeat"),
                backgroundSize: $el.css("background-size")
            };
        }
        function revert($input) {
            var www, $wrapper;
            www = $input.data(keys.www);
            $wrapper = $input.parent().filter(www.selectors.wrapper);
            _.each($input.data(keys.attrs), function(val, key) {
                _.isUndefined(val) ? $input.removeAttr(key) : $input.attr(key, val);
            });
            $input.removeData(keys.typeahead).removeData(keys.www).removeData(keys.attr).removeClass(www.classes.input);
            if ($wrapper.length) {
                $input.detach().insertAfter($wrapper);
                $wrapper.remove();
            }
        }
        function $elOrNull(obj) {
            var isValid, $el;
            isValid = _.isJQuery(obj) || _.isElement(obj);
            $el = isValid ? $(obj).first() : [];
            return $el.length ? $el : null;
        }
    })();
});
$(document).ready(function () {
  // context must be jQuery object
  function goToBrowseSearch(context) {
    var $this = context;
    var $context = $this.closest('[data-esearch-context]');
    var $inputEl = $context.find('.js-search-external-onEnter');
    var link =
      '/' +
      portalBase +
      '/browse.tt.html?type=' +
      $context.attr('data-esearch-context') +
      '&action=link';

    $inputEl.each(function () {
      var $el = $(this);
      // additional checkbox handling for Volltextsuche
      if ($el.attr('type') === 'checkbox' && $el.is(':checked') || $el.attr('type') != 'checkbox' && $el.val()) {
        // check if there is more than one WP selected - each value needs a key-value set
        if (Array.isArray($el.val())) {
          $el.val().forEach(wpSel => {
            link = link + '&' + $el.attr('name') + '=' + wpSel;
          })
        } else {
          link = link + '&' + $el.attr('name') + '=' + $el.val();
        }
      }
    });
    window.location.replace(link);
  }
	$('body').on('click', '.js-search-external-btn', function() {
		goToBrowseSearch($(this));
	})
	$('body').on('keypress', '.js-search-external-onEnter', function(e) {
		if (e.which == 13) {
      e.preventDefault()
      goToBrowseSearch($(this));
    }
	})
});
// plugin to automatically set correct sorting option for generic4 - speakers (LSA)

$(document).ready(() => {
	return
	if (typeof ESearch !== 'undefined') {
		ESearch.addEventHandler('reportLoaded.ViewportMain', setSortSpeaker, {})
	}
})

const setSortSpeaker = () => {
	if ($('#generic4Search-tab').hasClass('active')) {
		const fields = [
			$('#searchgeneric4-speaker'),
			$('#searchgeneric4-speakergroup'),
			$('#searchgeneric4-speakerfunction'),
		]

		const relevantValueChanges = !!fields.filter(
			(field) => field.val().length != 0 && field.val() != field.data('val')
		).length
		const relevantDisplayOption = !!$(
			'.multiselect-selected-text:contains(Reden Kurzanzeige)'
		).length
		const alreadySelected = !!$(
			'.multiselect-selected-text:contains(Gesuchte/r Redner*innen)'
		).length

		const sortDropdown = $('#efxDisplaySort.multiselect');
		const sortDropdownValues = [];
		$('#efxDisplaySort option').each(function () {
			sortDropdownValues.push($(this).val())
		});

		console.log(relevantDisplayOption + ' , ' + relevantValueChanges)

		if (relevantDisplayOption && relevantValueChanges) {
			// console.log('setRednerSort')
			setPreValues(fields)
			//! set x in eq(x) below to the position of the UI setting for display = Gesuchte/r Redner*innen
			sortDropdown.multiselect('select', sortDropdownValues[0]);
			sortDropdown.change();
		} else if (
			checkIfAllEmpty(fields) &&
			relevantDisplayOption &&
			alreadySelected
		) {
			// console.log('setStandardSort')
			setPreValues(fields)
			sortDropdown.multiselect('select', sortDropdownValues[1]);
			sortDropdown.change();
		}
		// console.log('doNothing')
	}
}

const setPreValues = (fieldArray) => {
	fieldArray.forEach((field) => {
		field.data('val', field.val())
		// console.log('field.data(val) after setting: ' + field.data('val'))
	})
}

const checkIfAllEmpty = (fieldArray) =>
	!fieldArray.filter((field) => field.val().length != 0).length

function initTypeahead(inputField) {
	const searchId = inputField.attr('id')
	const lookupField = searchId.split('-')[0] + '-wp' || ''
	const lookupValue = $('#' + lookupField).val() || ''
	inputField.typeahead(
		{
			hint: true,
			highlight: true,
			minLength: 0,
			autoselect: false,
		},
		{
			displayKey: searchId,
			limit: Infinity,
			source: function (query, sync, async) {
				$.getJSON(
					'/portal/components/dataentry/autocomplete.tt.html?list=' +
						searchId.replace('-', '.') +
						'&lookupField=' +
						lookupField +
						'&lookupValue=' +
						lookupValue +
						'&search=' +
						query,
					function (data) {
						console.log(data.resh.Records.length);
						data = data.resh.Records.map(function (item) {
							item[searchId] = item.value[searchId]
							return item
						})
						async(data)
					}
				)
			},
		}
	)
	// console.log("searchId: " + searchId + " || lookupField: " + lookupField + " || lookupValue: " + lookupValue)
}

$(document).ready(function () {
	// init typeahead
	$('.typeahead').each(function () {
		initTypeahead($(this));
	})
	// WP change event handler
	$('.multiselect').each(function () {
		$(this).change(function () {
			const id = $(this).attr('id').split('-')[0].substring(6)
			$('[class*=tab-pane][id*=' + id + ']').each(function () {
				if ($(this).hasClass('active')) {
					$(this)
						.find('.typeahead')
						.each(function () {
							if ($(this).attr('id')) {
								$(this).typeahead('destroy')
								initTypeahead($(this))
							}
						})
				}
			})
		})
	})
	// fix picklist overwrite on autocomplete-field
	$('.typeahead').on('change', function (e) {
		if ($(this).val() !== $(this).typeahead('val')) {
			$(this).typeahead('val', $(this).val())
		}
	});
	// fix for direct selection via mouseclick and therefor not triggering a change event manually.
	$('.typeahead').bind('typeahead:select', function (ev, suggestion) {
		$(this).typeahead('val', suggestion.value[$(this).attr('id')])
		$(this).change()
	});
})

$(function () {
  $('body').on('click', '.js-openWindow', function (e) {
    var $this = $(this);
    var link = $this.attr('data-link');
    window.open(link, "_blank", "width=1300, height=990, left=500, top=5, resizable=yes, scrollbars=yes");
  });
});

// facet usability via keyboard
$(document).keydown(function (e) {
	if ($(':focus').hasClass('facet-collapse')) {
		const facetHead = $(':focus');
		const facetPanel = $(':focus').parents('.facetpanel');
		const facetItemFirst = facetPanel.find('.efxFacetItem:eq(0)');
		const facetItemSelected = facetPanel.find('.facetItemSelected');
		const facetItemCountVisible =
			facetPanel.find('.efxFacetItem:visible').length - 1;
		const facetItemCountTotal = facetPanel.find('.efxFacetItem').length - 1;
		let i = facetItemSelected.index() || facetItemFirst.index();
		$('.facetItemSelected').each(function () {
			if (
				$(this).parents('facet-collapse').attr('id') != facetHead.attr('id')
			) {
				$(this).removeClass('facetItemSelected');
			}
		});
		switch (e.which) {
			case 40: // down key
				e.preventDefault();
				if (facetHead.attr('aria-expanded') === 'false') {
					facetHead.click();
					facetItemFirst.addClass('facetItemSelected');
				} else {
					if (
						i === facetItemCountVisible &&
						facetItemCountVisible < facetItemCountTotal
					) {
						facetPanel.find('.more_facets_link').click();
					}
					facetItemSelected.removeClass('facetItemSelected');
					facetPanel
						.find(
							`.efxFacetItem:eq(${i < facetItemCountTotal ? ++i : facetItemCountTotal
							})`
						)
						.addClass('facetItemSelected');
				}
				// console.log('i: ' + i);
				break;
			case 38: // up key
				e.preventDefault();
				if (facetHead.attr('aria-expanded') === 'true' && i == 0) {
					facetHead.click();
					facetItemFirst.removeClass('facetItemSelected');
					return false;
				}
				if (facetHead.attr('aria-expanded') === 'true') {
					facetItemSelected.removeClass('facetItemSelected');
					facetPanel
						.find(`.efxFacetItem:eq(${i > 0 ? --i : 0})`)
						.addClass('facetItemSelected');
				}
				// console.log('i: ' + i);
				break;
			case 32: // space key
				if (facetItemSelected.length > 0) {
					facetHead.blur();
					facetItemSelected.click();
				} else {
					facetHead.click();
				}
				return false;
				break;
			default:
				break;
		}
	}
});
$(document).ready(() => {
  const idExtLink = 'extlinks';

  const sendLogRequest = (type, values) => {
    const data = JSON.stringify({ type, values });
    $.ajax({
      type: 'POST',
      url: "/statistic/create/",
      headers: { "Content-Type": "application/json" },
      data: data
    });
  };

  $(`.${idExtLink}`).on('click auxclick', function () {
    const type = idExtLink;
    const url = new URL(this.href.replace(/^www./i, ''));

    if (url && url.host) {
      const name = this.innerText.trim().replaceAll(/\s+/g, ' ');
      const domain = url.host;
      const link = url.href;
      const params = url.search;
      const path = url.pathname;
      
      const values = { name, domain, link, params, path };
      sendLogRequest(type, values);
    }
  });
});
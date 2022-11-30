var TableAdvanced = function () {

    var initTable1 = function (table_name, url, swf_path) {
        var $table = $('#' + table_name);

        function fnFilterGlobal() {
            $table.dataTable().fnFilter(
                $("#global-filter").val(),
                null,
                false,
                false
            );
        }

        function fnFilterColumn(i) {
            console.log("filter-"+i+$("#filter-" + i).val());

            $table.dataTable().fnFilter(
                $("#filter-" + i).val(),
                i,
                false,
                false
            );
        }

        function fnFilterDateColumn(column, start, end) {
            var start_date = $("#filter-" + start).val();
            if (start_date == "") {
                start_date = "0";
            }
            var end_date = $("#filter-" + end).val();
            if (end_date == "") {
                end_date = "0";
            }
            $table.dataTable().fnFilter(
                start_date + "+" + end_date,
                column,
                false,
                false
            );
        }

        function fnSelectionFilterColumn(i) {
            console.log($('#filter-' + i).find('option:selected').val());
            $table.dataTable().fnFilter(
                $('#filter-' + i).find('option:selected').val(),
                i,
                false,
                false
            );
        }

        function fnFilterCorporateColumn(i) {
            console.log($("#corporate-filter-" + i).val());
            $table.dataTable().fnFilter(
                "corporate;" + $("#corporate-filter-" + i).val(),
                i,
                false,
                false
            );
        }


        function fnFilterDateCorporateColumn(column, start, end) {
            var start_date = $("#corporate-filter-" + start).val();
            if (start_date == "") {
                start_date = "0";
            }
            var end_date = $("#corporate-filter-" + end).val();
            if (end_date == "") {
                end_date = "0";
            }
            $table.dataTable().fnFilter(
                "corporate;" + start_date + "+" + end_date,
                column,
                false,
                false
            );
        }

        function fnSelectionFilterCorporateColumn(i) {
            console.log($('#corporate-filter-' + i).find('option:selected').val());
            $table.dataTable().fnFilter(
                "corporate;" + $('#corporate-filter-' + i).find('option:selected').val(),
                i,
                false,
                false
            );
        }

        function fnFilterCustomColumn(i) {
            console.log($("#custom-filter-" + i).val());
            $table.dataTable().fnFilter(
                "custom;" + $("#custom-filter-" + i).val(),
                i,
                false,
                false
            );
        }


        function fnFilterDateCustomColumn(column, start, end) {
            var start_date = $("#custom-filter-" + start).val();
            if (start_date == "") {
                start_date = "0";
            }
            var end_date = $("#custom-filter-" + end).val();
            if (end_date == "") {
                end_date = "0";
            }
            $table.dataTable().fnFilter(
                start_date + "+" + end_date,
                column,
                false,
                false
            );
        }

        function fnSelectionFilterCustomColumn(i) {
            $table.dataTable().fnFilter(
                "custom;" + $("#custom-filter-" + i).find('option:selected').val(),
                i,
                false,
                false
            );
        }

        function createFilter(i) {
            return function () {
                fnFilterColumn(i);
            };
        }

        function createDateFilter(column, start, end) {
            return function () {
                fnFilterDateColumn(column, start, end);
            };
        }

        function createSelectionFilter(i) {
            return function () {
                fnSelectionFilterColumn(i);
            };
        }



        function createAnalystFilters(){
             fnFilterCustomColumn(0);
             fnFilterCustomColumn(1);
             fnSelectionFilterCustomColumn(2);
             fnSelectionFilterCustomColumn(3);
             fnSelectionFilterCustomColumn(4);
             fnSelectionFilterCustomColumn(5);
        }

        function createReviewerFilters(){
            fnFilterCustomColumn(0);
            fnFilterCustomColumn(1);
            fnSelectionFilterCustomColumn(2);
            fnSelectionFilterCustomColumn(3);
            fnSelectionFilterCustomColumn(4);
       }


        function createAllFilters() {
            fnFilterColumn(0);
            fnFilterColumn(1);
            fnFilterColumn(2);
            fnSelectionFilterColumn(3);
            fnSelectionFilterColumn(4);
            fnSelectionFilterColumn(5);
            fnSelectionFilterColumn(6);
            fnFilterDateColumn(7, 7, 8);
            fnFilterDateColumn(7, 7, 8);
        }

        function createAllSupervisorFilters() {
            fnFilterColumn(0);
            fnFilterColumn(1);
            fnFilterColumn(2);
            fnSelectionFilterColumn(3);
            fnFilterColumn(4);
            fnSelectionFilterColumn(6);
            fnFilterDateColumn(7, 7, 8);
            fnFilterDateColumn(7, 7, 8);
        }

        function createAllCorporateFilters() {
            fnFilterCorporateColumn(0);
            fnFilterCorporateColumn(1);
            fnSelectionFilterCorporateColumn(2);
            fnSelectionFilterCorporateColumn(3);
            fnSelectionFilterCorporateColumn(4);
            fnSelectionFilterCorporateColumn(5);
            fnFilterDateCorporateColumn(7, 7, 8);
            fnFilterDateCorporateColumn(7, 7, 8);
        }

        function createAllCorporateSupervisorFilters() {
            fnFilterCorporateColumn(0);
            fnFilterCorporateColumn(1);
            fnFilterCorporateColumn(2);
            fnSelectionFilterCorporateColumn(3);
            fnSelectionFilterCorporateColumn(4);
            fnFilterDateCorporateColumn(5, 5, 6);
            fnFilterDateCorporateColumn(5, 5, 6);
        }

        function createAllCustomFilters() {
            fnFilterCustomColumn(0);
            fnSelectionFilterCustomColumn(1);
            fnSelectionFilterCustomColumn(2);
            fnFilterCustomColumn(3);
            fnSelectionFilterCustomColumn(4);
            fnSelectionFilterCustomColumn(5);
            fnFilterDateCustomColumn(6,6,7);
            fnSelectionFilterCustomColumn(8);
            fnFilterCustomColumn(9);
            fnSelectionFilterCustomColumn(10);
            fnSelectionFilterCustomColumn(11);


        }

        function createAllCustomSupervisorFilters() {
            fnFilterCustomColumn(0);
            fnFilterCustomColumn(1);
            fnFilterCustomColumn(2);
            fnSelectionFilterCustomColumn(3);
            fnSelectionFilterCustomColumn(4);
            //fnFilterDateColumn(5, 5, 6);
            fnFilterDateCustomColumn(5,5,6);
            fnSelectionFilterCustomColumn(7);
            fnFilterCustomColumn(8);
            fnFilterCustomColumn(9);
            fnFilterCustomColumn(10);
        }

        function createAllArchiveReportFilters() {
            fnFilterColumn(0);
            fnFilterColumn(1);
            fnSelectionFilterColumn(2);
            fnFilterColumn(3);
            fnFilterDateColumn(4, 4, 5);
            fnFilterDateColumn(4, 4, 5);
        }


        /* Set tabletools buttons and button container */

        $.extend(true, $.fn.DataTable.TableTools.classes, {
            "container": "btn-group tabletools-dropdown-on-portlet",
            "buttons": {
                "normal": "btn btn-sm default",
                "disabled": "btn btn-sm default disabled"
            },
            "collection": {
                "container": "DTTT_dropdown dropdown-menu tabletools-dropdown-menu"
            }
        });

        var oTable = $table.dataTable({
            "bPaginate": true,
            "bProcessing": true,
            "bServerSide": true,
            "sAjaxSource": url,

            "aLengthMenu": [
                [5, 15, 20, 100, 1000],
                [5, 15, 20, 100, 1000] // change per page values here
            ],
            // set the initial value
            "iDisplayLength": 5,
            "sDom": "<'row' <'col-md-12'T>><'row'<'col-md-6 col-sm-12'l>r><'table-scrollable't><'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>", // horizobtal scrollable datatable

            "oTableTools": {
                "sSwfPath": swf_path,
                "aButtons": [
                    ]
            }
        });



        $("#analyst-advanced-filter-button").click(
            function () {
                createAnalystFilters();
            });

        $("#reviewer-advanced-filter-button").click(
            function () {
                createReviewerFilters();
        });



        $("#filter-button1").click(
            function () {
                createAllFilters();
            });

        $("#filter-button2").click(
            function () {
                createAllCorporateFilters();
            });

        $("#filter-button3").click(
            function () {
                createAllArchiveReportFilters();
            });

        $("#filter-button-custom").click(
            function () {
                createAllCustomFilters();
            });


        //Supervisor Filters
        $("#filter-supervisor-button1").click(
            function () {
                createAllSupervisorFilters()
            });

        $("#filter-supervisor-button2").click(
            function () {
                createAllCorporateSupervisorFilters()
            });

        $("#filter-supervisor-button-custom").click(
            function () {
                createAllCustomSupervisorFilters();
            });

        var tableWrapper = $('#datatable_wrapper'); // datatable creates the table wrapper by adding with id {your_table_jd}_wrapper

        jQuery('.dataTables_filter input', tableWrapper).addClass("form-control input-small input-inline"); // modify table search input
        jQuery('.dataTables_length select', tableWrapper).addClass("form-control input-small"); // modify table per page dropdown
        jQuery('.dataTables_length select', tableWrapper).select2(); // initialize select2 dropdown
    }

    return {

        //main function to initiate the module
        init: function (table_name, url, swf_path) {

            if (!jQuery().dataTable) {
                return;
            }

            initTable1(table_name, url, swf_path);
        }

    };

}();


var TableSelect = function () {

    var initTable = function (table_name, url, csrftoken) {
        var $table = $('#' + table_name);

        function fnFilterGlobal() {
            $table.dataTable().fnFilter(
                $("#global-filter").val(),
                null,
                false,
                false
            );
        }

        function fnFilterColumn(i) {
            console.log("filter-" + i + $("#filter-" + i).val());

            $table.dataTable().fnFilter(
                $("#filter-" + i).val(),
                i,
                false,
                false
            );
        }


        function fnFilterDateColumn(column, start, end) {
            var start_date = $("#filter-" + start).val();
            if (start_date == "") {
                start_date = "0";
            }
            var end_date = $("#filter-" + end).val();
            if (end_date == "") {
                end_date = "0";
            }
            $table.dataTable().fnFilter(
                start_date + "+" + end_date,
                column,
                false,
                false
            );
        }


        function fnFilterCustomColumn(i) {
            console.log($("#custom-filter-" + i).val());
            $table.dataTable().fnFilter(
                "custom;" + $("#custom-filter-" + i).val(),
                i,
                false,
                false
            );
        }


        function fnFilterDateCustomColumn(column, start, end) {
            var start_date = $("#custom-filter-" + start).val();
            if (start_date == "") {
                start_date = "0";
            }
            var end_date = $("#custom-filter-" + end).val();
            if (end_date == "") {
                end_date = "0";
            }
            $table.dataTable().fnFilter(
                start_date + "+" + end_date,
                column,
                false,
                false
            );
        }

        function fnSelectionFilterCustomColumn(i) {
            console.log($("#custom-filter-" + i).find('option:selected').val());
            $table.dataTable().fnFilter(
                "custom;" + $("#custom-filter-" + i).find('option:selected').val(),
                i,
                false,
                false
            );
        }


        function createAllCustomSupervisorFilters() {
            fnFilterCustomColumn(0);
            fnFilterCustomColumn(1);
            fnFilterCustomColumn(2);
            fnSelectionFilterCustomColumn(3);
            fnSelectionFilterCustomColumn(4);
            fnFilterDateCustomColumn(5, 5, 6);
            fnSelectionFilterCustomColumn(7);
            fnFilterCustomColumn(8);
            fnFilterCustomColumn(9);
            fnFilterCustomColumn(10);
        }


        function drawCallBack() {

            var requests = $("input[name^='request']");
            for (var i = 0; i < requests.length; i++) {
                for (var j = 0; j < checked_boxes.length; j++) {
                    if ($(requests[i]).val() == checked_boxes[j]) {
                        $(requests[i]).attr('checked', 'checked');
                    }
                }
            }

        }


        var oTable = $table.dataTable({
            "bPaginate": true,
            "bProcessing": true,
            "bServerSide": true,
            "sAjaxSource": url,
            "sDom": "<'row'><'row'<'col-md-6 col-sm-12'l>r><'table-scrollable't><'row'<'col-md-5 col-sm-12'i><'col-md-7 col-sm-12'p>>",
            "aLengthMenu": [
                [5, 15, 20, 100, 400],
                [5, 15, 20, 100, 400] // change per page values here
            ],
            // set the initial value
            "iDisplayLength": 5,
            "fnDrawCallback": function (oSettings) {
                drawCallBack(oSettings);
            }
        });

        $("#filter-supervisor-button-custom").click(
            function () {
                createAllCustomSupervisorFilters();
            });

        var tableWrapper = $('#datatable_wrapper'); // datatable creates the table wrapper by adding with id {your_table_jd}_wrapper

        jQuery('.dataTables_filter input', tableWrapper).addClass("form-control input-small input-inline"); // modify table search input
        jQuery('.dataTables_length select', tableWrapper).addClass("form-control input-small"); // modify table per page dropdown
        jQuery('.dataTables_length select', tableWrapper).select2(); // initialize select2 dropdown


        var checked_boxes = [];
        $("#all_table").delegate("tr", "click", function(e){
            // if you click a row it checks the box.
            if (event.target.type !== 'checkbox') {
                $(':checkbox', this).attr('checked', function(){
                    return !this.checked;
                });
            }
            var checkbox = $(':checkbox', this);
            if (checkbox.attr('checked')){
                //checking
                checked_boxes.push(checkbox.val());
                $("#selected_count").html(checked_boxes.length);
            }else{
                //unchecking
                var index = checked_boxes.indexOf(checkbox.val());
                if (index > -1) {
                    checked_boxes.splice(index, 1);
                    $("#selected_count").html(checked_boxes.length);
                }
            }
        });

    function getCookie(sKey) {
        if (!sKey) { return null; }
            return decodeURIComponent(document.cookie.replace(new RegExp("(?:(?:^|.*;)\\s*" + encodeURIComponent(sKey).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=\\s*([^;]*).*$)|^.*$"), "$1")) || null;
        }


        $("#download_button").click(function(e){
            var request_type = $('#custom-filter-10').val();



            if(checked_boxes.length > 0 && checked_boxes.length < 401) {
                $("#download_button").attr("disabled", "disabled");
                $.ajax({
                    type: "POST",
                    data: ({csrfmiddlewaretoken: getCookie("csrftoken"), "requests": JSON.stringify(checked_boxes), "request_type": request_type}),
                    success: function (data) {
                        location.href = "/supervisor_archives_view/";
                    }
                });
            }else if(checked_boxes.length > 400){
                alert("Select 400 or fewer requests");
            }else{
                alert("Select at least one request");
            }
            localStorage.setItem("ComplyVisited",true);
        });

        var all_checked = false;
        $("#check_all").click(function(e){
            checked_boxes = [];
            var checks = $("input[name=requests]");
            if(all_checked == false){
                for(var i=0; i<checks.length; i++){
                    $(checks[i]).attr('checked', 'checked');
                    checked_boxes.push($(checks[i]).val());
                }
                all_checked = true;

            }else{
                for(var i=0; i<checks.length; i++){
                    $(checks[i]).attr('checked', false);
                }


                all_checked = false;
                checked_boxes = [];
            }
            $("#selected_count").html(checked_boxes.length);
        });

    };


     return {

        //main function to initiate the module
        init: function (table_name, url) {

            if (!jQuery().dataTable) {
                return;
            }

            initTable(table_name, url);
        }

    };

}();
